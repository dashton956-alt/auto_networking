"""NetBox 3.x Source-of-Truth adapter."""

from anif_platform.sot.protocol import Device, Interface, Prefix, Topology


class NetBoxAdapter:
    """Reads device/topology data from NetBox via REST API."""

    def __init__(self, url: str, token: str) -> None:
        self._url = url.rstrip("/")
        self._token = token

    def get_device(self, name: str) -> Device:
        raise NotImplementedError("NetBoxAdapter.get_device — implement in B2")

    def list_devices(self, site: str | None = None) -> list[Device]:
        raise NotImplementedError("NetBoxAdapter.list_devices — implement in B2")

    def list_interfaces(self, device: str) -> list[Interface]:
        raise NotImplementedError("NetBoxAdapter.list_interfaces — implement with live backend")

    def get_topology(self, site: str) -> Topology:
        raise NotImplementedError("NetBoxAdapter.get_topology — implement in B2")

    def get_prefix(self, prefix: str) -> Prefix:
        raise NotImplementedError("NetBoxAdapter.get_prefix — implement in B2")

    def tag_device(self, name: str, tag: str) -> None:
        raise NotImplementedError("NetBoxAdapter.tag_device — implement in B5")

    def tag_interface(self, device: str, interface: str, tag: str) -> None:
        raise NotImplementedError("NetBoxAdapter.tag_interface — implement in B5")

    def tag_connection(self, device_a: str, device_b: str, tag: str) -> None:
        raise NotImplementedError("NetBoxAdapter.tag_connection — implement in B5")

    def set_custom_field(self, object_type: str, name: str, field: str, value: str) -> None:
        raise NotImplementedError("NetBoxAdapter.set_custom_field — implement in B5")
