"""Tests for IntentRegistry.list_intents — F2 Intent Dashboard list view (ANIF-301)."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.intent.models import IntentRow
from anif_platform.intent.registry import IntentRegistry
from anif_platform.intent.schemas import ValidationResult


def make_result(service: str = "payments") -> ValidationResult:
    return ValidationResult(
        intent_id=uuid.uuid4(),
        status="validated",
        validated_intent={
            "service": service,
            "environment": "dev",
            "priority": "medium",
            "objectives": {"latency_ms": 50.0},
            "constraints": {"region": "EU"},
            "policies": [],
        },
        warnings=[],
    )


@pytest.mark.asyncio
class TestIntentRegistryList:
    async def test_list_empty_returns_empty_and_zero_total(self, db_session: AsyncSession) -> None:
        registry = IntentRegistry(db_session)

        items, total = await registry.list_intents()

        assert items == []
        assert total == 0

    async def test_list_returns_newest_first(self, db_session: AsyncSession) -> None:
        registry = IntentRegistry(db_session)
        first = await registry.register(make_result("svc-a"))
        second = await registry.register(make_result("svc-b"))
        third = await registry.register(make_result("svc-c"))

        items, total = await registry.list_intents()

        assert total == 3
        assert [i.intent_id for i in items] == [
            third.intent_id,
            second.intent_id,
            first.intent_id,
        ]

    async def test_list_pagination_limit_and_offset(self, db_session: AsyncSession) -> None:
        registry = IntentRegistry(db_session)
        for _ in range(3):
            await registry.register(make_result())

        page_one, total = await registry.list_intents(limit=2, offset=0)
        page_two, _ = await registry.list_intents(limit=2, offset=2)

        assert total == 3
        assert len(page_one) == 2
        assert len(page_two) == 1
        ids = {i.intent_id for i in page_one} | {i.intent_id for i in page_two}
        assert len(ids) == 3

    async def test_list_filters_by_service(self, db_session: AsyncSession) -> None:
        registry = IntentRegistry(db_session)
        await registry.register(make_result("payments"))
        await registry.register(make_result("checkout"))

        items, total = await registry.list_intents(service="payments")

        assert total == 1
        assert len(items) == 1
        assert items[0].service == "payments"

    async def test_list_filters_by_status(self, db_session: AsyncSession) -> None:
        registry = IntentRegistry(db_session)
        kept = await registry.register(make_result())
        changed = await registry.register(make_result())
        await db_session.execute(
            update(IntentRow)
            .where(IntentRow.intent_id == changed.intent_id)
            .values(status="executed")
        )

        items, total = await registry.list_intents(status="validated")

        assert total == 1
        assert items[0].intent_id == kept.intent_id

    async def test_list_total_ignores_pagination(self, db_session: AsyncSession) -> None:
        registry = IntentRegistry(db_session)
        for _ in range(3):
            await registry.register(make_result())

        items, total = await registry.list_intents(limit=1, offset=0)

        assert len(items) == 1
        assert total == 3
