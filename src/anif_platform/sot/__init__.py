"""Source-of-Truth adapter — Nautobot, NetBox, or InfraHub."""

import os

from anif_platform.exceptions import SoTAdapterError
from anif_platform.sot.protocol import SoTAdapter


def get_sot_adapter() -> SoTAdapter:
    """Return the configured SoT adapter based on SOT_BACKEND env var."""
    backend = os.environ.get("SOT_BACKEND", "nautobot").lower()

    if backend == "nautobot":
        from anif_platform.sot.nautobot import NautobotAdapter
        url = os.environ.get("NAUTOBOT_URL", "")
        token = os.environ.get("NAUTOBOT_TOKEN", "")
        if not url or not token:
            raise SoTAdapterError("NAUTOBOT_URL and NAUTOBOT_TOKEN must be set when SOT_BACKEND=nautobot")
        return NautobotAdapter(url=url, token=token)

    if backend == "netbox":
        from anif_platform.sot.netbox import NetBoxAdapter
        url = os.environ.get("NETBOX_URL", "")
        token = os.environ.get("NETBOX_TOKEN", "")
        if not url or not token:
            raise SoTAdapterError("NETBOX_URL and NETBOX_TOKEN must be set when SOT_BACKEND=netbox")
        return NetBoxAdapter(url=url, token=token)

    if backend == "infrahub":
        from anif_platform.sot.infrahub import InfraHubAdapter
        url = os.environ.get("INFRAHUB_URL", "")
        token = os.environ.get("INFRAHUB_TOKEN", "")
        if not url or not token:
            raise SoTAdapterError("INFRAHUB_URL and INFRAHUB_TOKEN must be set when SOT_BACKEND=infrahub")
        return InfraHubAdapter(url=url, token=token)

    raise SoTAdapterError(f"Unknown SOT_BACKEND: {backend!r} — must be nautobot | netbox | infrahub")
