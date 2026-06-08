"""Tests for ANIF-723 fairness enforcement controls."""

from __future__ import annotations

import uuid

import pytest

from anif_platform.ethics.fairness import (
    AffectedService,
    FairnessChecker,
    FairnessInput,
    ReproducibilityInput,
)


def _base_input(
    *,
    action_type: str = "apply_qos",
    services: list[AffectedService] | None = None,
    freshness_scores: list[float] | None = None,
    agent_tier: int = 2,
    repro: ReproducibilityInput | None = None,
) -> FairnessInput:
    return FairnessInput(
        intent_id=uuid.uuid4(),
        action_type=action_type,
        affected_services=services or [],
        canonical_state_freshness_scores=freshness_scores or [0.9],
        agent_tier=agent_tier,
        reproducibility=repro,
    )


# ── Check 1: SLA Floor ─────────────────────────────────────────────────────


def test_sla_floor_not_applicable_for_isolate_segment() -> None:
    """ANIF-723 §4.2: SLA floor check only applies to multi-service resource allocation."""
    result = FairnessChecker().check(_base_input(action_type="isolate_segment"))
    assert result.sla_floor_result == "not_applicable"


def test_sla_floor_not_applicable_when_fewer_than_two_services() -> None:
    """ANIF-723 §4.2: applies only when two or more services with declared SLA tiers."""
    service = AffectedService(name="svc-a", availability_percent=99.0, projected_allocation=95.0)
    result = FairnessChecker().check(
        _base_input(action_type="apply_qos", services=[service])
    )
    assert result.sla_floor_result == "not_applicable"


def test_sla_floor_pass_when_all_above_floor() -> None:
    """ANIF-723 §4.4: all services above SLA floor → pass."""
    services = [
        AffectedService(name="svc-a", availability_percent=99.0, projected_allocation=82.0),
        AffectedService(name="svc-b", availability_percent=95.0, projected_allocation=78.0),
    ]
    # sla_floor(svc-a) = 99 * 0.8 = 79.2; 82 > 79.2 ✓
    # sla_floor(svc-b) = 95 * 0.8 = 76.0; 78 > 76.0 ✓
    result = FairnessChecker().check(_base_input(action_type="apply_qos", services=services))
    assert result.sla_floor_result == "pass"
    assert result.blocked is False


def test_sla_floor_fail_when_service_below_floor() -> None:
    """ANIF-723 §4.5: any service below SLA floor → fail + manual_review."""
    services = [
        AffectedService(name="svc-a", availability_percent=99.0, projected_allocation=70.0),
        AffectedService(name="svc-b", availability_percent=95.0, projected_allocation=90.0),
    ]
    # svc-a sla_floor = 99 * 0.8 = 79.2; 70 < 79.2 → FAIL
    result = FairnessChecker().check(_base_input(action_type="apply_qos", services=services))
    assert result.sla_floor_result == "fail"
    assert result.blocked is True
    assert result.route_to == "manual_review"


# ── Check 2: Ground Truth Freshness ───────────────────────────────────────


def test_freshness_gate_pass_when_all_above_threshold() -> None:
    """ANIF-723 §5.4: all sources with freshness ≥ 0.7 → pass."""
    result = FairnessChecker().check(_base_input(freshness_scores=[0.9, 0.8, 0.75]))
    assert result.freshness_gate_result == "pass"


def test_freshness_gate_fail_when_any_below_threshold() -> None:
    """ANIF-723 §5.5: any source below 0.7 → fail + manual_review."""
    result = FairnessChecker().check(_base_input(freshness_scores=[0.9, 0.6]))
    assert result.freshness_gate_result == "fail"
    assert result.blocked is True


def test_freshness_threshold_is_not_lowerable() -> None:
    """ANIF-723 §5.7: threshold must be 0.7 — verify it is hardcoded."""
    from anif_platform.ethics.fairness import _FRESHNESS_THRESHOLD

    assert _FRESHNESS_THRESHOLD == 0.7


# ── Check 3: Reproducibility ───────────────────────────────────────────────


def test_reproducibility_not_checked_for_tier2() -> None:
    """ANIF-723 §6.2: reproducibility check MUST run for Tier 3 only."""
    result = FairnessChecker().check(_base_input(agent_tier=2))
    assert result.reproducibility_result == "not_applicable"


def test_reproducibility_pass_within_tolerance() -> None:
    """ANIF-723 §6.4: divergence within tolerance → pass."""
    repro = ReproducibilityInput(
        action_type="apply_qos",
        ai_qos_class=3,
        shadow_qos_class=3,
        shadow_available=True,
    )
    result = FairnessChecker().check(_base_input(agent_tier=3, repro=repro))
    assert result.reproducibility_result == "pass"


def test_reproducibility_fail_shadow_unavailable() -> None:
    """ANIF-723 §6.5: shadow unavailable → block, manual_review."""
    repro = ReproducibilityInput(
        action_type="apply_qos",
        ai_qos_class=3,
        shadow_qos_class=None,
        shadow_available=False,
    )
    result = FairnessChecker().check(_base_input(agent_tier=3, repro=repro))
    assert result.reproducibility_result == "shadow_unavailable"
    assert result.blocked is True


def test_reproducibility_divergence_exceeds_tolerance() -> None:
    """ANIF-723 §6.5: divergence beyond tolerance → suppress AI output."""
    repro = ReproducibilityInput(
        action_type="apply_qos",
        ai_qos_class=1,
        shadow_qos_class=5,
        shadow_available=True,
    )
    result = FairnessChecker().check(_base_input(agent_tier=3, repro=repro))
    assert result.reproducibility_result in ("fail", "shadow_used")
    assert result.blocked is True
