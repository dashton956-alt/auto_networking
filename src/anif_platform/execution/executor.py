"""
ActionExecutor — orchestrates execution and automatic rollback — ANIF-306 §6.

Checks governance preconditions (§5), calls the adapter (§7), writes audit
records (§11), persists execution records (§9), and triggers automatic
rollback on failure (§8.1).
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.audit.writer import AuditWriter
from anif_platform.ethics.containment import ContainmentContract, PipelineContext
from anif_platform.execution.adapter import NetworkAdapter
from anif_platform.execution.models import ExecutionRecordRow
from anif_platform.human_loop.models import ApprovalTicketRow, TicketStatus
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage

log = structlog.get_logger(__name__)

# isolate_segment MUST NEVER auto-execute — ANIF-306 §5
_ALWAYS_REQUIRES_TICKET: frozenset[str] = frozenset({"isolate_segment"})
_HTTP_FORBIDDEN: int = 403


class PreconditionError(Exception):
    """Raised when governance preconditions are not satisfied — ANIF-306 §5."""

    def __init__(self, message: str, http_status: int = 403) -> None:
        super().__init__(message)
        self.http_status = http_status


class ActionExecutor:
    """
    Orchestrates action execution with precondition checks and automatic rollback.

    Inject adapter, session, and writer via constructor.
    """

    def __init__(
        self,
        adapter: NetworkAdapter,
        session: AsyncSession,
        writer: AuditWriter,
    ) -> None:
        self._adapter = adapter
        self._session = session
        self._writer = writer

    async def execute(
        self,
        pipeline_context: PipelineContext,
        decision: dict[str, Any],
        parameters: dict[str, Any],
        ticket_id: str | None,
    ) -> dict[str, Any]:
        """
        Execute an action after verifying governance preconditions — ANIF-306 §6.1.

        ContainmentContract.validate() MUST be the first operation — ANIF-725 §4.3.
        Writes EXECUTION_START before calling the adapter.
        Writes EXECUTION_SUCCESS or EXECUTION_FAILED after the adapter responds.
        Triggers automatic rollback on failure (§8.1).
        """
        ContainmentContract.validate(pipeline_context)
        intent_id = pipeline_context.intent_id
        governance_result = pipeline_context.governance_decision or {}

        decision_id = decision.get("decision_id", "")
        action_type = decision.get("recommended_action", {}).get("action_type", "apply_qos")
        execution_id = str(uuid.uuid4())

        # ── Precondition check ────────────────────────────────────────────
        await self._check_preconditions(
            intent_id=intent_id,
            action_type=action_type,
            governance_result=governance_result,
            ticket_id=ticket_id,
        )

        # ── EXECUTION_START audit ─────────────────────────────────────────
        executed_at = datetime.now(UTC)
        await self._writer.write(
            AuditRecord(
                intent_id=intent_id,
                stage=AuditStage.execute,
                input_summary={
                    "execution_id": execution_id,
                    "action_type": action_type,
                    "event": "EXECUTION_START",
                },
                output_summary={},
                outcome=AuditOutcome.success,
                duration_ms=0,
            )
        )

        # ── Call adapter ──────────────────────────────────────────────────
        start = time.monotonic()
        try:
            adapter_response = self._adapter.execute(action_type, parameters, execution_id)
        except Exception as exc:
            duration_ms = int((time.monotonic() - start) * 1000)
            completed_at = datetime.now(UTC)
            await self._writer.write(
                AuditRecord(
                    intent_id=intent_id,
                    stage=AuditStage.execute,
                    input_summary={
                        "execution_id": execution_id,
                        "action_type": action_type,
                        "event": "EXECUTION_FAILED",
                    },
                    output_summary={"error": str(exc)},
                    outcome=AuditOutcome.failure,
                    duration_ms=duration_ms,
                )
            )
            raise
        duration_ms = int((time.monotonic() - start) * 1000)
        completed_at = datetime.now(UTC)

        rollback_available = (
            adapter_response.success and adapter_response.rollback_reference is not None
        )
        rollback_status: str | None = None

        exec_status = "success" if adapter_response.success else "failed"
        outcome = AuditOutcome.success if adapter_response.success else AuditOutcome.failure
        event = "EXECUTION_SUCCESS" if adapter_response.success else "EXECUTION_FAILED"

        # ── Persist execution record ──────────────────────────────────────
        record = ExecutionRecordRow(
            execution_id=execution_id,
            intent_id=intent_id,
            decision_id=decision_id,
            action_type=action_type,
            status=exec_status,
            adapter_name="mock",
            adapter_status_code=adapter_response.adapter_status_code,
            adapter_message=adapter_response.adapter_message,
            applied_changes=json.dumps(adapter_response.applied_changes),
            rollback_reference=adapter_response.rollback_reference,
            rollback_available=rollback_available,
            rollback_status=None,
            duration_ms=duration_ms,
            executed_at=executed_at,
            completed_at=completed_at,
            parameters_json=json.dumps(parameters),
        )
        self._session.add(record)
        await self._session.flush()

        # ── EXECUTION_SUCCESS / EXECUTION_FAILED audit ────────────────────
        await self._writer.write(
            AuditRecord(
                intent_id=intent_id,
                stage=AuditStage.execute,
                input_summary={
                    "execution_id": execution_id,
                    "action_type": action_type,
                    "event": event,
                },
                output_summary={
                    "status": exec_status,
                    "adapter_status_code": adapter_response.adapter_status_code,
                    "rollback_available": rollback_available,
                },
                outcome=outcome,
                duration_ms=duration_ms,
            )
        )

        log.info(
            "execution_completed",
            execution_id=execution_id,
            intent_id=str(intent_id),
            action_type=action_type,
            status=exec_status,
        )

        # ── Automatic rollback on failure (§8.1) ─────────────────────────
        if not adapter_response.success:
            rollback_status, _ = await self._auto_rollback(
                intent_id=intent_id,
                action_type=action_type,
                rollback_reference=adapter_response.rollback_reference,
                execution_id=execution_id,
            )
            record.rollback_status = rollback_status
            await self._session.flush()

        return {
            "execution_id": execution_id,
            "intent_id": intent_id,
            "decision_id": decision_id,
            "action_type": action_type,
            "status": exec_status,
            "adapter_response": {
                "success": adapter_response.success,
                "adapter_status_code": adapter_response.adapter_status_code,
                "adapter_message": adapter_response.adapter_message,
                "applied_changes": adapter_response.applied_changes,
                "rollback_reference": adapter_response.rollback_reference,
            },
            "duration_ms": duration_ms,
            "rollback_available": rollback_available,
            "rollback_status": rollback_status,
            "executed_at": executed_at.isoformat(),
            "completed_at": completed_at.isoformat(),
        }

    async def rollback(self, intent_id: uuid.UUID) -> dict[str, Any]:
        """
        Manually roll back the most recent execution for an intent — ANIF-306 §6.2.

        Callable using only intent_id.
        """
        result = await self._session.execute(
            select(ExecutionRecordRow)
            .where(ExecutionRecordRow.intent_id == intent_id)
            .order_by(ExecutionRecordRow.executed_at.desc())
            .limit(1)
        )
        record = result.scalar_one_or_none()
        if record is None:
            raise ValueError(f"No execution record found for intent_id={intent_id}")

        rollback_status, rollback_audit_id = await self._auto_rollback(
            intent_id=intent_id,
            action_type=record.action_type,
            rollback_reference=record.rollback_reference,
            execution_id=record.execution_id,
        )

        return {
            "intent_id": intent_id,
            "execution_id": record.execution_id,
            "action_type": record.action_type,
            "rollback_status": rollback_status,
            "rolled_back_at": datetime.now(UTC).isoformat(),
            "audit_record_id": rollback_audit_id,
        }

    # ── Private helpers ───────────────────────────────────────────────────

    async def _check_preconditions(
        self,
        intent_id: uuid.UUID,
        action_type: str,
        governance_result: dict[str, Any],
        ticket_id: str | None,
    ) -> None:
        """Check ANIF-306 §5 preconditions; raise PreconditionError and write audit if unmet."""
        mode = governance_result.get("mode", "block")

        # isolate_segment always requires an approved ticket
        if action_type in _ALWAYS_REQUIRES_TICKET and mode == "auto":
            await self._write_precondition_failed(
                intent_id=intent_id,
                action_type=action_type,
                reason="isolate_segment MUST NOT execute under auto mode (ANIF-306 §5).",
            )
            raise PreconditionError(
                "isolate_segment requires an approved governance ticket; auto mode is prohibited.",
                http_status=_HTTP_FORBIDDEN,
            )

        if mode == "manual_review":
            if not ticket_id:
                await self._write_precondition_failed(
                    intent_id=intent_id,
                    action_type=action_type,
                    reason="manual_review mode requires a ticket_id but none was provided.",
                )
                raise PreconditionError(
                    "Governance mode is manual_review but ticket_id was not provided.",
                    http_status=_HTTP_FORBIDDEN,
                )

            ticket = await self._session.get(ApprovalTicketRow, ticket_id)
            if ticket is None or ticket.status != TicketStatus.approved:
                status = ticket.status if ticket else "not_found"
                await self._write_precondition_failed(
                    intent_id=intent_id,
                    action_type=action_type,
                    reason=f"Ticket {ticket_id} must be approved (status: {status}).",
                )
                raise PreconditionError(
                    f"Ticket {ticket_id} is not approved (status: {status}).",
                    http_status=_HTTP_FORBIDDEN,
                )

    async def _write_precondition_failed(
        self,
        intent_id: uuid.UUID,
        action_type: str,
        reason: str,
    ) -> None:
        await self._writer.write(
            AuditRecord(
                intent_id=intent_id,
                stage=AuditStage.execute,
                input_summary={"action_type": action_type, "event": "PRECONDITION_FAILED"},
                output_summary={"reason": reason},
                outcome=AuditOutcome.blocked,
                duration_ms=0,
            )
        )

    async def _auto_rollback(
        self,
        intent_id: uuid.UUID,
        action_type: str,
        rollback_reference: str | None,
        execution_id: str,
    ) -> tuple[str, str]:
        """Attempt automatic rollback — ANIF-306 §8.1. Returns (rollback_status, audit_record_id)."""
        rollback_id = str(uuid.uuid4())

        await self._writer.write(
            AuditRecord(
                intent_id=intent_id,
                stage=AuditStage.rollback,
                input_summary={
                    "execution_id": execution_id,
                    "action_type": action_type,
                    "event": "ROLLBACK_START",
                    "rollback_reference": rollback_reference,
                },
                output_summary={},
                outcome=AuditOutcome.success,
                duration_ms=0,
            )
        )

        try:
            rb_response = self._adapter.rollback(action_type, rollback_reference, rollback_id)
        except Exception as exc:
            log.error(
                "rollback_adapter_exception",
                intent_id=str(intent_id),
                action_type=action_type,
                execution_id=execution_id,
                error=str(exc),
            )
            # Treat adapter exception as rollback failure
            from anif_platform.execution.adapter import AdapterResponse

            rb_response = AdapterResponse(
                success=False,
                adapter_status_code=500,
                adapter_message=f"Adapter raised exception during rollback: {exc}",
                applied_changes=[],
                rollback_reference=None,
            )
        rollback_status = "success" if rb_response.success else "failed"
        outcome = AuditOutcome.success if rb_response.success else AuditOutcome.failure
        event = "ROLLBACK_SUCCESS" if rb_response.success else "ROLLBACK_FAILED"

        if not rb_response.success:
            log.error(
                "rollback_failed_human_escalation_required",
                intent_id=str(intent_id),
                action_type=action_type,
                execution_id=execution_id,
            )

        final_audit = AuditRecord(
            intent_id=intent_id,
            stage=AuditStage.rollback,
            input_summary={
                "execution_id": execution_id,
                "action_type": action_type,
                "event": event,
            },
            output_summary={
                "rollback_status": rollback_status,
                "adapter_status_code": rb_response.adapter_status_code,
            },
            outcome=outcome,
            duration_ms=0,
        )
        await self._writer.write(final_audit)

        return (rollback_status, str(final_audit.record_id))
