"""
Cross-request persistence regression tests.

Guards against the missing-commit failure mode where handlers returned
success but every row (tickets, audit records) was discarded when the
request session closed. Uses the real app dependency wiring — no
dependency overrides — so writes go through the production session
factories and must survive into subsequent requests.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

API_KEY = "integration-test-key"


@pytest_asyncio.fixture
async def real_client(
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[AsyncClient, None]:
    """Client against the real app wiring (production session factories)."""
    monkeypatch.setenv("ANIF_API_KEY", API_KEY)
    from anif_platform.database import engine
    from anif_platform.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    # The global engine pools connections bound to this test's event loop;
    # dispose so the next test (new loop) doesn't inherit dead connections.
    await engine.dispose()


async def _cleanup(intent_id: uuid.UUID) -> None:
    """Remove rows the test committed through the real factories."""
    from anif_platform.audit.models import AuditRecordRow
    from anif_platform.database import async_session_factory
    from anif_platform.execution.models import ExecutionRecordRow
    from anif_platform.human_loop.models import ApprovalTicketRow
    from anif_platform.intent.models import IntentRow

    async with async_session_factory() as session:
        await session.execute(
            delete(ApprovalTicketRow).where(ApprovalTicketRow.intent_id == intent_id)
        )
        await session.execute(delete(AuditRecordRow).where(AuditRecordRow.intent_id == intent_id))
        await session.execute(
            delete(ExecutionRecordRow).where(ExecutionRecordRow.intent_id == intent_id)
        )
        await session.execute(delete(IntentRow).where(IntentRow.intent_id == intent_id))
        await session.commit()


@pytest.mark.asyncio
async def test_ticket_and_audit_persist_across_requests(real_client: AsyncClient) -> None:
    """A governance check that escalates MUST leave a durable ticket and audit record."""
    intent_id = uuid.uuid4()
    headers = {"X-API-Key": API_KEY}

    try:
        check = await real_client.post(
            "/governance/check",
            headers=headers,
            json={
                "intent_id": str(intent_id),
                "operator_id": "integration-test",
                "operator_roles": ["automation_agent"],
                "action_type": "apply_qos",
                "environment": "staging",
                "risk_score": 74,
                "trust_score": 80,
                "policy_results": [],
                "trace_id": str(uuid.uuid4()),
            },
        )
        assert check.status_code == 200, check.text
        body = check.json()
        assert body["mode"] == "manual_review"
        ticket_id = body["ticket_id"]
        assert ticket_id

        # Separate request: the ticket MUST be visible in the pending queue.
        listing = await real_client.get("/governance/tickets", headers=headers)
        assert listing.status_code == 200
        ticket_ids = [t["ticket_id"] for t in listing.json()["tickets"]]
        assert ticket_id in ticket_ids, "ticket was not durably persisted (missing commit?)"

        # Separate request: the governance audit record MUST be durable (ANIF-107 §4.3).
        audit = await real_client.get(f"/audit/{intent_id}", headers=headers)
        assert audit.status_code == 200
        stages = [r["stage"] for r in audit.json()]
        assert "governance" in stages, "audit record was not durably persisted"

        # Approve in a separate request; the state change MUST be durable too.
        approve = await real_client.post(
            f"/governance/approve/{ticket_id}",
            headers={
                **headers,
                "X-Operator-Id": "senior-1",
                "X-Operator-Roles": "senior_engineer",
            },
            json={"approver_role": "senior_engineer", "notes": "integration test"},
        )
        assert approve.status_code == 200, approve.text
        assert approve.json()["status"] == "approved"

        # The approved ticket MUST leave the pending queue.
        after = await real_client.get("/governance/tickets", headers=headers)
        assert ticket_id not in [t["ticket_id"] for t in after.json()["tickets"]]
    finally:
        await _cleanup(intent_id)


@pytest.mark.asyncio
async def test_orchestrate_full_pipeline_completes_and_persists(
    real_client: AsyncClient,
) -> None:
    """
    A passing intent MUST run all six stages to pipeline_complete.

    Regression: the decision-stage audit record was written without a
    reasoning chain, so /orchestrate 500'd for any intent that passed risk
    (ANIF-107 §4.2.2 requires reasoning on decision/governance records).
    """
    headers = {"X-API-Key": API_KEY}
    intent_id: uuid.UUID | None = None

    try:
        resp = await real_client.post(
            "/orchestrate",
            headers=headers,
            json={
                "intent": {
                    "service": "persistence-test",
                    "environment": "staging",
                    "priority": "high",
                    "objectives": {"latency_ms": 50, "availability_percent": 99.9},
                    "constraints": {"region": "EU", "encryption": True},
                    "policies": ["zero_trust"],
                },
                "dry_run": False,
            },
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["status"] in ("pipeline_complete", "pending_approval"), body
        intent_id = uuid.UUID(body["intent_id"])

        # Decision-stage record MUST be durable and carry reasoning (§4.2.2).
        audit = await real_client.get(f"/audit/{intent_id}", headers=headers)
        assert audit.status_code == 200
        records = audit.json()
        decision_records = [r for r in records if r["stage"] == "decision"]
        assert decision_records, f"no decision record; stages: {[r['stage'] for r in records]}"
        assert decision_records[0]["reasoning_chain"], "decision record has no reasoning chain"

        # Hash chain over the full run MUST verify.
        verify = await real_client.get(f"/audit/{intent_id}/verify", headers=headers)
        assert verify.status_code == 200
        assert verify.json()["valid"] is True
    finally:
        if intent_id is not None:
            await _cleanup(intent_id)
