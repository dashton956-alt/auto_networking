"""Source-of-Truth adapter protocol — defines the interface all SoT backends must implement."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class Device:
    name: str
    site: str
    role: str
    platform: str
    primary_ip: str | None
    tags: list[str]


@dataclass
class Interface:
    name: str
    device: str
    ip_address: str | None
    tags: list[str]


@dataclass
class Prefix:
    prefix: str
    site: str | None
    vrf: str | None


@dataclass
class Topology:
    site: str
    devices: list[Device]
    connections: list[tuple[str, str]]  # (device_a, device_b)


@runtime_checkable
class SoTAdapter(Protocol):
    """Protocol that all Source-of-Truth adapter implementations must satisfy."""

    def get_device(self, name: str) -> Device:
        """Fetch a single device record by name."""
        ...

    def list_devices(self, site: str | None = None) -> list[Device]:
        """List devices, optionally filtered by site."""
        ...

    def get_topology(self, site: str) -> Topology:
        """Fetch full site topology including devices and connections."""
        ...

    def get_prefix(self, prefix: str) -> Prefix:
        """Fetch an IP prefix record."""
        ...

    def tag_device(self, name: str, tag: str) -> None:
        """Add an intent tag to a device (e.g. 'intent:qos-prod-v2')."""
        ...

    def tag_interface(self, device: str, interface: str, tag: str) -> None:
        """Add an intent tag to a device interface."""
        ...

    def tag_connection(self, device_a: str, device_b: str, tag: str) -> None:
        """Add an intent tag to a connection between two devices."""
        ...

    def set_custom_field(self, object_type: str, name: str, field: str, value: str) -> None:
        """Set a custom field on a SoT object."""
        ...
