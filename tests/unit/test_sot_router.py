"""Tests for GET /topology — F5 Topology View endpoint (ANIF-307)."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from anif_platform.auth import get_api_key
from anif_platform.exceptions import SoTAdapterError
from anif_platform.sot.protocol import Device, Interface, Topology
from anif_platform.sot.router import get_sot_adapter_dep
from anif_platform.sot.router import router as sot_router


class FakeAdapter:
    def __init__(self) -> None:
        self.default_site = "lab-1"
        self._devices = [
            Device(
                name="spine-1",
                site="lab-1",
                role="spine",
                platform="frr",
                primary_ip="10.0.0.1",
                tags=["intent:abc"],
                custom_fields={"intent_status": "success"},
            ),
            Device(
                name="leaf-1",
                site="lab-1",
                role="leaf",
                platform="frr",
                primary_ip=None,
                tags=[],
                custom_fields={},
            ),
        ]

    def get_topology(self, site: str) -> Topology:
        if site != "lab-1":
            raise SoTAdapterError(f"unknown site: {site}")
        return Topology(site=site, devices=self._devices, connections=[("spine-1", "leaf-1")])

    def list_interfaces(self, device: str) -> list[Interface]:
        if device == "spine-1":
            return [Interface(name="eth1", device="spine-1", ip_address="10.1.0.1/30", tags=[])]
        if device == "leaf-1":
            return []
        raise SoTAdapterError(f"unknown device: {device}")


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(sot_router)
    app.dependency_overrides[get_sot_adapter_dep] = lambda: FakeAdapter()
    app.dependency_overrides[get_api_key] = lambda: "test-key"
    return TestClient(app)


class TestTopologyEndpoint:
    def test_returns_devices_with_interfaces_and_connections(self, client: TestClient) -> None:
        resp = client.get("/topology")

        assert resp.status_code == 200
        body = resp.json()
        assert body["site"] == "lab-1"
        assert len(body["devices"]) == 2
        spine = body["devices"][0]
        assert spine["name"] == "spine-1"
        assert spine["custom_fields"]["intent_status"] == "success"
        assert spine["interfaces"][0]["name"] == "eth1"
        assert body["connections"] == [["spine-1", "leaf-1"]]

    def test_unknown_site_returns_404(self, client: TestClient) -> None:
        resp = client.get("/topology", params={"site": "nowhere"})
        assert resp.status_code == 404

    def test_requires_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANIF_API_KEY", "secret")
        app = FastAPI()
        app.include_router(sot_router)
        app.dependency_overrides[get_sot_adapter_dep] = lambda: FakeAdapter()
        unauthed = TestClient(app)

        assert unauthed.get("/topology").status_code == 401
        assert unauthed.get("/topology", headers={"X-API-Key": "secret"}).status_code == 200
