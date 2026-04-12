"""InfraHub Source-of-Truth adapter."""

from anif_platform.sot.protocol import Device, Prefix, Topology


class InfraHubAdapter:
    """Reads device/topology data from InfraHub via GraphQL."""

    def __init__(self, url: str, token: str) -> None:
        self._url = url.rstrip("/")
        self._token = token

    def get_device(self, name: str) -> Device:
        raise NotImplementedError("InfraHubAdapter.get_device — implement in B2")

    def list_devices(self, site: str | None = None) -> list[Device]:
        raise NotImplementedError("InfraHubAdapter.list_devices — implement in B2")

    def get_topology(self, site: str) -> Topology:
        raise NotImplementedError("InfraHubAdapter.get_topology — implement in B2")

    def get_prefix(self, prefix: str) -> Prefix:
        raise NotImplementedError("InfraHubAdapter.get_prefix — implement in B2")

    def tag_device(self, name: str, tag: str) -> None:
        raise NotImplementedError("InfraHubAdapter.tag_device — implement in B5")

    def tag_interface(self, device: str, interface: str, tag: str) -> None:
        raise NotImplementedError("InfraHubAdapter.tag_interface — implement in B5")

    def tag_connection(self, device_a: str, device_b: str, tag: str) -> None:
        raise NotImplementedError("InfraHubAdapter.tag_connection — implement in B5")

    def set_custom_field(self, object_type: str, name: str, field: str, value: str) -> None:
        raise NotImplementedError("InfraHubAdapter.set_custom_field — implement in B5")
