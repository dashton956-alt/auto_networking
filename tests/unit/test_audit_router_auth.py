"""Audit endpoints must require API-key auth like every other router (ANIF-840s)."""

from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from anif_platform.audit.router import router as audit_router


@pytest.fixture()
def unauthed_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ANIF_API_KEY", "secret")
    app = FastAPI()
    app.include_router(audit_router)
    return TestClient(app)


@pytest.mark.parametrize(
    "path",
    [
        "/audit",
        f"/audit/{uuid.uuid4()}",
        f"/audit/{uuid.uuid4()}/why",
        f"/audit/{uuid.uuid4()}/verify",
    ],
)
def test_audit_endpoints_reject_missing_api_key(unauthed_client: TestClient, path: str) -> None:
    assert unauthed_client.get(path).status_code == 401


@pytest.mark.parametrize(
    "path",
    [
        "/audit",
        f"/audit/{uuid.uuid4()}",
    ],
)
def test_audit_endpoints_reject_wrong_api_key(unauthed_client: TestClient, path: str) -> None:
    assert unauthed_client.get(path, headers={"X-API-Key": "wrong"}).status_code == 401
