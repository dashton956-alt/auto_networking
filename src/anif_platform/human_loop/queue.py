"""
ApprovalQueue — approval ticket lifecycle — ANIF-404 §4.4.

Wraps AsyncSession and AuditWriter. Raises TicketError for all
rule violations (caller converts to HTTP status codes).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.audit.writer import AuditWriter
from anif_platform.human_loop.models import ApprovalTicketRow, TicketStatus
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage, ReasoningStep

log = structlog.get_logger(__name__)

_TICKET_EXPIRY_MINUTES = 15  # ANIF-404 §4.4.1 — NOT configurable
_APPROVER_ROLES = frozenset({"senior_engineer"})
_REJECTOR_ROLES = frozenset({"network_engineer", "senior_engineer"})


class TicketError(Exception):
    """Raised for all ticket lifecycle violations."""

    def __init__(self, message: str, http_status: int = 400) -> None:
        super().__init__(message)
        self.http_status = http_status


class ApprovalQueue:
    """
    Stateful approval ticket CRUD — ANIF-404 §4.4.

    One instance per request. Inject via FastAPI dependency.
    """

    def __init__(self, session: AsyncSession, writer: AuditWriter) -> None:
        self._session = session
        self._writer = writer

    async def create_ticket(
        self,
        intent_id: uuid.UUID,
        operator_id: str,
        risk_score: int,
        decision_summary: str,
    ) -> ApprovalTicketRow:
        """
        Create a new approval ticket in pending state — ANIF-404 §4.4.1.

        Writes an audit record before returning (write-before-return).
        """
        now = datetime.now(UTC)
        ticket = ApprovalTicketRow(
            ticket_id=str(uuid.uuid4()),
            intent_id=intent_id,
            status=TicketStatus.pending,
            requested_by=operator_id,
            decision_summary=decision_summary,
            risk_score=risk_score,
            required_approver_role="senior_engineer",
            created_at=now,
            expires_at=now + timedelta(minutes=_TICKET_EXPIRY_MINUTES),
        )
        self._session.add(ticket)
        await self._session.flush()

        await self._writer.write(
            AuditRecord(
                intent_id=intent_id,
                stage=AuditStage.governance,
                operator_id=operator_id,
                input_summary={"ticket_id": ticket.ticket_id, "action": "ticket_created"},
                output_summary={
                    "status": TicketStatus.pending,
                    "expires_at": ticket.expires_at.isoformat(),
                },
                outcome=AuditOutcome.escalated,
                duration_ms=0,
                reasoning_chain=[
                    ReasoningStep(
                        step=1,
                        description="Approval ticket created",
                        decision="pending",
                        rationale=(
                            "Action requires manual review; ticket created for "
                            "senior_engineer approval."
                        ),
                    )
                ],
            )
        )

        log.info(
            "approval_ticket_created",
            ticket_id=ticket.ticket_id,
            intent_id=str(intent_id),
            requested_by=operator_id,
            expires_at=ticket.expires_at.isoformat(),
        )
        return ticket

    async def get_ticket(self, ticket_id: str) -> ApprovalTicketRow | None:
        """Retrieve a ticket by ID."""
        return await self._session.get(ApprovalTicketRow, ticket_id)

    async def approve(
        self,
        ticket_id: str,
        approver_id: str,
        approver_roles: list[str],
        notes: str | None = None,
    ) -> ApprovalTicketRow:
        """
        Approve a pending ticket — ANIF-404 §4.4.4.

        Raises TicketError for: wrong role, self-approval, non-pending state.
        Writes audit record before returning.
        """
        if not set(approver_roles).intersection(_APPROVER_ROLES):
            raise TicketError(
                f"Approval requires senior_engineer role. Caller roles: {approver_roles}",
                http_status=403,
            )

        ticket = await self._get_or_raise(ticket_id)

        if ticket.requested_by == approver_id:
            raise TicketError(
                f"self-approval is prohibited (ANIF-404 §4.4.4). "
                f"Submitter and approver are both {approver_id}.",
                http_status=403,
            )

        if ticket.status != TicketStatus.pending:
            raise TicketError(
                f"Ticket {ticket_id} is not in pending state (current: {ticket.status}). "
                f"Approved, rejected, and expired tickets are terminal.",
                http_status=409,
            )

        now = datetime.now(UTC)
        ticket.status = TicketStatus.approved
        ticket.approved_by = approver_id
        ticket.approved_at = now
        ticket.approval_notes = notes
        await self._session.flush()

        await self._writer.write(
            AuditRecord(
                intent_id=ticket.intent_id,
                stage=AuditStage.governance,
                operator_id=approver_id,
                input_summary={"ticket_id": ticket_id, "action": "approve"},
                output_summary={"status": TicketStatus.approved, "approved_by": approver_id},
                outcome=AuditOutcome.success,
                duration_ms=0,
                reasoning_chain=[
                    ReasoningStep(
                        step=1,
                        description="Ticket approved",
                        decision="approved",
                        rationale=(
                            f"Approver {approver_id} (senior_engineer) approved the ticket."
                        ),
                    )
                ],
            )
        )

        log.info("approval_ticket_approved", ticket_id=ticket_id, approver_id=approver_id)
        return ticket

    async def reject(
        self,
        ticket_id: str,
        operator_id: str,
        operator_roles: list[str],
        reason: str,
    ) -> ApprovalTicketRow:
        """
        Reject a pending ticket — ANIF-404 §4.4.5.

        Raises TicketError for: missing reason, wrong role, non-pending state.
        Writes audit record before returning.
        """
        if not reason or not reason.strip():
            raise TicketError(
                "A reason MUST be provided when rejecting a ticket (ANIF-404 §4.4.5).",
                http_status=400,
            )

        if not set(operator_roles).intersection(_REJECTOR_ROLES):
            raise TicketError(
                f"Rejection requires network_engineer role or above. Caller roles: {operator_roles}",
                http_status=403,
            )

        ticket = await self._get_or_raise(ticket_id)

        if ticket.status != TicketStatus.pending:
            raise TicketError(
                f"Ticket {ticket_id} is not in pending state (current: {ticket.status}).",
                http_status=409,
            )

        now = datetime.now(UTC)
        ticket.status = TicketStatus.rejected
        ticket.rejected_by = operator_id
        ticket.rejected_at = now
        ticket.rejection_reason = reason
        await self._session.flush()

        await self._writer.write(
            AuditRecord(
                intent_id=ticket.intent_id,
                stage=AuditStage.governance,
                operator_id=operator_id,
                input_summary={"ticket_id": ticket_id, "action": "reject"},
                output_summary={"status": TicketStatus.rejected, "reason": reason},
                outcome=AuditOutcome.failure,
                duration_ms=0,
                reasoning_chain=[
                    ReasoningStep(
                        step=1,
                        description="Ticket rejected",
                        decision="rejected",
                        rationale=(f"Operator {operator_id} rejected the ticket. Reason: {reason}"),
                    )
                ],
            )
        )

        log.info("approval_ticket_rejected", ticket_id=ticket_id, operator_id=operator_id)
        return ticket

    async def expire_pending(self) -> list[str]:
        """
        Transition overdue pending tickets to expired — ANIF-406 §4.4.3.

        Called by the background expiry task every 60 seconds.
        Returns list of expired ticket IDs.
        Writes one audit record per expiry event.
        """
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(ApprovalTicketRow).where(
                ApprovalTicketRow.status == TicketStatus.pending,
                ApprovalTicketRow.expires_at <= now,
            )
        )
        overdue = result.scalars().all()
        expired_ids: list[str] = []

        for ticket in overdue:
            ticket.status = TicketStatus.expired
            await self._session.flush()

            await self._writer.write(
                AuditRecord(
                    intent_id=ticket.intent_id,
                    stage=AuditStage.governance,
                    operator_id="system",
                    input_summary={"ticket_id": ticket.ticket_id, "action": "expire"},
                    output_summary={
                        "status": TicketStatus.expired,
                        "requested_by": ticket.requested_by,
                        "expired_at": now.isoformat(),
                    },
                    outcome=AuditOutcome.failure,
                    duration_ms=0,
                    reasoning_chain=[
                        ReasoningStep(
                            step=1,
                            description="Ticket expired",
                            decision="expired",
                            rationale=(
                                f"Ticket {ticket.ticket_id} exceeded its "
                                f"{_TICKET_EXPIRY_MINUTES}-minute approval window."
                            ),
                        )
                    ],
                )
            )

            log.warning(
                "approval_ticket_expired",
                ticket_id=ticket.ticket_id,
                intent_id=str(ticket.intent_id),
                requested_by=ticket.requested_by,
            )
            expired_ids.append(ticket.ticket_id)

        return expired_ids

    async def _get_or_raise(self, ticket_id: str) -> ApprovalTicketRow:
        ticket = await self._session.get(ApprovalTicketRow, ticket_id)
        if ticket is None:
            raise TicketError(f"Ticket {ticket_id} not found.", http_status=404)
        return ticket
