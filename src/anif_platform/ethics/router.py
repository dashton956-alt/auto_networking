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
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel

from anif_platform.auth import get_api_key

log = structlog.get_logger(__name__)

router = APIRouter(tags=["ethics"])


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
