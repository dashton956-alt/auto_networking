"""RiskScore Pydantic model — ANIF-600 §4.4."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, Field, computed_field, model_validator


class SafetyDecision(str, Enum):
    allow = "allow"
    warn = "warn"
    block = "block"


class ThresholdApplied(BaseModel):
    """The threshold profile used for the allow/warn/block decision."""

    warn_threshold: Annotated[int, Field(ge=0, le=100)]
    block_threshold: Annotated[int, Field(ge=0, le=100)]
    profile: str


class RiskScore(BaseModel):
    """
    Risk and trust assessment output — ANIF-600 §4.4.

    `safety_decision` is derived programmatically from `risk_score` vs
    `threshold_applied`. It MUST NOT be set by the caller (ANIF-600 §5.4).
    """

    model_config = {"frozen": True}

    risk_score: Annotated[int, Field(ge=0, le=100)]
    trust_score: Annotated[int, Field(ge=0, le=100)]
    justification: list[str]
    threshold_applied: ThresholdApplied

    @model_validator(mode="before")
    @classmethod
    def reject_caller_supplied_safety_decision(cls, values: dict[str, Any]) -> dict[str, Any]:
        """ANIF-600 §5.4: safety_decision MUST NOT be set arbitrarily."""
        if "safety_decision" in values:
            raise ValueError(
                "safety_decision is derived programmatically from risk_score; "
                "callers MUST NOT supply it (ANIF-600 §5.4)"
            )
        return values

    @computed_field  # type: ignore[prop-decorator]
    @property
    def safety_decision(self) -> SafetyDecision:
        """
        Derive safety decision from risk_score vs thresholds.

        allow  — risk_score < warn_threshold
        warn   — warn_threshold <= risk_score < block_threshold
        block  — risk_score >= block_threshold
        """
        if self.risk_score >= self.threshold_applied.block_threshold:
            return SafetyDecision.block
        if self.risk_score >= self.threshold_applied.warn_threshold:
            return SafetyDecision.warn
        return SafetyDecision.allow
