"""Tests for ANIF-725 pipeline containment contract."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from anif_platform.ethics.constraints import RollbackPlan
from anif_platform.ethics.containment import ContainmentContract, PipelineContext
from anif_platform.exceptions import ANIFError


def _valid_context(**overrides) -> PipelineContext:  # type: ignore[no-untyped-def]
    base: dict = dict(
        intent_id=uuid.uuid4(),
        policy_result={"mode": "auto", "policies_evaluated": []},
        risk_score_result={"score": 20, "threshold_applied": "default"},
        harm_classification_result={"harm_class": "none", "harm_severity_score": 10},
        fairness_check_result={
            "sla_floor_result": "not_applicable",
            "freshness_gate_result": "pass",
        },
        llm_validation_result=None,
        governance_decision={"mode": "auto", "ticket_id": None},
        rollback_plan=RollbackPlan(
            rollback_action_type="reroute_traffic",
            rollback_target="segment-a",
            rollback_within_seconds=60,
            rollback_confirmed_at=datetime.now(UTC),
        ),
    )
    base.update(overrides)
    return PipelineContext(**base)


def test_valid_context_passes_validation() -> None:
    """ANIF-725 §4.2: a fully specified PipelineContext passes containment validation."""
    ctx = _valid_context()
    ContainmentContract.validate(ctx)  # must not raise


def test_missing_policy_result_raises() -> None:
    """ANIF-725 §4.2: policy_result is mandatory — None raises ANIFError."""
    ctx = _valid_context(policy_result=None)
    with pytest.raises(ANIFError, match="policy_result"):
        ContainmentContract.validate(ctx)


def test_missing_risk_score_result_raises() -> None:
    """ANIF-725 §4.2: risk_score_result is mandatory."""
    ctx = _valid_context(risk_score_result=None)
    with pytest.raises(ANIFError, match="risk_score_result"):
        ContainmentContract.validate(ctx)


def test_missing_harm_classification_raises() -> None:
    """ANIF-725 §4.2: harm_classification_result is mandatory."""
    ctx = _valid_context(harm_classification_result=None)
    with pytest.raises(ANIFError, match="harm_classification_result"):
        ContainmentContract.validate(ctx)


def test_missing_fairness_check_raises() -> None:
    """ANIF-725 §4.2: fairness_check_result is mandatory."""
    ctx = _valid_context(fairness_check_result=None)
    with pytest.raises(ANIFError, match="fairness_check_result"):
        ContainmentContract.validate(ctx)


def test_missing_governance_decision_raises() -> None:
    """ANIF-725 §4.2: governance_decision is mandatory."""
    ctx = _valid_context(governance_decision=None)
    with pytest.raises(ANIFError, match="governance_decision"):
        ContainmentContract.validate(ctx)


def test_missing_rollback_plan_raises() -> None:
    """ANIF-725 §4.2: rollback_plan is mandatory — ANIF-721 §5 constraint."""
    ctx = _valid_context(rollback_plan=None)
    with pytest.raises(ANIFError, match="rollback_plan"):
        ContainmentContract.validate(ctx)
