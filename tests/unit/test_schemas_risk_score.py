"""Tests for RiskScore Pydantic model — ANIF-600 §4.4."""

import pytest
from pydantic import ValidationError

from anif_platform.schemas.risk_score import RiskScore, SafetyDecision, ThresholdApplied

DEFAULT_THRESHOLD = ThresholdApplied(warn_threshold=40, block_threshold=70, profile="default")


class TestThresholdApplied:
    def test_valid_threshold(self) -> None:
        t = ThresholdApplied(warn_threshold=40, block_threshold=70, profile="default")
        assert t.warn_threshold == 40

    def test_warn_threshold_required(self) -> None:
        with pytest.raises(ValidationError):
            ThresholdApplied(block_threshold=70, profile="default")  # type: ignore[call-arg]

    def test_threshold_out_of_range_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ThresholdApplied(warn_threshold=-1, block_threshold=70, profile="default")

    def test_threshold_above_100_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ThresholdApplied(warn_threshold=40, block_threshold=101, profile="default")


class TestRiskScore:
    def test_allow_decision_when_below_warn(self) -> None:
        """safety_decision MUST be derived from risk_score vs thresholds — ANIF-600 §5.4."""
        rs = RiskScore(
            risk_score=39,
            trust_score=80,
            justification=["low risk"],
            threshold_applied=DEFAULT_THRESHOLD,
        )
        assert rs.safety_decision == SafetyDecision.allow

    def test_warn_decision_at_warn_threshold(self) -> None:
        rs = RiskScore(
            risk_score=40,
            trust_score=70,
            justification=["prod env: +30", "policy fail: +10"],
            threshold_applied=DEFAULT_THRESHOLD,
        )
        assert rs.safety_decision == SafetyDecision.warn

    def test_warn_decision_between_thresholds(self) -> None:
        rs = RiskScore(
            risk_score=55,
            trust_score=60,
            justification=["prod env: +30"],
            threshold_applied=DEFAULT_THRESHOLD,
        )
        assert rs.safety_decision == SafetyDecision.warn

    def test_block_decision_at_block_threshold(self) -> None:
        rs = RiskScore(
            risk_score=70,
            trust_score=20,
            justification=["prod env: +30", "isolate_segment: +25"],
            threshold_applied=DEFAULT_THRESHOLD,
        )
        assert rs.safety_decision == SafetyDecision.block

    def test_risk_score_above_100_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RiskScore(
                risk_score=101,
                trust_score=50,
                justification=[],
                threshold_applied=DEFAULT_THRESHOLD,
            )

    def test_risk_score_below_0_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RiskScore(
                risk_score=-1,
                trust_score=50,
                justification=[],
                threshold_applied=DEFAULT_THRESHOLD,
            )

    def test_trust_score_range_enforced(self) -> None:
        with pytest.raises(ValidationError):
            RiskScore(
                risk_score=30,
                trust_score=101,
                justification=[],
                threshold_applied=DEFAULT_THRESHOLD,
            )

    def test_arbitrary_safety_decision_rejected(self) -> None:
        """ANIF-600 §5.4: safety_decision MUST NOT be set arbitrarily."""
        with pytest.raises((ValidationError, TypeError)):
            RiskScore(
                risk_score=30,
                trust_score=80,
                safety_decision="allow",  # type: ignore[call-arg]
                justification=[],
                threshold_applied=DEFAULT_THRESHOLD,
            )

    def test_justification_required(self) -> None:
        with pytest.raises(ValidationError):
            RiskScore(
                risk_score=30,
                trust_score=80,
                threshold_applied=DEFAULT_THRESHOLD,
            )  # type: ignore[call-arg]

    def test_strict_profile_thresholds(self) -> None:
        strict = ThresholdApplied(warn_threshold=25, block_threshold=50, profile="strict")
        rs = RiskScore(
            risk_score=30,
            trust_score=70,
            justification=["staging env: +10"],
            threshold_applied=strict,
        )
        assert rs.safety_decision == SafetyDecision.warn
