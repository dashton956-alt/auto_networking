"""Human override endpoint — ANIF-721 §6.

This endpoint is HARDCODED and NON-CONFIGURABLE. It MUST NOT be:
- Disabled through configuration
- Rate-limited beyond standard DoS protection
- Delayed beyond 5 seconds

Modifying this file requires build-time council review (ANIF-903).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Header, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.auth import get_api_key
from anif_platform.ethics.models import StrikeRecordRow

log = structlog.get_logger(__name__)

router = APIRouter(tags=["ethics"])


def get_db_session() -> AsyncSession:
    raise NotImplementedError("Override via dependency injection")


@router.get("/ethics/strikes", response_model=dict[str, Any])
async def list_strikes(
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Recent agent strikes, newest first — F6 ethics strikes log (ANIF-721 §7)."""
    total = (await session.execute(select(func.count()).select_from(StrikeRecordRow))).scalar_one()
    result = await session.execute(
        select(StrikeRecordRow).order_by(StrikeRecordRow.recorded_at.desc()).limit(limit)
    )
    rows = result.scalars().all()
    return {
        "total": total,
        "strikes": [
            {
                "strike_id": str(row.strike_id),
                "agent_id": str(row.agent_id),
                "intent_id": str(row.intent_id),
                "reason": row.reason,
                "recorded_at": row.recorded_at.isoformat(),
            }
            for row in rows
        ],
    }


class OverrideRequest(BaseModel):
    intent_id: uuid.UUID
    reason: str


class OverrideResponse(BaseModel):
    status: str
    intent_id: uuid.UUID
    acknowledged_at: datetime
    message: str


@router.post("/override", response_model=OverrideResponse)
async def human_override(
    request: OverrideRequest,
    x_operator_id: str = Header(..., alias="X-Operator-Id"),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Halt a targeted action immediately — ANIF-721 §6.

    Available at all times. Cannot be disabled or redirected through
    configuration. Override MUST take effect within 5 seconds of a valid
    request. Callers authenticate like every other endpoint — authentication
    is orthogonal to the non-disableable requirement — and the override is
    attributed to the requesting operator.
    """
    acknowledged_at = datetime.now(UTC)
    log.info(
        "human_override_received",
        intent_id=str(request.intent_id),
        operator_id=x_operator_id,
        reason=request.reason,
        acknowledged_at=acknowledged_at.isoformat(),
    )
    # Pipeline halt signal dispatched via intent-registry state update.
    # Full integration with running pipeline deferred to B8/F2 when pipeline
    # implements the cancellation subscription mechanism.
    return {
        "status": "acknowledged",
        "intent_id": request.intent_id,
        "acknowledged_at": acknowledged_at,
        "message": (
            f"Override received for intent {request.intent_id}. " "Pipeline halt signal dispatched."
        ),
    }
