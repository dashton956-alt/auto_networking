"""FastAPI router for topology reads — F5 Topology View (ANIF-307)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from anif_platform.auth import get_api_key
from anif_platform.exceptions import SoTAdapterError
from anif_platform.sot.protocol import SoTAdapter

router = APIRouter(tags=["topology"], dependencies=[Depends(get_api_key)])


def get_sot_adapter_dep() -> SoTAdapter:
    raise NotImplementedError("Provide SoTAdapter via dependency injection")


class InterfaceOut(BaseModel):
    name: str
    ip_address: str | None
    tags: list[str]


class DeviceOut(BaseModel):
    name: str
    role: str
    platform: str
    primary_ip: str | None
    tags: list[str]
    custom_fields: dict[str, str]
    interfaces: list[InterfaceOut]


class TopologyResponse(BaseModel):
    site: str
    devices: list[DeviceOut]
    connections: list[tuple[str, str]]


@router.get("/topology", response_model=TopologyResponse)
async def get_topology(
    site: str | None = Query(None),
    adapter: SoTAdapter = Depends(get_sot_adapter_dep),
) -> TopologyResponse:
    """
    Return the site topology with per-device interfaces and intent
    write-back metadata (custom_fields) for the F5 overlay.

    site defaults to the adapter's default site.
    """
    effective_site = site or getattr(adapter, "default_site", None)
    if not effective_site:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="site query parameter is required for this SoT backend",
        )

    try:
        topology = adapter.get_topology(effective_site)
        devices = [
            DeviceOut(
                name=device.name,
                role=device.role,
                platform=device.platform,
                primary_ip=device.primary_ip,
                tags=device.tags,
                custom_fields=device.custom_fields,
                interfaces=[
                    InterfaceOut(name=i.name, ip_address=i.ip_address, tags=i.tags)
                    for i in adapter.list_interfaces(device.name)
                ],
            )
            for device in topology.devices
        ]
    except SoTAdapterError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configured SoT backend does not support topology reads yet",
        ) from exc

    return TopologyResponse(site=topology.site, devices=devices, connections=topology.connections)
