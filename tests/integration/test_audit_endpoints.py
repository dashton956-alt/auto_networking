"""Integration tests for GET /audit/* endpoints — ANIF-107 §4.5."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.audit.writer import AuditWriter
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage, ReasoningStep


def make_record(
    intent_id: uuid.UUID,
    stage: AuditStage = AuditStage.validate,
    outcome: AuditOutcome = AuditOutcome.success,
) -> AuditRecord:
    chain: list = []
    if stage in (AuditStage.decision, AuditStage.governance):
        chain = [ReasoningStep(step=1, description="Risk threshold evaluated", decision="warn")]
    return AuditRecord(
        intent_id=intent_id,
        stage=stage,
        input_summary={"service": "payments", "environment": "prod"},
        output_summary={"result": "pass"},
        outcome=outcome,
        duration_ms=15,
        reasoning_chain=chain,
    )


@pytest.mark.asyncio
class TestGetAuditByIntent:
    async def test_returns_empty_list_for_unknown_intent(self, client: AsyncClient) -> None:
        """ANIF-107 §4.5.3: empty array (not 404) for valid intent_id with no records."""
        unknown_id = uuid.uuid4()
        resp = await client.get(f"/audit/{unknown_id}")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_returns_records_for_known_intent(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        intent_id = uuid.uuid4()
        writer = AuditWriter(db_session)
        await writer.write(make_record(intent_id, AuditStage.validate))
        await writer.write(make_record(intent_id, AuditStage.policy))

        resp = await client.get(f"/audit/{intent_id}")
        assert resp.status_code == 200
        records = resp.json()
        assert len(records) == 2
        assert records[0]["stage"] == "validate"
        assert records[1]["stage"] == "policy"

    async def test_records_ordered_by_timestamp_ascending(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        intent_id = uuid.uuid4()
        writer = AuditWriter(db_session)
        await writer.write(make_record(intent_id, AuditStage.validate))
        await writer.write(make_record(intent_id, AuditStage.policy))
        await writer.write(make_record(intent_id, AuditStage.risk))

        resp = await client.get(f"/audit/{intent_id}")
        records = resp.json()
        stages = [r["stage"] for r in records]
        assert stages == ["validate", "policy", "risk"]

    async def test_returns_422_for_invalid_uuid(self, client: AsyncClient) -> None:
        """ANIF-107 §4.5.3: 404 only for syntactically invalid intent_id."""
        resp = await client.get("/audit/not-a-uuid")
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestGetAuditWhy:
    async def test_returns_string_explanation(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        intent_id = uuid.uuid4()
        writer = AuditWriter(db_session)
        await writer.write(make_record(intent_id, AuditStage.decision, AuditOutcome.escalated))

        resp = await client.get(f"/audit/{intent_id}/why")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, str)
        assert str(intent_id) in body

    async def test_returns_message_for_unknown_intent(self, client: AsyncClient) -> None:
        unknown_id = uuid.uuid4()
        resp = await client.get(f"/audit/{unknown_id}/why")
        assert resp.status_code == 200
        assert "No audit records" in resp.json()


@pytest.mark.asyncio
class TestVerifyHashChain:
    async def test_valid_chain_returns_true(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        intent_id = uuid.uuid4()
        writer = AuditWriter(db_session)
        await writer.write(make_record(intent_id, AuditStage.validate))
        await writer.write(make_record(intent_id, AuditStage.policy))

        resp = await client.get(f"/audit/{intent_id}/verify")
        assert resp.status_code == 200
        body = resp.json()
        assert body["valid"] is True
        assert body["broken_at"] is None
        assert body["record_count"] == 2

    async def test_empty_chain_returns_valid(self, client: AsyncClient) -> None:
        unknown_id = uuid.uuid4()
        resp = await client.get(f"/audit/{unknown_id}/verify")
        assert resp.status_code == 200
        assert resp.json()["valid"] is True


@pytest.mark.asyncio
class TestListAuditRecords:
    async def test_returns_records(self, client: AsyncClient, db_session: AsyncSession) -> None:
        intent_id = uuid.uuid4()
        writer = AuditWriter(db_session)
        await writer.write(make_record(intent_id, AuditStage.validate))

        resp = await client.get("/audit")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_filter_by_stage(self, client: AsyncClient, db_session: AsyncSession) -> None:
        intent_id = uuid.uuid4()
        writer = AuditWriter(db_session)
        await writer.write(make_record(intent_id, AuditStage.validate))
        await writer.write(make_record(intent_id, AuditStage.policy))

        resp = await client.get("/audit?stage=validate")
        assert resp.status_code == 200
        records = resp.json()
        assert all(r["stage"] == "validate" for r in records)

    async def test_default_limit_is_50(self, client: AsyncClient) -> None:
        resp = await client.get("/audit")
        assert resp.status_code == 200

    async def test_limit_above_1000_clamped(self, client: AsyncClient) -> None:
        """ANIF-107 §4.5.4: max page size MUST NOT exceed 1000."""
        resp = await client.get("/audit?limit=2000")
        assert resp.status_code == 422  # FastAPI validates le=1000
