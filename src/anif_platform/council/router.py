"""Council API router — ANIF-902/903/904/905."""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.auth import get_api_key
from anif_platform.council.models import CouncilRecordRow
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


@router.get("/council/sessions", response_model=dict[str, Any])
async def list_council_sessions(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Recent council sessions, newest first — F6 council decision feed."""
    total = (await session.execute(select(func.count()).select_from(CouncilRecordRow))).scalar_one()
    result = await session.execute(
        select(CouncilRecordRow).order_by(CouncilRecordRow.trigger_timestamp.desc()).limit(limit)
    )
    rows = result.scalars().all()
    return {
        "total": total,
        "sessions": [
            {
                "council_id": row.council_id,
                "council_type": row.council_type,
                "decision": row.decision,
                "triggered_by": row.triggered_by,
                "trigger_timestamp": row.trigger_timestamp.isoformat(),
                "session_close_timestamp": (
                    row.session_close_timestamp.isoformat() if row.session_close_timestamp else None
                ),
                "decision_rationale": row.decision_rationale,
                "intent_id": row.intent_id,
            }
            for row in rows
        ],
    }


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
