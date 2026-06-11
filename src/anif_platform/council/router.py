"""Council API router — ANIF-902/903/904/905."""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.auth import get_api_key
from anif_platform.council.schemas import (
    BuildTimeReviewRequest,
    CouncilDecision,
    ReviewCouncilRequest,
    ReviewDecision,
    RuntimeCouncilRequest,
)
from anif_platform.council.service import (
    BuildTimeCouncil,
    CouncilInputError,
    ReviewCouncil,
    RuntimeCouncil,
)

log = structlog.get_logger(__name__)
router = APIRouter(tags=["council"])


def get_db_session() -> AsyncSession:
    raise NotImplementedError("Override via dependency injection")


@router.post("/council/build-time", response_model=dict[str, Any])
async def open_build_time_session(
    request: BuildTimeReviewRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Open a Build-Time Council review session — ANIF-903."""
    try:
        svc = BuildTimeCouncil(session=session)
        return await svc.open_session(request)
    except CouncilInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.post("/council/build-time/{council_id}/decision", response_model=dict[str, Any])
async def record_build_time_decision(
    council_id: str,
    decision: CouncilDecision,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Record Build-Time Council decision — ANIF-903."""
    try:
        svc = BuildTimeCouncil(session=session)
        return await svc.record_decision(council_id=council_id, decision=decision)
    except CouncilInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.post("/council/runtime", response_model=dict[str, Any])
async def open_runtime_session(
    request: RuntimeCouncilRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Open a Runtime Council review session — ANIF-904."""
    svc = RuntimeCouncil(session=session)
    return await svc.open_session(request)


@router.post("/council/runtime/{council_id}/timeout", response_model=dict[str, Any])
async def apply_runtime_timeout(
    council_id: str,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Record HALTED_COUNCIL_TIMEOUT when deliberation time limit expires — CR-904-04."""
    try:
        svc = RuntimeCouncil(session=session)
        return await svc.apply_timeout(council_id=council_id)
    except CouncilInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.post("/council/review", response_model=dict[str, Any])
async def open_review_session(
    request: ReviewCouncilRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Open a Review Council session — ANIF-905."""
    svc = ReviewCouncil(session=session)
    return await svc.open_session(request)


@router.post("/council/review/{council_id}/decision", response_model=dict[str, Any])
async def record_review_decision(
    council_id: str,
    decision: ReviewDecision,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Record Review Council decision with all three mandatory outputs — CR-905-03."""
    try:
        svc = ReviewCouncil(session=session)
        return await svc.record_decision(council_id=council_id, decision=decision)
    except CouncilInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
