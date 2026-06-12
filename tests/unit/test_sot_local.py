"""Tests for the file-backed local SoT adapter — ANIF-307 (F5 topology slice)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from anif_platform.exceptions import SoTAdapterError
from anif_platform.sot.local import LocalSoTAdapter

INVENTORY = {
    "site": "lab-1",
    "devices": [
        {
            "name": "spine-1",
            "role": "spine",
            "platform": "frr",
            "primary_ip": "10.0.0.1",
            "tags": ["intent:abc"],
            "custom_fields": {"intent_status": "success", "last_intent_id": "abc"},
            "interfaces": [
                {"name": "eth1", "ip_address": "10.1.0.1/30", "tags": []},
                {"name": "eth2", "ip_address": "10.1.0.5/30", "tags": []},
            ],
        },
        {
            "name": "leaf-1",
            "role": "leaf",
            "platform": "frr",
            "primary_ip": "10.0.0.11",
            "tags": [],
            "custom_fields": {},
            "interfaces": [{"name": "eth1", "ip_address": "10.1.0.2/30", "tags": []}],
        },
    ],
    "connections": [["spine-1", "leaf-1"]],
}


@pytest.fixture()
def inventory_path(tmp_path: Path) -> Path:
    path = tmp_path / "inventory.yml"
    path.write_text(yaml.safe_dump(INVENTORY))
    return path


@pytest.fixture()
def adapter(inventory_path: Path) -> LocalSoTAdapter:
    return LocalSoTAdapter(inventory_path)


class TestLocalSoTAdapterReads:
    def test_get_device_returns_fields(self, adapter: LocalSoTAdapter) -> None:
        device = adapter.get_device("spine-1")
        assert device.name == "spine-1"
        assert device.site == "lab-1"
        assert device.role == "spine"
        assert device.platform == "frr"
        assert device.primary_ip == "10.0.0.1"
        assert device.custom_fields["intent_status"] == "success"

    def test_get_device_unknown_raises(self, adapter: LocalSoTAdapter) -> None:
        with pytest.raises(SoTAdapterError):
            adapter.get_device("nope")

    def test_list_devices_returns_all(self, adapter: LocalSoTAdapter) -> None:
        devices = adapter.list_devices()
        assert [d.name for d in devices] == ["spine-1", "leaf-1"]

    def test_list_devices_filters_by_site(self, adapter: LocalSoTAdapter) -> None:
        assert adapter.list_devices(site="lab-1") != []
        assert adapter.list_devices(site="other") == []

    def test_get_topology_returns_devices_and_connections(self, adapter: LocalSoTAdapter) -> None:
        topology = adapter.get_topology("lab-1")
        assert topology.site == "lab-1"
        assert len(topology.devices) == 2
        assert topology.connections == [("spine-1", "leaf-1")]

    def test_get_topology_unknown_site_raises(self, adapter: LocalSoTAdapter) -> None:
        with pytest.raises(SoTAdapterError):
            adapter.get_topology("nowhere")

    def test_list_interfaces_returns_device_interfaces(self, adapter: LocalSoTAdapter) -> None:
        interfaces = adapter.list_interfaces("spine-1")
        assert [i.name for i in interfaces] == ["eth1", "eth2"]
        assert interfaces[0].device == "spine-1"
        assert interfaces[0].ip_address == "10.1.0.1/30"

    def test_list_interfaces_unknown_device_raises(self, adapter: LocalSoTAdapter) -> None:
        with pytest.raises(SoTAdapterError):
            adapter.list_interfaces("nope")


class TestLocalSoTAdapterWriteBack:
    def test_tag_device_persists_to_file(
        self, adapter: LocalSoTAdapter, inventory_path: Path
    ) -> None:
        adapter.tag_device("leaf-1", "intent:xyz")

        assert "intent:xyz" in adapter.get_device("leaf-1").tags
        reloaded = LocalSoTAdapter(inventory_path)
        assert "intent:xyz" in reloaded.get_device("leaf-1").tags

    def test_tag_device_is_idempotent(self, adapter: LocalSoTAdapter) -> None:
        adapter.tag_device("leaf-1", "intent:xyz")
        adapter.tag_device("leaf-1", "intent:xyz")
        assert adapter.get_device("leaf-1").tags.count("intent:xyz") == 1

    def test_tag_interface_persists(self, adapter: LocalSoTAdapter, inventory_path: Path) -> None:
        adapter.tag_interface("spine-1", "eth1", "intent:xyz")
        reloaded = LocalSoTAdapter(inventory_path)
        assert "intent:xyz" in reloaded.list_interfaces("spine-1")[0].tags

    def test_set_custom_field_on_device_persists(
        self, adapter: LocalSoTAdapter, inventory_path: Path
    ) -> None:
        adapter.set_custom_field("device", "leaf-1", "intent_status", "pending")
        reloaded = LocalSoTAdapter(inventory_path)
        assert reloaded.get_device("leaf-1").custom_fields["intent_status"] == "pending"

    def test_tag_connection_unknown_pair_raises(self, adapter: LocalSoTAdapter) -> None:
        with pytest.raises(SoTAdapterError):
            adapter.tag_connection("spine-1", "nope", "intent:xyz")
