"""Tests for the human override endpoint — ANIF-721 §6."""

from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from anif_platform.ethics.router import router as override_router


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(override_router)
    return TestClient(app)


def test_override_endpoint_exists(client: TestClient) -> None:
    """ANIF-721 §6.2: override endpoint MUST exist at /override."""
    intent_id = str(uuid.uuid4())
    resp = client.post("/override", json={"intent_id": intent_id, "reason": "test"})
    assert resp.status_code in (200, 202)


def test_override_endpoint_returns_acknowledged(client: TestClient) -> None:
    """ANIF-721 §6.2: override MUST acknowledge receipt."""
    intent_id = str(uuid.uuid4())
    resp = client.post("/override", json={"intent_id": intent_id, "reason": "test"})
    body = resp.json()
    assert body.get("status") == "acknowledged"
    assert body.get("intent_id") == intent_id


def test_override_requires_intent_id(client: TestClient) -> None:
    """ANIF-721 §6.2: override without intent_id MUST return 422."""
    resp = client.post("/override", json={"reason": "test"})
    assert resp.status_code == 422


def test_override_requires_reason(client: TestClient) -> None:
    """ANIF-721 §6.2: override without reason MUST return 422."""
    resp = client.post("/override", json={"intent_id": str(uuid.uuid4())})
    assert resp.status_code == 422
