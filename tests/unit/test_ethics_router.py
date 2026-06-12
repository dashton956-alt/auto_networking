"""Tests for the human override endpoint — ANIF-721 §6."""

from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from anif_platform.auth import get_api_key
from anif_platform.ethics.router import router as override_router

_OPERATOR_HEADERS = {"X-Operator-Id": "op-1"}


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(override_router)
    app.dependency_overrides[get_api_key] = lambda: "test-key"
    return TestClient(app)


def test_override_endpoint_exists(client: TestClient) -> None:
    """ANIF-721 §6.2: override endpoint MUST exist at /override."""
    intent_id = str(uuid.uuid4())
    resp = client.post(
        "/override",
        json={"intent_id": intent_id, "reason": "test"},
        headers=_OPERATOR_HEADERS,
    )
    assert resp.status_code in (200, 202)


def test_override_endpoint_returns_acknowledged(client: TestClient) -> None:
    """ANIF-721 §6.2: override MUST acknowledge receipt."""
    intent_id = str(uuid.uuid4())
    resp = client.post(
        "/override",
        json={"intent_id": intent_id, "reason": "test"},
        headers=_OPERATOR_HEADERS,
    )
    body = resp.json()
    assert body.get("status") == "acknowledged"
    assert body.get("intent_id") == intent_id


def test_override_requires_intent_id(client: TestClient) -> None:
    """ANIF-721 §6.2: override without intent_id MUST return 422."""
    resp = client.post("/override", json={"reason": "test"}, headers=_OPERATOR_HEADERS)
    assert resp.status_code == 422


def test_override_requires_reason(client: TestClient) -> None:
    """ANIF-721 §6.2: override without reason MUST return 422."""
    resp = client.post(
        "/override", json={"intent_id": str(uuid.uuid4())}, headers=_OPERATOR_HEADERS
    )
    assert resp.status_code == 422


def test_override_requires_operator_id_header(client: TestClient) -> None:
    """Override must be attributable: missing X-Operator-Id MUST return 422."""
    resp = client.post("/override", json={"intent_id": str(uuid.uuid4()), "reason": "test"})
    assert resp.status_code == 422


def test_override_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Override requires authentication like every other endpoint."""
    monkeypatch.setenv("ANIF_API_KEY", "secret")
    app = FastAPI()
    app.include_router(override_router)
    unauthed = TestClient(app)

    payload = {"intent_id": str(uuid.uuid4()), "reason": "test"}
    assert unauthed.post("/override", json=payload, headers=_OPERATOR_HEADERS).status_code == 401
    assert (
        unauthed.post(
            "/override",
            json=payload,
            headers={**_OPERATOR_HEADERS, "X-API-Key": "secret"},
        ).status_code
        == 200
    )
