"""Unit tests for TierBoundaryChecker — ANIF-802, ANIF-843 §6."""
from __future__ import annotations

import pytest

from anif_platform.agents.tier_boundary import TierBoundaryChecker


@pytest.fixture
def checker() -> TierBoundaryChecker:
    return TierBoundaryChecker()


def test_tier_0_can_read_canonical_state(checker: TierBoundaryChecker) -> None:
    """ANIF-843 §6.2: canonical_state_read requires Tier 0 minimum."""
    assert checker.check(agent_tier=0, endpoint_category="canonical_state_read") is True


def test_tier_1_can_call_policy_evaluation(checker: TierBoundaryChecker) -> None:
    """ANIF-843 §6.2: policy_evaluation requires Tier 1 minimum."""
    assert checker.check(agent_tier=1, endpoint_category="policy_evaluation") is True


def test_tier_0_cannot_call_policy_evaluation(checker: TierBoundaryChecker) -> None:
    """Tier 0 is below the Tier 1 minimum for policy_evaluation."""
    assert checker.check(agent_tier=0, endpoint_category="policy_evaluation") is False


def test_tier_2_can_call_risk_scoring(checker: TierBoundaryChecker) -> None:
    assert checker.check(agent_tier=2, endpoint_category="risk_scoring") is True


def test_tier_1_cannot_call_risk_scoring(checker: TierBoundaryChecker) -> None:
    assert checker.check(agent_tier=1, endpoint_category="risk_scoring") is False


def test_tier_3_can_call_execution_api(checker: TierBoundaryChecker) -> None:
    assert checker.check(agent_tier=3, endpoint_category="execution_api") is True


def test_tier_2_cannot_call_execution_api(checker: TierBoundaryChecker) -> None:
    """ANIF-802: Tier 2 MUST NOT call execution endpoints."""
    assert checker.check(agent_tier=2, endpoint_category="execution_api") is False


def test_tier_1_cannot_call_execution_api(checker: TierBoundaryChecker) -> None:
    """ANIF-802: Tier 1 MUST NOT call execution endpoints."""
    assert checker.check(agent_tier=1, endpoint_category="execution_api") is False


def test_higher_tier_satisfies_lower_requirement(checker: TierBoundaryChecker) -> None:
    """Tier 3 agents can call policy evaluation (requires Tier 1 minimum)."""
    assert checker.check(agent_tier=3, endpoint_category="policy_evaluation") is True


def test_unknown_endpoint_category_defaults_to_tier_0_requirement(
    checker: TierBoundaryChecker,
) -> None:
    """Unknown endpoint categories require Tier 0 minimum (safe default)."""
    assert checker.check(agent_tier=0, endpoint_category="unknown_category") is True
