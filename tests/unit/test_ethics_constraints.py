"""Tests for ANIF-721 agent action constraints."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from anif_platform.ethics.constraints import (
    ActionTypeValidator,
    RollbackPlan,
    StrikeService,
)
from anif_platform.exceptions import ANIFError


# ── ActionTypeValidator ────────────────────────────────────────────────────


def test_validator_accepts_reroute_traffic() -> None:
    """ANIF-721 §4.1: reroute_traffic is a valid action type."""
    ActionTypeValidator.validate_action_type("reroute_traffic")  # must not raise


def test_validator_accepts_apply_qos() -> None:
    """ANIF-721 §4.1: apply_qos is a valid action type."""
    ActionTypeValidator.validate_action_type("apply_qos")


def test_validator_accepts_scale_bandwidth() -> None:
    """ANIF-721 §4.1: scale_bandwidth is a valid action type."""
    ActionTypeValidator.validate_action_type("scale_bandwidth")


def test_validator_accepts_isolate_segment() -> None:
    """ANIF-721 §4.1: isolate_segment is a valid action type."""
    ActionTypeValidator.validate_action_type("isolate_segment")


def test_validator_rejects_unknown_action_type() -> None:
    """ANIF-721 §4.4: unknown action type MUST be rejected."""
    with pytest.raises(ANIFError, match="invalid action type"):
        ActionTypeValidator.validate_action_type("delete_all_routes")


def test_validator_rejects_empty_string() -> None:
    """ANIF-721 §4.4: empty string is not a valid action type."""
    with pytest.raises(ANIFError):
        ActionTypeValidator.validate_action_type("")


def test_startup_validation_passes_with_correct_enum() -> None:
    """ANIF-721 §4.2: startup validation succeeds when all four action types are present."""
    ActionTypeValidator.validate_at_startup()  # must not raise


# ── RollbackPlan ───────────────────────────────────────────────────────────


def test_rollback_plan_requires_rollback_action_type() -> None:
    """ANIF-721 §5.3: rollback_action_type is required."""
    with pytest.raises(Exception):
        RollbackPlan(  # type: ignore[call-arg]
            rollback_target="segment-a",
            rollback_within_seconds=60,
            rollback_confirmed_at=datetime.now(UTC),
        )  # missing rollback_action_type


def test_rollback_plan_requires_non_empty_target() -> None:
    """ANIF-721 §5.3: rollback_target is required and non-empty."""
    with pytest.raises(Exception):
        RollbackPlan(
            rollback_action_type="reroute_traffic",
            rollback_target="",
            rollback_within_seconds=60,
            rollback_confirmed_at=datetime.now(UTC),
        )


def test_rollback_plan_valid() -> None:
    """ANIF-721 §5.3: a fully specified rollback plan is accepted."""
    plan = RollbackPlan(
        rollback_action_type="reroute_traffic",
        rollback_target="segment-a",
        rollback_within_seconds=60,
        rollback_confirmed_at=datetime.now(UTC),
    )
    assert plan.rollback_action_type == "reroute_traffic"


def test_rollback_plan_rejects_invalid_action_type() -> None:
    """ANIF-721 §5.3: rollback_action_type must be within the bounded enum."""
    with pytest.raises(Exception, match="invalid action type"):
        RollbackPlan(
            rollback_action_type="drop_all_routes",
            rollback_target="segment-a",
            rollback_within_seconds=60,
            rollback_confirmed_at=datetime.now(UTC),
        )


# ── StrikeService ──────────────────────────────────────────────────────────


def test_strike_service_record_strike_returns_record() -> None:
    """ANIF-721 §7.1: recording a strike returns the created record."""
    service = StrikeService()
    record = service.record_strike(
        agent_id=uuid.uuid4(),
        intent_id=uuid.uuid4(),
        reason="schema_validation_failure",
    )
    assert record.reason == "schema_validation_failure"


def test_strike_service_count_returns_zero_initially() -> None:
    """ANIF-721 §7.1: no strikes recorded yet."""
    service = StrikeService()
    agent_id = uuid.uuid4()
    assert service.count_strikes(agent_id=agent_id, window_minutes=60) == 0


def test_strike_service_count_after_recording() -> None:
    """ANIF-721 §7.1: count increases after recording a strike."""
    service = StrikeService()
    agent_id = uuid.uuid4()
    service.record_strike(agent_id=agent_id, intent_id=uuid.uuid4(), reason="test")
    assert service.count_strikes(agent_id=agent_id, window_minutes=60) == 1
