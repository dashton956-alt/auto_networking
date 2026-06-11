"""Unit tests for ModeSelector — ANIF-902."""

from __future__ import annotations

from anif_platform.council.mode_selector import (
    DeliberationModel,
    ModeSelector,
    ModeSelectorInput,
    ModeSelectorResult,
)


def _inp(**kwargs) -> ModeSelectorInput:
    defaults = dict(
        reversibility="reversible",
        risk_score=30,
        ethics_flag="absent",
        time_pressure="normal",
        novelty="precedented",
        strike_history="none",
    )
    defaults.update(kwargs)
    return ModeSelectorInput(**defaults)


class TestDecisionMatrix:
    def test_rule1_ethics_flag_present_returns_consensus(self) -> None:
        """CR-902-01/02: Rule 1 — ethics_flag=present → consensus."""
        result = ModeSelector.select(_inp(ethics_flag="present"))
        assert result.mode_selected == DeliberationModel.consensus
        assert result.rule_matched == 1

    def test_rule2_active_strike_returns_adversarial(self) -> None:
        """CR-902-01/02: Rule 2 — active_strike → adversarial."""
        result = ModeSelector.select(_inp(strike_history="active_strike"))
        assert result.mode_selected == DeliberationModel.adversarial
        assert result.rule_matched == 2

    def test_rule3_irreversible_high_risk_returns_consensus(self) -> None:
        """CR-902-01: Rule 3 — irreversible AND risk_score >= 70 → consensus."""
        result = ModeSelector.select(_inp(reversibility="irreversible", risk_score=70))
        assert result.mode_selected == DeliberationModel.consensus
        assert result.rule_matched == 3

    def test_rule3_irreversible_risk_below_threshold_skips(self) -> None:
        """Rule 3 does NOT apply when risk_score < 70."""
        result = ModeSelector.select(_inp(reversibility="irreversible", risk_score=69))
        assert result.rule_matched != 3

    def test_rule4_novel_medium_risk_returns_adversarial(self) -> None:
        """CR-902-01: Rule 4 — novel AND risk_score >= 50 → adversarial."""
        result = ModeSelector.select(_inp(novelty="novel", risk_score=50))
        assert result.mode_selected == DeliberationModel.adversarial
        assert result.rule_matched == 4

    def test_rule4_novel_risk_below_threshold_skips(self) -> None:
        """Rule 4 does NOT apply when risk_score < 50."""
        result = ModeSelector.select(_inp(novelty="novel", risk_score=49))
        assert result.rule_matched != 4

    def test_rule5_critical_reversible_returns_majority(self) -> None:
        """CR-902-01: Rule 5 — critical time_pressure AND reversible → majority."""
        result = ModeSelector.select(_inp(time_pressure="critical", reversibility="reversible"))
        assert result.mode_selected == DeliberationModel.majority
        assert result.rule_matched == 5

    def test_rule5_critical_but_irreversible_skips(self) -> None:
        """Rule 5 requires BOTH critical AND reversible."""
        result = ModeSelector.select(
            _inp(time_pressure="critical", reversibility="irreversible", risk_score=50)
        )
        assert result.rule_matched != 5

    def test_rule6_high_risk_score_returns_weighted(self) -> None:
        """CR-902-01: Rule 6 — risk_score >= 80 → weighted."""
        result = ModeSelector.select(_inp(risk_score=80))
        assert result.mode_selected == DeliberationModel.weighted
        assert result.rule_matched == 6

    def test_rule7_historical_strike_returns_weighted(self) -> None:
        """CR-902-01: Rule 7 — historical_strike → weighted."""
        result = ModeSelector.select(_inp(strike_history="historical_strike"))
        assert result.mode_selected == DeliberationModel.weighted
        assert result.rule_matched == 7

    def test_rule8_irreversible_returns_weighted(self) -> None:
        """CR-902-01: Rule 8 — irreversible → weighted."""
        result = ModeSelector.select(_inp(reversibility="irreversible", risk_score=30))
        assert result.mode_selected == DeliberationModel.weighted
        assert result.rule_matched == 8

    def test_rule9_default_returns_majority(self) -> None:
        """CR-902-01: Rule 9 — all other cases → majority."""
        result = ModeSelector.select(_inp())
        assert result.mode_selected == DeliberationModel.majority
        assert result.rule_matched == 9

    def test_rule1_takes_priority_over_rule2(self) -> None:
        """CR-902-01: ethics_flag beats active_strike (rule 1 > rule 2)."""
        result = ModeSelector.select(_inp(ethics_flag="present", strike_history="active_strike"))
        assert result.rule_matched == 1
        assert result.mode_selected == DeliberationModel.consensus


class TestDeterminism:
    def test_same_inputs_produce_same_output(self) -> None:
        """CR-902-02: Mode Selector MUST be deterministic."""
        inp = _inp(risk_score=55, novelty="novel")
        results = [ModeSelector.select(inp) for _ in range(10)]
        modes = {r.mode_selected for r in results}
        rules = {r.rule_matched for r in results}
        assert len(modes) == 1
        assert len(rules) == 1


class TestLoggingFields:
    def test_result_contains_all_six_input_factors(self) -> None:
        """CR-902-03: All 6 input factors MUST be recorded."""
        inp = _inp(risk_score=60, ethics_flag="absent", novelty="novel")
        result = ModeSelector.select(inp)
        assert result.input_reversibility == inp.reversibility
        assert result.input_risk_score == inp.risk_score
        assert result.input_ethics_flag == inp.ethics_flag
        assert result.input_time_pressure == inp.time_pressure
        assert result.input_novelty == inp.novelty
        assert result.input_strike_history == inp.strike_history

    def test_result_contains_timestamp(self) -> None:
        """CR-902-03: mode_selector_timestamp MUST be populated."""
        result = ModeSelector.select(_inp())
        assert result.mode_selector_timestamp is not None

    def test_result_is_a_mode_selector_result(self) -> None:
        """ModeSelector.select() returns a ModeSelectorResult."""
        result = ModeSelector.select(_inp())
        assert isinstance(result, ModeSelectorResult)
