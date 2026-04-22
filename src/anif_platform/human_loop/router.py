"""
Human-in-loop control endpoints — ANIF-404 §4.6.

POST /execution/{intent_id}/halt — emergency halt.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, status

from anif_platform.audit.writer import AuditWriter
from anif_platform.auth import get_api_key
from anif_platform.human_loop.schemas import HaltRequest, HaltResponse
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage

log = structlog.get_logger(__name__)
router = APIRouter(tags=["human-in-loop"])

_HALT_PERMITTED_ROLES = frozenset({"network_engineer", "senior_engineer"})


def get_audit_writer() -> AuditWriter:
    raise NotImplementedError("Override via dependency injection")


def _parse_roles(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [r.strip() for r in raw.split(",") if r.strip()]


@router.post("/execution/{intent_id}/halt", response_model=HaltResponse)
async def halt_execution(
    intent_id: uuid.UUID,
    body: HaltRequest,
    x_operator_roles: str | None = Header(None, alias="X-Operator-Roles"),
    writer: AuditWriter = Depends(get_audit_writer),
    _: str = Depends(get_api_key),
) -> HaltResponse:
    """
    Emergency halt of an in-progress execution — ANIF-404 §4.6.

    Requires network_engineer role. Audit written before returning.
    """
    roles = _parse_roles(x_operator_roles)
    if not set(roles).intersection(_HALT_PERMITTED_ROLES):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Emergency halt requires network_engineer role. Caller roles: {roles}",
        )

    if not body.reason or not body.reason.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A reason MUST be provided for emergency halt (ANIF-404 §4.6.2).",
        )

    now = datetime.now(UTC)

    audit_record = AuditRecord(
        intent_id=intent_id,
        stage=AuditStage.execute,
        operator_id=body.operator_id,
        input_summary={"action": "halt", "reason": body.reason},
        output_summary={"halt_status": "halted", "rollback_initiated": True},
        outcome=AuditOutcome.blocked,
        duration_ms=0,
    )
    await writer.write(audit_record)

    log.warning(
        "execution_halted_by_operator",
        intent_id=str(intent_id),
        operator_id=body.operator_id,
        reason=body.reason,
    )

    return HaltResponse(
        intent_id=intent_id,
        halt_status="halted",
        rollback_initiated=True,
        rollback_status="in_progress",
        audit_record_id=str(audit_record.record_id),
        halted_by=body.operator_id,
        halted_at=now,
    )
