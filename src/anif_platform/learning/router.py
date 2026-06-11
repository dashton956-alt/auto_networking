"""Learning Agent API router — ANIF-812."""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.auth import get_api_key
from anif_platform.learning.broker import KnowledgeBroker, KnowledgeBrokerError
from anif_platform.learning.schemas import KnowledgePackageInput

log = structlog.get_logger(__name__)
router = APIRouter(tags=["learning"])


def get_db_session() -> AsyncSession:
    raise NotImplementedError("Override via dependency injection")


@router.post("/learning/packages", response_model=dict[str, Any])
async def submit_knowledge_package(
    package: KnowledgePackageInput,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Submit a knowledge package for human approval — CR-812-01/02."""
    try:
        broker = KnowledgeBroker(session=session)
        return await broker.submit_package(package)
    except KnowledgeBrokerError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.post("/learning/packages/{package_id}/approve", response_model=dict[str, Any])
async def approve_package(
    package_id: str,
    approver_id: str,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Human approves a knowledge package — CR-812-01."""
    try:
        broker = KnowledgeBroker(session=session)
        return await broker.approve_package(package_id=package_id, approver_id=approver_id)
    except KnowledgeBrokerError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/learning/packages/{package_id}/reject", response_model=dict[str, Any])
async def reject_package(
    package_id: str,
    approver_id: str,
    reason: str,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Human rejects a knowledge package — CR-812-01."""
    try:
        broker = KnowledgeBroker(session=session)
        return await broker.reject_package(
            package_id=package_id, approver_id=approver_id, reason=reason
        )
    except KnowledgeBrokerError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
