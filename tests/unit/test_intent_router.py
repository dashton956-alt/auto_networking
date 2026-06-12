"""Tests for GET /intent/intents — F2 Intent Dashboard list endpoint (ANIF-301)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from anif_platform.auth import get_api_key
from anif_platform.intent.router import get_intent_registry
from anif_platform.intent.router import router as intent_router
from anif_platform.intent.schemas import ValidatedIntent


def make_intent(service: str = "payments", change_number: int = 1) -> ValidatedIntent:
    return ValidatedIntent(
        intent_id=uuid.uuid4(),
        change_number=change_number,
        version="0.1.0",
        service=service,
        status="validated",
        git_ref=None,
        resolved_intent={"service": service},
        warnings=[],
        created_at=datetime.now(UTC),
    )


class FakeRegistry:
    def __init__(self, items: list[ValidatedIntent], total: int) -> None:
        self._items = items
        self._total = total
        self.calls: list[dict[str, Any]] = []

    async def list_intents(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
        service: str | None = None,
    ) -> tuple[list[ValidatedIntent], int]:
        self.calls.append({"limit": limit, "offset": offset, "status": status, "service": service})
        return self._items, self._total


@pytest.fixture()
def fake_registry() -> FakeRegistry:
    return FakeRegistry(items=[make_intent("payments", 2), make_intent("checkout", 1)], total=2)


@pytest.fixture()
def client(fake_registry: FakeRegistry) -> TestClient:
    app = FastAPI()
    app.include_router(intent_router)
    app.dependency_overrides[get_intent_registry] = lambda: fake_registry
    app.dependency_overrides[get_api_key] = lambda: "test-key"
    return TestClient(app)


class TestListIntentsEndpoint:
    def test_returns_items_and_total(self, client: TestClient) -> None:
        resp = client.get("/intent/intents")

        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 2
        assert body["limit"] == 20
        assert body["offset"] == 0
        assert len(body["items"]) == 2
        assert body["items"][0]["service"] == "payments"

    def test_forwards_query_params_to_registry(
        self, client: TestClient, fake_registry: FakeRegistry
    ) -> None:
        resp = client.get(
            "/intent/intents",
            params={"limit": 5, "offset": 10, "status": "validated", "service": "checkout"},
        )

        assert resp.status_code == 200
        assert fake_registry.calls == [
            {"limit": 5, "offset": 10, "status": "validated", "service": "checkout"}
        ]

    def test_rejects_limit_over_100(self, client: TestClient) -> None:
        resp = client.get("/intent/intents", params={"limit": 101})

        assert resp.status_code == 422

    def test_rejects_negative_offset(self, client: TestClient) -> None:
        resp = client.get("/intent/intents", params={"offset": -1})

        assert resp.status_code == 422

    def test_requires_api_key(
        self, fake_registry: FakeRegistry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ANIF_API_KEY", "secret")
        app = FastAPI()
        app.include_router(intent_router)
        app.dependency_overrides[get_intent_registry] = lambda: fake_registry
        unauthed = TestClient(app)

        assert unauthed.get("/intent/intents").status_code == 401
        assert unauthed.get("/intent/intents", headers={"X-API-Key": "wrong"}).status_code == 401
        assert unauthed.get("/intent/intents", headers={"X-API-Key": "secret"}).status_code == 200
