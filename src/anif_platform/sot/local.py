"""File-backed local Source-of-Truth adapter — ANIF-307.

Reads and writes a YAML inventory file. Intended for development and
simulation: the file IS the source of truth, so write-back operations
(tags, custom fields) persist to it. Production deployments use the
Nautobot/NetBox/InfraHub adapters instead.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from anif_platform.exceptions import SoTAdapterError
from anif_platform.sot.protocol import Device, Interface, Prefix, Topology


class LocalSoTAdapter:
    """SoT adapter backed by a local YAML inventory file."""

    def __init__(self, inventory_path: str | Path) -> None:
        self._path = Path(inventory_path)
        if not self._path.exists():
            raise SoTAdapterError(f"Local SoT inventory not found: {self._path}")
        raw = yaml.safe_load(self._path.read_text())
        if not isinstance(raw, dict) or "site" not in raw:
            raise SoTAdapterError(f"Invalid local SoT inventory (no site): {self._path}")
        self._data: dict[str, Any] = raw

    @property
    def default_site(self) -> str:
        return str(self._data["site"])

    # ── Reads ────────────────────────────────────────────────────────────

    def get_device(self, name: str) -> Device:
        return self._to_device(self._device_entry(name))

    def list_devices(self, site: str | None = None) -> list[Device]:
        if site is not None and site != self.default_site:
            return []
        return [self._to_device(entry) for entry in self._device_entries()]

    def list_interfaces(self, device: str) -> list[Interface]:
        entry = self._device_entry(device)
        return [
            Interface(
                name=str(iface["name"]),
                device=str(entry["name"]),
                ip_address=iface.get("ip_address"),
                tags=list(iface.get("tags", [])),
            )
            for iface in entry.get("interfaces", [])
        ]

    def get_topology(self, site: str) -> Topology:
        if site != self.default_site:
            raise SoTAdapterError(
                f"Unknown site: {site!r} (local inventory holds {self.default_site!r})"
            )
        connections = [(str(pair[0]), str(pair[1])) for pair in self._data.get("connections", [])]
        return Topology(site=site, devices=self.list_devices(), connections=connections)

    def get_prefix(self, prefix: str) -> Prefix:
        for entry in self._data.get("prefixes", []):
            if entry.get("prefix") == prefix:
                return Prefix(prefix=prefix, site=entry.get("site"), vrf=entry.get("vrf"))
        raise SoTAdapterError(f"Unknown prefix: {prefix}")

    # ── Write-back (tags + custom fields only — never config/topology) ──

    def tag_device(self, name: str, tag: str) -> None:
        entry = self._device_entry(name)
        tags = entry.setdefault("tags", [])
        if tag not in tags:
            tags.append(tag)
        self._save()

    def tag_interface(self, device: str, interface: str, tag: str) -> None:
        entry = self._device_entry(device)
        for iface in entry.get("interfaces", []):
            if iface.get("name") == interface:
                tags = iface.setdefault("tags", [])
                if tag not in tags:
                    tags.append(tag)
                self._save()
                return
        raise SoTAdapterError(f"Unknown interface: {device}/{interface}")

    def tag_connection(self, device_a: str, device_b: str, tag: str) -> None:
        for pair in self._data.get("connections", []):
            if {str(pair[0]), str(pair[1])} == {device_a, device_b}:
                # Connections are stored as 2-item lists; tags ride in a
                # parallel mapping keyed "a|b" to keep the pair shape intact.
                conn_tags = self._data.setdefault("connection_tags", {})
                key = f"{pair[0]}|{pair[1]}"
                tags = conn_tags.setdefault(key, [])
                if tag not in tags:
                    tags.append(tag)
                self._save()
                return
        raise SoTAdapterError(f"Unknown connection: {device_a} <-> {device_b}")

    def set_custom_field(self, object_type: str, name: str, field: str, value: str) -> None:
        if object_type != "device":
            raise SoTAdapterError(
                f"Local adapter supports custom fields on devices only, got {object_type!r}"
            )
        entry = self._device_entry(name)
        entry.setdefault("custom_fields", {})[field] = value
        self._save()

    # ── Internals ────────────────────────────────────────────────────────

    def _device_entries(self) -> list[dict[str, Any]]:
        return list(self._data.get("devices", []))

    def _device_entry(self, name: str) -> dict[str, Any]:
        for entry in self._device_entries():
            if entry.get("name") == name:
                return entry
        raise SoTAdapterError(f"Unknown device: {name}")

    def _to_device(self, entry: dict[str, Any]) -> Device:
        return Device(
            name=str(entry["name"]),
            site=self.default_site,
            role=str(entry.get("role", "unknown")),
            platform=str(entry.get("platform", "unknown")),
            primary_ip=entry.get("primary_ip"),
            tags=list(entry.get("tags", [])),
            custom_fields=dict(entry.get("custom_fields", {})),
        )

    def _save(self) -> None:
        self._path.write_text(yaml.safe_dump(self._data, sort_keys=False))
