"""Council Mode Selector — ANIF-902.

Deterministic 9-rule decision matrix. No LLM inference.
Same input always produces the same output (CR-902-02).
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class DeliberationModel(StrEnum):
    consensus = "consensus"
    adversarial = "adversarial"
    weighted = "weighted"
    majority = "majority"


class ModeSelectorInput(BaseModel):
    reversibility: Literal["reversible", "partially_reversible", "irreversible"]
    risk_score: int  # 0–100
    ethics_flag: Literal["present", "absent"]
    time_pressure: Literal["critical", "elevated", "normal"]
    novelty: Literal["novel", "precedented"]
    strike_history: Literal["active_strike", "historical_strike", "none"]


class ModeSelectorResult(BaseModel):
    # All six input factors — CR-902-03
    input_reversibility: str
    input_risk_score: int
    input_ethics_flag: str
    input_time_pressure: str
    input_novelty: str
    input_strike_history: str

    rule_matched: int
    mode_selected: DeliberationModel
    mode_selector_timestamp: datetime


# Time limits in seconds per deliberation model — ANIF-904 §5
TIME_LIMITS: dict[DeliberationModel, int] = {
    DeliberationModel.majority: 15 * 60,
    DeliberationModel.weighted: 15 * 60,
    DeliberationModel.consensus: 30 * 60,
    DeliberationModel.adversarial: 45 * 60,
}


class ModeSelector:
    """Deterministic mode selector implementing ANIF-902 §4 decision matrix."""

    @staticmethod
    def select(inp: ModeSelectorInput) -> ModeSelectorResult:
        """Evaluate all six factors; return the first matching rule. CR-902-01/02."""
        mode, rule = ModeSelector._evaluate(inp)
        return ModeSelectorResult(
            input_reversibility=inp.reversibility,
            input_risk_score=inp.risk_score,
            input_ethics_flag=inp.ethics_flag,
            input_time_pressure=inp.time_pressure,
            input_novelty=inp.novelty,
            input_strike_history=inp.strike_history,
            rule_matched=rule,
            mode_selected=mode,
            mode_selector_timestamp=datetime.now(UTC),
        )

    @staticmethod
    def _evaluate(inp: ModeSelectorInput) -> tuple[DeliberationModel, int]:
        # Rule 1: ethics_flag = present → consensus
        if inp.ethics_flag == "present":
            return DeliberationModel.consensus, 1

        # Rule 2: active_strike → adversarial
        if inp.strike_history == "active_strike":
            return DeliberationModel.adversarial, 2

        # Rule 3: irreversible AND risk_score >= 70 → consensus
        if inp.reversibility == "irreversible" and inp.risk_score >= 70:
            return DeliberationModel.consensus, 3

        # Rule 4: novel AND risk_score >= 50 → adversarial
        if inp.novelty == "novel" and inp.risk_score >= 50:
            return DeliberationModel.adversarial, 4

        # Rule 5: critical time_pressure AND reversible → majority
        if inp.time_pressure == "critical" and inp.reversibility == "reversible":
            return DeliberationModel.majority, 5

        # Rule 6: risk_score >= 80 → weighted
        if inp.risk_score >= 80:
            return DeliberationModel.weighted, 6

        # Rule 7: historical_strike → weighted
        if inp.strike_history == "historical_strike":
            return DeliberationModel.weighted, 7

        # Rule 8: irreversible → weighted
        if inp.reversibility == "irreversible":
            return DeliberationModel.weighted, 8

        # Rule 9: all other cases → majority
        return DeliberationModel.majority, 9
