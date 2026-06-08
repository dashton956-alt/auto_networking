"""Tests for AuditRecord Pydantic model — ANIF-107, ANIF-600 §4.5, ANIF-724."""

import uuid
from datetime import UTC

import pytest
from pydantic import ValidationError

from anif_platform.schemas.audit_record import (
    AuditOutcome,
    AuditRecord,
    AuditStage,
    ReasoningStep,
)

INTENT_ID = uuid.uuid4()


def make_base_record(**kwargs) -> AuditRecord:
    defaults = dict(
        intent_id=INTENT_ID,
        stage=AuditStage.validate,
        input_summary={"service": "payments"},
        output_summary={"result": "pass"},
        outcome=AuditOutcome.success,
        duration_ms=12,
    )
    defaults.update(kwargs)
    return AuditRecord(**defaults)


class TestReasoningStep:
    def test_valid_step(self) -> None:
        step = ReasoningStep(step=1, description="Schema checked", decision="Pass")
        assert step.step == 1

    def test_step_required(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningStep(description="x", decision="y")  # type: ignore[call-arg]

    def test_rationale_optional(self) -> None:
        step = ReasoningStep(step=1, description="x", decision="y")
        assert step.rationale is None


class TestAuditRecord:
    def test_valid_record_auto_generates_record_id(self) -> None:
        record = make_base_record()
        assert record.record_id is not None
        assert isinstance(record.record_id, uuid.UUID)

    def test_valid_record_auto_generates_timestamp(self) -> None:
        record = make_base_record()
        assert record.timestamp.tzinfo is not None

    def test_intent_id_required(self) -> None:
        with pytest.raises(ValidationError):
            AuditRecord(
                stage=AuditStage.validate,
                input_summary={},
                output_summary={},
                outcome=AuditOutcome.success,
                duration_ms=1,
            )  # type: ignore[call-arg]

    def test_invalid_stage_rejected(self) -> None:
        with pytest.raises(ValidationError):
            make_base_record(stage="unknown_stage")

    def test_invalid_outcome_rejected(self) -> None:
        with pytest.raises(ValidationError):
            make_base_record(outcome="partial")

    def test_duration_ms_cannot_be_negative(self) -> None:
        with pytest.raises(ValidationError):
            make_base_record(duration_ms=-1)

    def test_duration_ms_zero_is_valid(self) -> None:
        record = make_base_record(duration_ms=0)
        assert record.duration_ms == 0

    def test_decision_stage_requires_nonempty_reasoning_chain(self) -> None:
        """ANIF-107 §4.2.2: reasoning_chain MUST NOT be empty for decision stage."""
        with pytest.raises(ValidationError):
            make_base_record(stage=AuditStage.decision, reasoning_chain=[])

    def test_governance_stage_requires_nonempty_reasoning_chain(self) -> None:
        """ANIF-107 §4.2.2: reasoning_chain MUST NOT be empty for governance stage."""
        with pytest.raises(ValidationError):
            make_base_record(stage=AuditStage.governance, reasoning_chain=[])

    def test_validate_stage_allows_empty_reasoning_chain(self) -> None:
        record = make_base_record(stage=AuditStage.validate, reasoning_chain=[])
        assert record.reasoning_chain == []

    def test_reasoning_chain_with_steps_accepted(self) -> None:
        record = make_base_record(
            stage=AuditStage.decision,
            reasoning_chain=[
                ReasoningStep(step=1, description="Risk checked", decision="warn"),
            ],
        )
        assert len(record.reasoning_chain) == 1

    def test_timestamp_is_utc(self) -> None:
        record = make_base_record()
        assert record.timestamp.tzinfo == UTC or str(record.timestamp.tzinfo) == "UTC"

    def test_operator_id_defaults_to_none(self) -> None:
        record = make_base_record()
        assert record.operator_id is None

    def test_hash_chain_fields_default_to_none(self) -> None:
        record = make_base_record()
        assert record.record_hash is None
        assert record.prev_hash is None
        assert record.chain_id is None

    def test_all_seven_stages_are_valid(self) -> None:
        for stage in AuditStage:
            chain = []
            if stage in (AuditStage.decision, AuditStage.governance):
                chain = [ReasoningStep(step=1, description="x", decision="y")]
            record = make_base_record(stage=stage, reasoning_chain=chain)
            assert record.stage == stage

    def test_ethics_fields_optional(self) -> None:
        """ANIF-724: ethics fields are optional (only required for AI-involved actions)."""
        record = make_base_record()
        assert record.agent_id is None
        assert record.llm_used is None
        assert record.harm_class is None
