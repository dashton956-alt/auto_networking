"""AuditRecord Pydantic model — ANIF-107, ANIF-600 §4.5, ANIF-724."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum, StrEnum
from typing import Annotated, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class AuditStage(StrEnum):
    """Pipeline stages that produce audit records — ANIF-107 §4.1.2."""

    validate = "validate"
    policy = "policy"
    risk = "risk"
    decision = "decision"
    governance = "governance"
    execute = "execute"
    rollback = "rollback"
    agent_lifecycle = "agent_lifecycle"


class AuditOutcome(StrEnum):
    """Stage outcome values — ANIF-107 §4.2."""

    success = "success"
    failure = "failure"
    escalated = "escalated"
    blocked = "blocked"


class GovernanceMode(StrEnum):
    auto = "auto"
    manual_review = "manual_review"
    block = "block"
    council_review = "council_review"


class PostVerificationOutcome(StrEnum):
    pass_ = "pass"
    fail = "fail"
    pending = "pending"

    @classmethod
    def _missing_(cls, value: object) -> PostVerificationOutcome | None:
        if value == "pass":
            return cls.pass_
        return None


class RollbackOutcome(StrEnum):
    success = "success"
    failure = "failure"


class AgentTier(int, Enum):
    tier_0 = 0
    tier_1 = 1
    tier_2 = 2
    tier_3 = 3


class AgentTrustLevel(StrEnum):
    SYSTEM = "SYSTEM"
    VERIFIED = "VERIFIED"
    PROVISIONAL = "PROVISIONAL"
    UNTRUSTED = "UNTRUSTED"


class HarmClass(StrEnum):
    service = "service"
    infrastructure = "infrastructure"
    cascading = "cascading"
    none = "none"


class HarmGateOutcome(StrEnum):
    pass_ = "pass"
    manual_review_forced = "manual_review_forced"
    council_review_forced = "council_review_forced"


class FairnessResult(StrEnum):
    pass_ = "pass"
    fail = "fail"
    not_applicable = "not_applicable"


class ReproducibilityResult(StrEnum):
    pass_ = "pass"
    fail = "fail"
    shadow_used = "shadow_used"
    shadow_unavailable = "shadow_unavailable"


class LLMValidationResult(StrEnum):
    pass_ = "pass"
    fail = "fail"
    skipped = "skipped"
    suppressed = "suppressed"


class ReasoningStep(BaseModel):
    """A single step in the reasoning chain — schemas/audit_record_schema.yml."""

    step: int
    description: str
    decision: str
    rationale: str | None = None


# Stages that MUST have a non-empty reasoning_chain (ANIF-107 §4.2.2)
_REASONING_REQUIRED_STAGES = {AuditStage.decision, AuditStage.governance}


class AuditRecord(BaseModel):
    """
    Immutable audit record written by each pipeline stage — ANIF-107 §4.2.

    Base fields are required for all stages. Stage-specific additional fields
    (ANIF-107 §4.2.1) and ethics fields (ANIF-724 §4) are optional here;
    their enforcement per stage is the responsibility of the calling module.

    Hash chain fields (`record_hash`, `prev_hash`, `chain_id`) are populated
    by AuditWriter — callers MUST NOT set them.
    """

    # ── Base required fields (ANIF-107 §4.2) ─────────────────────────────
    record_id: UUID = Field(default_factory=uuid4)
    intent_id: UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    stage: AuditStage
    operator_id: str | None = None
    input_summary: dict[str, Any]
    output_summary: dict[str, Any]
    outcome: AuditOutcome
    reasoning_chain: list[ReasoningStep] = Field(default_factory=list)
    duration_ms: Annotated[int, Field(ge=0)]

    # ── Hash chain fields (set by AuditWriter only) ───────────────────────
    record_hash: str | None = None
    prev_hash: str | None = None
    chain_id: UUID | None = None

    # ── Stage-specific additional fields (ANIF-107 §4.2.1) ───────────────
    # governance stage
    governance_mode: GovernanceMode | None = None
    ticket_id: UUID | None = None
    applied_policies: list[str] | None = None

    # execute stage
    action_type: str | None = None
    target: str | None = None
    rollback_available: bool | None = None
    post_verification_outcome: PostVerificationOutcome | None = None

    # rollback stage
    original_execute_record_id: UUID | None = None
    rollback_reason: str | None = None
    rollback_outcome: RollbackOutcome | None = None

    # policy stage
    policies_evaluated: list[str] | None = None
    policies_violated: list[str] | None = None

    # risk stage
    risk_score: Annotated[int, Field(ge=0, le=100)] | None = None
    risk_factors: list[str] | None = None

    # ── Ethics extension fields (ANIF-724 §4) ────────────────────────────
    # Agent identity
    agent_id: UUID | None = None
    agent_version: str | None = None
    agent_tier: AgentTier | None = None
    agent_trust_level: AgentTrustLevel | None = None

    # Determinism
    deterministic: bool | None = None
    llm_used: bool | None = None
    llm_model_id: str | None = None
    shadow_used_as_substitution: bool | None = None

    # LLM audit
    llm_prompt_hash: str | None = None
    llm_prompt_length_tokens: int | None = None
    llm_confidence_score: float | None = None
    llm_validation_stage1: LLMValidationResult | None = None
    llm_validation_stage2: LLMValidationResult | None = None
    llm_validation_stage3: LLMValidationResult | None = None
    llm_validation_stage4: LLMValidationResult | None = None

    # Fairness audit
    fairness_check_result: FairnessResult | None = None
    fairness_freshness_gate_result: LLMValidationResult | None = None
    reproducibility_check_result: ReproducibilityResult | None = None
    ai_shadow_divergence: float | None = None

    # Harm classification
    harm_class: HarmClass | None = None
    harm_severity_score: Annotated[int, Field(ge=0, le=100)] | None = None
    blast_radius_segment_count: int | None = None
    harm_gate_outcome: HarmGateOutcome | None = None
    simulation_completed: bool | None = None

    # Accountability chain
    accountability_designer_id: str | None = None
    accountability_deployer_id: str | None = None
    accountability_operator_id: str | None = None
    accountability_approver_id: str | None = None

    # Ethics gate results
    ethics_gates_passed: list[str] | None = None
    ethics_gates_failed: list[str] | None = None
    ethics_gates_skipped: list[str] | None = None

    @field_validator("timestamp")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        """ANIF-107 §4.2.2: timestamp MUST be UTC."""
        if v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v.astimezone(UTC)

    @model_validator(mode="after")
    def enforce_reasoning_chain_for_critical_stages(self) -> AuditRecord:
        """ANIF-107 §4.2.2: reasoning_chain MUST NOT be empty for decision and governance."""
        if self.stage in _REASONING_REQUIRED_STAGES and len(self.reasoning_chain) == 0:
            raise ValueError(
                f"reasoning_chain MUST NOT be empty for stage '{self.stage.value}' "
                "(ANIF-107 §4.2.2)"
            )
        return self
