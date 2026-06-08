"""ANIF-723 fairness enforcement controls — 3 independent blocking checks."""

from __future__ import annotations

import uuid
from typing import Literal

import structlog
from pydantic import BaseModel

log = structlog.get_logger(__name__)

# ANIF-723 §5.7: hardcoded — MUST NOT be lowered by configuration
_FRESHNESS_THRESHOLD: float = 0.7

# ANIF-723 §6.4: maximum divergence tolerance for apply_qos (1 DSCP class)
_QOS_MAX_DIVERGENCE: int = 1

_RESOURCE_ALLOCATION_ACTIONS = frozenset({"reroute_traffic", "apply_qos", "scale_bandwidth"})


class AffectedService(BaseModel):
    """A service affected by a proposed action, with its SLA declaration."""

    name: str
    availability_percent: float
    projected_allocation: float


class ReproducibilityInput(BaseModel):
    """Inputs for the reproducibility check (Tier 3 only)."""

    action_type: str
    shadow_available: bool
    ai_qos_class: int | None = None
    shadow_qos_class: int | None = None


class FairnessInput(BaseModel):
    """Inputs to all three fairness checks."""

    intent_id: uuid.UUID
    action_type: str
    affected_services: list[AffectedService]
    canonical_state_freshness_scores: list[float]
    agent_tier: int
    reproducibility: ReproducibilityInput | None = None


class FairnessOutcome(BaseModel):
    """Result of the three fairness checks — written to ethics audit record."""

    intent_id: uuid.UUID
    sla_floor_result: Literal["pass", "fail", "not_applicable"]
    sla_floor_failing_service: str | None
    sla_floor_deficit: float | None
    freshness_gate_result: Literal["pass", "fail"]
    freshness_gate_failing_score: float | None
    reproducibility_result: Literal[
        "pass", "fail", "shadow_used", "shadow_unavailable", "not_applicable"
    ]
    ai_output_divergence: float | None
    shadow_substitution_applied: bool
    blocked: bool
    route_to: Literal["manual_review", "approved"] | None


class FairnessChecker:
    """Runs ANIF-723 fairness checks independently — all three run even if one fails."""

    def check(self, inp: FairnessInput) -> FairnessOutcome:
        """Run all three checks independently. Any failure sets blocked=True."""
        sla_result, failing_svc, deficit = self._check_sla_floor(inp)
        freshness_result, failing_score = self._check_freshness(inp)
        repro_result, divergence, shadow_sub = self._check_reproducibility(inp)

        blocked = (
            sla_result == "fail"
            or freshness_result == "fail"
            or repro_result in ("fail", "shadow_unavailable")
        )

        return FairnessOutcome(
            intent_id=inp.intent_id,
            sla_floor_result=sla_result,
            sla_floor_failing_service=failing_svc,
            sla_floor_deficit=deficit,
            freshness_gate_result=freshness_result,
            freshness_gate_failing_score=failing_score,
            reproducibility_result=repro_result,
            ai_output_divergence=divergence,
            shadow_substitution_applied=shadow_sub,
            blocked=blocked,
            route_to="manual_review" if blocked else "approved",
        )

    def _check_sla_floor(
        self, inp: FairnessInput
    ) -> tuple[Literal["pass", "fail", "not_applicable"], str | None, float | None]:
        if (
            inp.action_type not in _RESOURCE_ALLOCATION_ACTIONS
            or len(inp.affected_services) < 2
        ):
            return "not_applicable", None, None

        for svc in inp.affected_services:
            sla_floor = svc.availability_percent * 0.80
            if svc.projected_allocation < sla_floor:
                deficit = sla_floor - svc.projected_allocation
                log.warning(
                    "fairness_sla_floor_fail",
                    service=svc.name,
                    floor=sla_floor,
                    projected=svc.projected_allocation,
                    deficit=deficit,
                    intent_id=str(inp.intent_id),
                )
                return "fail", svc.name, deficit

        return "pass", None, None

    def _check_freshness(
        self, inp: FairnessInput
    ) -> tuple[Literal["pass", "fail"], float | None]:
        for score in inp.canonical_state_freshness_scores:
            if score < _FRESHNESS_THRESHOLD:
                log.warning(
                    "fairness_freshness_gate_fail",
                    score=score,
                    threshold=_FRESHNESS_THRESHOLD,
                    intent_id=str(inp.intent_id),
                )
                return "fail", score
        return "pass", None

    def _check_reproducibility(
        self, inp: FairnessInput
    ) -> tuple[
        Literal["pass", "fail", "shadow_used", "shadow_unavailable", "not_applicable"],
        float | None,
        bool,
    ]:
        if inp.agent_tier < 3 or inp.reproducibility is None:
            return "not_applicable", None, False

        repro = inp.reproducibility

        if not repro.shadow_available or repro.shadow_qos_class is None:
            log.warning(
                "fairness_reproducibility_shadow_unavailable",
                intent_id=str(inp.intent_id),
            )
            return "shadow_unavailable", None, False

        if repro.action_type == "apply_qos" and repro.ai_qos_class is not None:
            divergence = float(abs(repro.ai_qos_class - repro.shadow_qos_class))
            if divergence > _QOS_MAX_DIVERGENCE:
                log.warning(
                    "fairness_reproducibility_divergence_exceeded",
                    divergence=divergence,
                    tolerance=_QOS_MAX_DIVERGENCE,
                    intent_id=str(inp.intent_id),
                )
                return "fail", divergence, False

        return "pass", 0.0, False
