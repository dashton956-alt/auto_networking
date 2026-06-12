"""Tests for F6 dashboard read endpoints — council sessions, ethics strikes, /metrics."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.council.models import CouncilRecordRow
from anif_platform.ethics.models import StrikeRecordRow


@pytest.mark.asyncio
class TestCouncilSessionsEndpoint:
    async def test_lists_sessions_newest_first(self, client, db_session: AsyncSession) -> None:
        older = CouncilRecordRow(
            council_type="runtime",
            triggered_by="intent timeout",
            trigger_timestamp=datetime.now(UTC) - timedelta(hours=2),
            decision="approved",
            intent_id=str(uuid.uuid4()),
        )
        newer = CouncilRecordRow(
            council_type="review",
            triggered_by="post-incident review",
            trigger_timestamp=datetime.now(UTC),
            decision="completed",
            decision_rationale="No accountability breach found",
        )
        db_session.add_all([older, newer])
        await db_session.flush()

        resp = await client.get("/council/sessions")

        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 2
        ids = [s["council_id"] for s in body["sessions"]]
        assert ids.index(newer.council_id) < ids.index(older.council_id)
        first = body["sessions"][ids.index(newer.council_id)]
        assert first["council_type"] == "review"
        assert first["decision"] == "completed"
        assert first["decision_rationale"] == "No accountability breach found"

    async def test_limit_is_respected(self, client, db_session: AsyncSession) -> None:
        for i in range(3):
            db_session.add(
                CouncilRecordRow(
                    council_type="runtime",
                    triggered_by=f"t-{i}",
                    trigger_timestamp=datetime.now(UTC) - timedelta(minutes=i),
                    decision="pending",
                )
            )
        await db_session.flush()

        resp = await client.get("/council/sessions", params={"limit": 2})

        assert resp.status_code == 200
        assert len(resp.json()["sessions"]) == 2

    async def test_limit_over_100_rejected(self, client) -> None:
        resp = await client.get("/council/sessions", params={"limit": 500})
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestStrikesEndpoint:
    async def test_lists_strikes_newest_first(self, client, db_session: AsyncSession) -> None:
        agent_id = uuid.uuid4()
        older = StrikeRecordRow(
            agent_id=agent_id,
            intent_id=uuid.uuid4(),
            reason="rollback plan missing",
            recorded_at=datetime.now(UTC) - timedelta(hours=1),
        )
        newer = StrikeRecordRow(
            agent_id=agent_id,
            intent_id=uuid.uuid4(),
            reason="acted outside declared capabilities",
            recorded_at=datetime.now(UTC),
        )
        db_session.add_all([older, newer])
        await db_session.flush()

        resp = await client.get("/ethics/strikes")

        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 2
        ids = [s["strike_id"] for s in body["strikes"]]
        assert ids.index(str(newer.strike_id)) < ids.index(str(older.strike_id))
        first = body["strikes"][ids.index(str(newer.strike_id))]
        assert first["reason"] == "acted outside declared capabilities"
        assert first["agent_id"] == str(agent_id)

    async def test_limit_over_100_rejected(self, client) -> None:
        resp = await client.get("/ethics/strikes", params={"limit": 500})
        assert resp.status_code == 422


class TestMetricsEndpoint:
    def test_metrics_mounted_and_returns_prometheus_text(self) -> None:
        from anif_platform.main import app

        with TestClient(app) as tc:
            resp = tc.get("/metrics")

        assert resp.status_code == 200
        assert "anif_governance_auto_total" in resp.text
