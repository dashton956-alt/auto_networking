"""ANIF-722 LLM output validation — 4-stage sequential blocking pipeline."""

from __future__ import annotations

import uuid
from typing import Literal

import structlog
from pydantic import BaseModel

log = structlog.get_logger(__name__)

# ANIF-722 §7.2: confidence thresholds by agent tier
_CONFIDENCE_THRESHOLDS: dict[int, float] = {2: 0.65, 3: 0.80}
_MAX_CANONICAL_STATE_AGE_SECONDS = 300  # 5 minutes — ANIF-722 §6.2


class Stage4SecurityIncidentError(Exception):
    """Raised when prompt hash mismatch is detected — ANIF-722 §8.4.

    This is a security incident, not a validation failure. MUST NOT be caught
    and routed to manual_review. The pipeline halts and the security team is notified.
    """

    def __init__(self, agent_id: uuid.UUID, intent_id: uuid.UUID) -> None:
        super().__init__(
            f"SEVERITY 1 SECURITY INCIDENT: prompt hash mismatch "
            f"agent_id={agent_id} intent_id={intent_id} (ANIF-722 §8)"
        )
        self.agent_id = agent_id
        self.intent_id = intent_id


class LLMValidationInput(BaseModel):
    """Inputs to the 4-stage LLM output validation pipeline."""

    agent_id: uuid.UUID
    intent_id: uuid.UUID
    agent_tier: int

    # Stage 1
    output_schema_valid: bool

    # Stage 2
    factual_claims_consistent: bool
    canonical_state_age_seconds: int

    # Stage 3
    confidence_score: float

    # Stage 4
    prompt_hash_recorded: str
    prompt_hash_submitted: str


class LLMValidationOutcome(BaseModel):
    """Result of the 4-stage validation pipeline — written to ethics audit record."""

    agent_id: uuid.UUID
    intent_id: uuid.UUID
    stage1: Literal["pass", "fail"]
    stage2: Literal["pass", "fail", "skipped"]
    stage3: Literal["pass", "suppressed"]
    stage4: Literal["pass", "fail"]
    blocked: bool
    route_to: Literal["manual_review", "approved"] | None
    strike_incremented: bool
    canonical_state_age_seconds: int
    confidence_score: float


class LLMOutputValidator:
    """Runs the ANIF-722 4-stage validation pipeline sequentially.

    Stages MUST run in order. Stage 4 failure raises Stage4SecurityIncidentError
    rather than returning a blocked result — it is a security incident.
    """

    def validate(self, inp: LLMValidationInput) -> LLMValidationOutcome:
        """Run all four stages in order. Returns outcome or raises Stage4SecurityIncidentError."""
        # Stage 1: Schema check
        if not inp.output_schema_valid:
            log.warning(
                "llm_validation_stage1_fail",
                agent_id=str(inp.agent_id),
                intent_id=str(inp.intent_id),
            )
            return LLMValidationOutcome(
                agent_id=inp.agent_id,
                intent_id=inp.intent_id,
                stage1="fail",
                stage2="skipped",
                stage3="suppressed",
                stage4="fail",
                blocked=True,
                route_to="manual_review",
                strike_incremented=True,
                canonical_state_age_seconds=inp.canonical_state_age_seconds,
                confidence_score=inp.confidence_score,
            )

        # Stage 2: Hallucination check — stale canonical state blocks first
        if inp.canonical_state_age_seconds > _MAX_CANONICAL_STATE_AGE_SECONDS:
            log.warning(
                "llm_validation_stage2_stale_canonical_state",
                age_seconds=inp.canonical_state_age_seconds,
                max_age=_MAX_CANONICAL_STATE_AGE_SECONDS,
                agent_id=str(inp.agent_id),
            )
            return LLMValidationOutcome(
                agent_id=inp.agent_id,
                intent_id=inp.intent_id,
                stage1="pass",
                stage2="fail",
                stage3="suppressed",
                stage4="fail",
                blocked=True,
                route_to="manual_review",
                strike_incremented=True,
                canonical_state_age_seconds=inp.canonical_state_age_seconds,
                confidence_score=inp.confidence_score,
            )

        if not inp.factual_claims_consistent:
            log.warning(
                "llm_validation_stage2_hallucination",
                agent_id=str(inp.agent_id),
                intent_id=str(inp.intent_id),
            )
            return LLMValidationOutcome(
                agent_id=inp.agent_id,
                intent_id=inp.intent_id,
                stage1="pass",
                stage2="fail",
                stage3="suppressed",
                stage4="fail",
                blocked=True,
                route_to="manual_review",
                strike_incremented=True,
                canonical_state_age_seconds=inp.canonical_state_age_seconds,
                confidence_score=inp.confidence_score,
            )

        # Stage 3: Confidence check — suppressed output is not a strike
        threshold = _CONFIDENCE_THRESHOLDS.get(inp.agent_tier, 0.65)
        if inp.confidence_score < threshold:
            log.info(
                "llm_validation_stage3_suppressed",
                confidence=inp.confidence_score,
                threshold=threshold,
                agent_tier=inp.agent_tier,
            )
            return LLMValidationOutcome(
                agent_id=inp.agent_id,
                intent_id=inp.intent_id,
                stage1="pass",
                stage2="pass",
                stage3="suppressed",
                stage4="fail",
                blocked=True,
                route_to="manual_review",
                strike_incremented=False,
                canonical_state_age_seconds=inp.canonical_state_age_seconds,
                confidence_score=inp.confidence_score,
            )

        # Stage 4: Prompt integrity hash — SECURITY INCIDENT on mismatch
        if inp.prompt_hash_submitted != inp.prompt_hash_recorded:
            log.critical(
                "llm_validation_stage4_hash_mismatch_SECURITY_INCIDENT",
                agent_id=str(inp.agent_id),
                intent_id=str(inp.intent_id),
                recorded_hash=inp.prompt_hash_recorded,
                submitted_hash=inp.prompt_hash_submitted,
            )
            raise Stage4SecurityIncidentError(
                agent_id=inp.agent_id,
                intent_id=inp.intent_id,
            )

        return LLMValidationOutcome(
            agent_id=inp.agent_id,
            intent_id=inp.intent_id,
            stage1="pass",
            stage2="pass",
            stage3="pass",
            stage4="pass",
            blocked=False,
            route_to="approved",
            strike_incremented=False,
            canonical_state_age_seconds=inp.canonical_state_age_seconds,
            confidence_score=inp.confidence_score,
        )
