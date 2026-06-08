"""Unit tests for ActionExecutor — ANIF-306 §5, §6, §8."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from anif_platform.ethics.constraints import RollbackPlan
from anif_platform.ethics.containment import PipelineContext
from anif_platform.execution.executor import ActionExecutor, PreconditionError
from anif_platform.execution.mock_adapter import MockNetworkAdapter
from anif_platform.execution.models import ExecutionRecordRow
from anif_platform.human_loop.models import ApprovalTicketRow, TicketStatus


def make_gov_auto() -> dict:
    return {"mode": "auto", "triggered_rule": "none", "rationale": "auto"}


def make_gov_manual_approved() -> dict:
    return {"mode": "manual_review", "triggered_rule": "R-02", "rationale": "review"}


def make_pipeline_context(
    intent_id: uuid.UUID | None = None,
    governance_result: dict | None = None,
) -> PipelineContext:
    return PipelineContext(
        intent_id=intent_id or uuid.uuid4(),
        policy_result={"mode": "auto", "policies_evaluated": []},
        risk_score_result={"risk_score": 20, "threshold_applied": "default"},
        harm_classification_result={"harm_class": "none", "harm_severity_score": 10},
        fairness_check_result={"sla_floor_result": "not_applicable", "freshness_gate_result": "pass"},
        llm_validation_result=None,
        governance_decision=governance_result or make_gov_auto(),
        rollback_plan=RollbackPlan(
            rollback_action_type="apply_qos",
            rollback_target="segment-test",
            rollback_within_seconds=60,
            rollback_confirmed_at=datetime.now(UTC),
        ),
    )


def make_decision(action_type: str = "apply_qos") -> dict:
    return {
        "decision_id": str(uuid.uuid4()),
        "recommended_action": {"action_type": action_type, "parameters": {}, "risk_level": "low"},
        "rollback_plan": {
            "action_type": action_type,
            "description": "Rollback",
            "estimated_duration_ms": 2000,
        },
    }


def make_params(action_type: str = "apply_qos") -> dict:
    params = {
        "reroute_traffic": {
            "source_segment": "s1",
            "target_segment": "s2",
            "routing_protocol": "BGP",
        },
        "apply_qos": {
            "policy_name": "prio",
            "traffic_class": "DSCP_EF",
            "bandwidth_guarantee_mbps": 100,
        },
        "scale_bandwidth": {"segment_id": "seg-1", "target_bandwidth_mbps": 200, "direction": "up"},
        "isolate_segment": {
            "segment_id": "seg-1",
            "isolation_reason": "fault",
            "blast_radius_assessment": "low",
        },
    }
    return params.get(action_type, {})


def make_executor(
    force_success: bool = False,
    force_failure: bool = False,
) -> tuple[ActionExecutor, AsyncMock, AsyncMock]:
    adapter = MockNetworkAdapter(seed=42, force_success=force_success, force_failure=force_failure)
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    writer = AsyncMock()
    executor = ActionExecutor(adapter=adapter, session=session, writer=writer)
    return executor, session, writer


class TestGovernancePreconditions:
    @pytest.mark.asyncio
    async def test_auto_mode_permits_non_isolate_actions(self) -> None:
        """ANIF-306 §5: auto mode satisfies Precondition A for non-isolate actions."""
        executor, _, _ = make_executor()
        result = await executor.execute(
            pipeline_context=make_pipeline_context(),
            decision=make_decision("apply_qos"),
            parameters=make_params("apply_qos"),
            ticket_id=None,
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_isolate_segment_blocked_in_auto_mode(self) -> None:
        """ANIF-306 §5: isolate_segment MUST NOT execute under auto mode."""
        executor, _, _ = make_executor()
        with pytest.raises(PreconditionError, match="isolate_segment"):
            await executor.execute(
                pipeline_context=make_pipeline_context(),
                decision=make_decision("isolate_segment"),
                parameters=make_params("isolate_segment"),
                ticket_id=None,
            )

    @pytest.mark.asyncio
    async def test_isolate_segment_permitted_with_approved_ticket(self) -> None:
        """ANIF-306 §5: isolate_segment executes when Precondition B (approved ticket) is met."""
        executor, session, _ = make_executor()
        ticket = ApprovalTicketRow()
        ticket.ticket_id = "t-001"
        ticket.status = TicketStatus.approved
        ticket.intent_id = uuid.uuid4()
        ticket.requested_by = "jsmith"
        ticket.decision_summary = "test"
        ticket.risk_score = 80
        ticket.required_approver_role = "senior_engineer"
        ticket.created_at = datetime.now(UTC)
        ticket.expires_at = datetime.now(UTC)
        session.get = AsyncMock(return_value=ticket)

        result = await executor.execute(
            pipeline_context=make_pipeline_context(governance_result=make_gov_manual_approved()),
            decision=make_decision("isolate_segment"),
            parameters=make_params("isolate_segment"),
            ticket_id="t-001",
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_manual_review_without_ticket_id_raises(self) -> None:
        """ANIF-306 §5: manual_review mode requires ticket_id."""
        executor, _, _ = make_executor()
        with pytest.raises(PreconditionError, match="ticket_id"):
            await executor.execute(
                pipeline_context=make_pipeline_context(governance_result=make_gov_manual_approved()),
                decision=make_decision("apply_qos"),
                parameters=make_params("apply_qos"),
                ticket_id=None,
            )

    @pytest.mark.asyncio
    async def test_manual_review_with_pending_ticket_raises(self) -> None:
        """ANIF-306 §5: Precondition B requires status=approved, not pending."""
        executor, session, _ = make_executor()
        ticket = ApprovalTicketRow()
        ticket.ticket_id = "t-002"
        ticket.status = TicketStatus.pending
        ticket.intent_id = uuid.uuid4()
        ticket.requested_by = "jsmith"
        ticket.decision_summary = "test"
        ticket.risk_score = 80
        ticket.required_approver_role = "senior_engineer"
        ticket.created_at = datetime.now(UTC)
        ticket.expires_at = datetime.now(UTC)
        session.get = AsyncMock(return_value=ticket)

        with pytest.raises(PreconditionError, match="approved"):
            await executor.execute(
                pipeline_context=make_pipeline_context(governance_result=make_gov_manual_approved()),
                decision=make_decision("apply_qos"),
                parameters=make_params("apply_qos"),
                ticket_id="t-002",
            )

    @pytest.mark.asyncio
    async def test_precondition_failure_writes_audit_record(self) -> None:
        """ANIF-306 §11: PRECONDITION_FAILED event MUST be written to audit."""
        executor, _, writer = make_executor()
        with pytest.raises(PreconditionError):
            await executor.execute(
                pipeline_context=make_pipeline_context(),
                decision=make_decision("isolate_segment"),
                parameters=make_params("isolate_segment"),
                ticket_id=None,
            )
        writer.write.assert_called_once()


class TestExecuteSuccess:
    @pytest.mark.asyncio
    async def test_success_returns_required_fields(self) -> None:
        """ANIF-306 §9: execution response MUST include all required fields."""
        executor, _, _ = make_executor(force_success=True)
        intent_id = uuid.uuid4()
        result = await executor.execute(
            pipeline_context=make_pipeline_context(intent_id=intent_id),
            decision=make_decision("apply_qos"),
            parameters=make_params("apply_qos"),
            ticket_id=None,
        )
        assert result["execution_id"]
        assert result["intent_id"] == intent_id
        assert result["decision_id"]
        assert result["action_type"] == "apply_qos"
        assert result["status"] == "success"
        assert result["adapter_response"]["success"] is True
        assert isinstance(result["duration_ms"], int)
        assert result["rollback_available"] is True
        assert result["rollback_status"] is None
        assert result["executed_at"]
        assert result["completed_at"]

    @pytest.mark.asyncio
    async def test_success_writes_two_audit_records(self) -> None:
        """ANIF-306 §11: EXECUTION_START and EXECUTION_SUCCESS MUST be written."""
        executor, _, writer = make_executor(force_success=True)
        await executor.execute(
            pipeline_context=make_pipeline_context(),
            decision=make_decision("apply_qos"),
            parameters=make_params("apply_qos"),
            ticket_id=None,
        )
        assert writer.write.call_count == 2

    @pytest.mark.asyncio
    async def test_success_persists_execution_record(self) -> None:
        """Execution record MUST be persisted to DB."""
        executor, session, _ = make_executor(force_success=True)
        await executor.execute(
            pipeline_context=make_pipeline_context(),
            decision=make_decision("apply_qos"),
            parameters=make_params("apply_qos"),
            ticket_id=None,
        )
        session.add.assert_called_once()


class TestExecuteFailureAndRollback:
    @pytest.mark.asyncio
    async def test_failure_triggers_automatic_rollback(self) -> None:
        """ANIF-306 §8.1: automatic rollback MUST be attempted on every failure."""
        executor, _, writer = make_executor(force_failure=True)
        result = await executor.execute(
            pipeline_context=make_pipeline_context(),
            decision=make_decision("apply_qos"),
            parameters=make_params("apply_qos"),
            ticket_id=None,
        )
        assert result["status"] == "failed"
        # 3 audit records: EXECUTION_START, EXECUTION_FAILED, ROLLBACK_START + ROLLBACK_SUCCESS
        assert writer.write.call_count >= 3

    @pytest.mark.asyncio
    async def test_failure_response_has_rollback_status(self) -> None:
        """ANIF-306 §9: rollback_status MUST be set after automatic rollback."""
        executor, _, _ = make_executor(force_failure=True)
        result = await executor.execute(
            pipeline_context=make_pipeline_context(),
            decision=make_decision("scale_bandwidth"),
            parameters=make_params("scale_bandwidth"),
            ticket_id=None,
        )
        assert result["rollback_status"] in ("success", "failed")

    @pytest.mark.asyncio
    async def test_failure_rollback_available_is_false(self) -> None:
        """ANIF-306 §9: rollback_available=False when adapter returned null rollback_reference."""
        executor, _, _ = make_executor(force_failure=True)
        result = await executor.execute(
            pipeline_context=make_pipeline_context(),
            decision=make_decision("apply_qos"),
            parameters=make_params("apply_qos"),
            ticket_id=None,
        )
        assert result["rollback_available"] is False


class TestManualRollback:
    @pytest.mark.asyncio
    async def test_rollback_by_intent_id(self) -> None:
        """ANIF-306 §6.2: rollback MUST be callable using only intent_id."""
        executor, session, writer = make_executor(force_success=True)
        record = ExecutionRecordRow()
        record.execution_id = str(uuid.uuid4())
        record.intent_id = uuid.uuid4()
        record.decision_id = str(uuid.uuid4())
        record.action_type = "apply_qos"
        record.status = "success"
        record.adapter_name = "mock"
        record.adapter_status_code = 200
        record.adapter_message = "ok"
        record.applied_changes = "[]"
        record.rollback_reference = "mock-rollback-abc"
        record.rollback_available = True
        record.rollback_status = None
        record.duration_ms = 100
        record.executed_at = datetime.now(UTC)
        record.completed_at = datetime.now(UTC)
        record.parameters_json = "{}"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = record
        session.execute = AsyncMock(return_value=mock_result)
        session.flush = AsyncMock()

        result = await executor.rollback(intent_id=record.intent_id)
        assert result["rollback_status"] == "success"
        assert isinstance(result["audit_record_id"], str)
        assert result["audit_record_id"]  # non-empty
        assert result["intent_id"] == record.intent_id

    @pytest.mark.asyncio
    async def test_rollback_not_found_raises(self) -> None:
        """Rollback with unknown intent_id MUST raise a clear error."""
        executor, session, _ = make_executor()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="No execution record"):
            await executor.rollback(intent_id=uuid.uuid4())
