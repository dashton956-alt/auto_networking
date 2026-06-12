"""
Governance router — ANIF-406 §4.1.

POST /governance/check
POST /governance/approve/{ticket_id}
POST /governance/reject/{ticket_id}
GET  /governance/tickets
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select

from anif_platform.audit.writer import AuditWriter
from anif_platform.auth import get_api_key
from anif_platform.governance.gate import GovernanceGate
from anif_platform.human_loop.models import ApprovalTicketRow, TicketStatus
from anif_platform.human_loop.queue import ApprovalQueue, TicketError
from anif_platform.human_loop.schemas import (
    ApproveRequest,
    ApproveResponse,
    GovernanceCheckRequest,
    GovernanceCheckResponse,
    RejectRequest,
    RejectResponse,
)
from anif_platform.monitoring.metrics import (
    GOVERNANCE_AUTO,
    GOVERNANCE_BLOCK,
    GOVERNANCE_MANUAL_REVIEW,
    RULE_TRIGGERS,
    TICKET_APPROVED,
    TICKET_REJECTED,
)
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage, ReasoningStep

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/governance", tags=["governance"])


def get_audit_writer() -> AuditWriter:
    raise NotImplementedError("Override via dependency injection")


def get_approval_queue() -> ApprovalQueue:
    raise NotImplementedError("Override via dependency injection")


def get_governance_gate() -> GovernanceGate:
    return GovernanceGate()


def _parse_roles(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [r.strip() for r in raw.split(",") if r.strip()]


@router.post("/check", response_model=GovernanceCheckResponse)
async def governance_check(
    request: GovernanceCheckRequest,
    writer: AuditWriter = Depends(get_audit_writer),
    queue: ApprovalQueue = Depends(get_approval_queue),
    gate: GovernanceGate = Depends(get_governance_gate),
    _: str = Depends(get_api_key),
) -> GovernanceCheckResponse:
    """Evaluate governance rules — ANIF-406 §4.1.1. Returns 503 if audit write fails."""
    start = time.monotonic()

    gate_result = gate.check(
        intent_id=str(request.intent_id),
        operator_id=request.operator_id,
        operator_roles=request.operator_roles,
        action_type=request.action_type,
        environment=request.environment,
        risk_score=request.risk_score,
        trust_score=request.trust_score,
        policy_results=[r.model_dump() for r in request.policy_results],
        trace_id=str(request.trace_id),
    )

    mode = gate_result["mode"]
    triggered = gate_result["triggered_rule"]
    duration_ms = int((time.monotonic() - start) * 1000)

    ticket_id: str | None = None
    ticket_expires_at: datetime | None = None

    if mode == "manual_review":
        ticket = await queue.create_ticket(
            intent_id=request.intent_id,
            operator_id=request.operator_id,
            risk_score=request.risk_score,
            decision_summary=(
                f"{request.action_type} on {request.environment} "
                f"(risk_score={request.risk_score})"
            ),
        )
        ticket_id = ticket.ticket_id
        ticket_expires_at = ticket.expires_at

    outcome_map = {
        "auto": AuditOutcome.success,
        "manual_review": AuditOutcome.escalated,
        "block": AuditOutcome.blocked,
    }

    try:
        audit_record = AuditRecord(
            intent_id=request.intent_id,
            stage=AuditStage.governance,
            operator_id=request.operator_id,
            input_summary={
                "action_type": request.action_type,
                "environment": request.environment,
                "risk_score": request.risk_score,
                "trust_score": request.trust_score,
            },
            output_summary={
                "mode": mode,
                "triggered_rule": triggered,
                "ticket_id": ticket_id,
            },
            outcome=outcome_map.get(mode, AuditOutcome.success),
            duration_ms=duration_ms,
            reasoning_chain=[
                ReasoningStep(
                    step=1,
                    description=f"Governance gate evaluated; mode={mode}",
                    decision=mode,
                    rationale=gate_result["rationale"],
                )
            ],
        )
        await writer.write(audit_record)
    except Exception as exc:
        log.error("governance_audit_write_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Governance audit write failed; request cannot proceed.",
        ) from exc

    env_label = request.environment
    if mode == "auto":
        GOVERNANCE_AUTO.labels(environment=env_label).inc()
    elif mode == "manual_review":
        GOVERNANCE_MANUAL_REVIEW.labels(environment=env_label).inc()
    else:
        GOVERNANCE_BLOCK.labels(environment=env_label, triggered_rule=triggered).inc()

    for rule_id in triggered.split(", "):
        if rule_id and rule_id != "none":
            RULE_TRIGGERS.labels(rule_id=rule_id, environment=env_label).inc()

    return GovernanceCheckResponse(
        intent_id=request.intent_id,
        mode=mode,
        triggered_rule=triggered,
        rationale=gate_result["rationale"],
        ticket_id=ticket_id,
        ticket_expires_at=ticket_expires_at,
        audit_record_id=str(audit_record.record_id),
        trace_id=request.trace_id,
    )


@router.post("/approve/{ticket_id}", response_model=ApproveResponse)
async def approve_ticket(
    ticket_id: str,
    body: ApproveRequest,
    x_operator_id: str = Header(..., alias="X-Operator-Id"),
    x_operator_roles: str | None = Header(None, alias="X-Operator-Roles"),
    queue: ApprovalQueue = Depends(get_approval_queue),
    _: str = Depends(get_api_key),
) -> ApproveResponse:
    """Approve a pending ticket — ANIF-404 §4.4.4."""
    roles = _parse_roles(x_operator_roles)
    try:
        ticket = await queue.approve(
            ticket_id=ticket_id,
            approver_id=x_operator_id,
            approver_roles=roles,
            notes=body.notes,
        )
    except TicketError as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc

    TICKET_APPROVED.labels(environment="unknown", approver_role=body.approver_role).inc()

    return ApproveResponse(
        ticket_id=ticket.ticket_id,
        status=ticket.status,
        approved_by=ticket.approved_by or x_operator_id,
        approved_at=ticket.approved_at or datetime.now(UTC),
        audit_record_id="",
    )


@router.post("/reject/{ticket_id}", response_model=RejectResponse)
async def reject_ticket(
    ticket_id: str,
    body: RejectRequest,
    x_operator_id: str = Header(..., alias="X-Operator-Id"),
    x_operator_roles: str | None = Header(None, alias="X-Operator-Roles"),
    queue: ApprovalQueue = Depends(get_approval_queue),
    _: str = Depends(get_api_key),
) -> RejectResponse:
    """Reject a pending ticket — ANIF-404 §4.4.5."""
    roles = _parse_roles(x_operator_roles)
    try:
        ticket = await queue.reject(
            ticket_id=ticket_id,
            operator_id=x_operator_id,
            operator_roles=roles,
            reason=body.reason,
        )
    except TicketError as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc

    TICKET_REJECTED.labels(environment="unknown").inc()

    return RejectResponse(
        ticket_id=ticket.ticket_id,
        status=ticket.status,
        rejected_by=ticket.rejected_by or x_operator_id,
        rejected_at=ticket.rejected_at or datetime.now(UTC),
        audit_record_id="",
    )


@router.get("/tickets")
async def list_pending_tickets(
    queue: ApprovalQueue = Depends(get_approval_queue),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """List pending approval tickets — ANIF-404 §4.5."""
    result = await queue._session.execute(
        select(ApprovalTicketRow).where(ApprovalTicketRow.status == TicketStatus.pending)
    )
    tickets = result.scalars().all()
    return {
        "pending_count": len(tickets),
        "tickets": [
            {
                "ticket_id": t.ticket_id,
                "intent_id": str(t.intent_id),
                "requested_by": t.requested_by,
                "risk_score": t.risk_score,
                "decision_summary": t.decision_summary,
                "created_at": t.created_at.isoformat(),
                "expires_at": t.expires_at.isoformat(),
            }
            for t in tickets
        ],
    }
