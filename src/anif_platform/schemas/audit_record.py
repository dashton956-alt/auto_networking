"""AuditRecord Pydantic model — ANIF-107, ANIF-600 §4.5, ANIF-724."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Annotated, Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class AuditStage(str, Enum):
    """Pipeline stages that produce audit records — ANIF-107 §4.1.2."""

    validate = "validate"
    policy = "policy"
    risk = "risk"
    decision = "decision"
    governance = "governance"
    execute = "execute"
    rollback = "rollback"


class AuditOutcome(str, Enum):
    """Stage outcome values — ANIF-107 §4.2."""

    success = "success"
    failure = "failure"
    escalated = "escalated"
    blocked = "blocked"


class GovernanceMode(str, Enum):
    auto = "auto"
    manual_review = "manual_review"
    block = "block"
    council_review = "council_review"


class PostVerificationOutcome(str, Enum):
    pass_ = "pass"
    fail = "fail"
    pending = "pending"

    @classmethod
    def _missing_(cls, value: object) -> Optional[PostVerificationOutcome]:
        if value == "pass":
            return cls.pass_
        return None


class RollbackOutcome(str, Enum):
    success = "success"
    failure = "failure"


class AgentTier(int, Enum):
    tier_0 = 0
    tier_1 = 1
    tier_2 = 2
    tier_3 = 3


class AgentTrustLevel(str, Enum):
    SYSTEM = "SYSTEM"
    VERIFIED = "VERIFIED"
    PROVISIONAL = "PROVISIONAL"
    UNTRUSTED = "UNTRUSTED"


class HarmClass(str, Enum):
    service = "service"
    infrastructure = "infrastructure"
    cascading = "cascading"
    none = "none"


class HarmGateOutcome(str, Enum):
    pass_ = "pass"
    manual_review_forced = "manual_review_forced"
    council_review_forced = "council_review_forced"


class FairnessResult(str, Enum):
    pass_ = "pass"
    fail = "fail"
    not_applicable = "not_applicable"


class ReproducibilityResult(str, Enum):
    pass_ = "pass"
    fail = "fail"
    shadow_used = "shadow_used"
    shadow_unavailable = "shadow_unavailable"


class LLMValidationResult(str, Enum):
    pass_ = "pass"
    fail = "fail"
    skipped = "skipped"
    suppressed = "suppressed"


class ReasoningStep(BaseModel):
    """A single step in the reasoning chain — schemas/audit_record_schema.yml."""

    step: int
    description: str
    decision: str
    rationale: Optional[str] = None


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
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    stage: AuditStage
    operator_id: Optional[str] = None
    input_summary: dict[str, Any]
    output_summary: dict[str, Any]
    outcome: AuditOutcome
    reasoning_chain: list[ReasoningStep] = Field(default_factory=list)
    duration_ms: Annotated[int, Field(ge=0)]

    # ── Hash chain fields (set by AuditWriter only) ───────────────────────
    record_hash: Optional[str] = None
    prev_hash: Optional[str] = None
    chain_id: Optional[UUID] = None

    # ── Stage-specific additional fields (ANIF-107 §4.2.1) ───────────────
    # governance stage
    governance_mode: Optional[GovernanceMode] = None
    ticket_id: Optional[UUID] = None
    applied_policies: Optional[list[str]] = None

    # execute stage
    action_type: Optional[str] = None
    target: Optional[str] = None
    rollback_available: Optional[bool] = None
    post_verification_outcome: Optional[PostVerificationOutcome] = None

    # rollback stage
    original_execute_record_id: Optional[UUID] = None
    rollback_reason: Optional[str] = None
    rollback_outcome: Optional[RollbackOutcome] = None

    # policy stage
    policies_evaluated: Optional[list[str]] = None
    policies_violated: Optional[list[str]] = None

    # risk stage
    risk_score: Optional[Annotated[int, Field(ge=0, le=100)]] = None
    risk_factors: Optional[list[str]] = None

    # ── Ethics extension fields (ANIF-724 §4) ────────────────────────────
    # Agent identity
    agent_id: Optional[UUID] = None
    agent_version: Optional[str] = None
    agent_tier: Optional[AgentTier] = None
    agent_trust_level: Optional[AgentTrustLevel] = None

    # Determinism
    deterministic: Optional[bool] = None
    llm_used: Optional[bool] = None
    llm_model_id: Optional[str] = None
    shadow_used_as_substitution: Optional[bool] = None

    # LLM audit
    llm_prompt_hash: Optional[str] = None
    llm_prompt_length_tokens: Optional[int] = None
    llm_confidence_score: Optional[float] = None
    llm_validation_stage1: Optional[LLMValidationResult] = None
    llm_validation_stage2: Optional[LLMValidationResult] = None
    llm_validation_stage3: Optional[LLMValidationResult] = None
    llm_validation_stage4: Optional[LLMValidationResult] = None

    # Fairness audit
    fairness_check_result: Optional[FairnessResult] = None
    fairness_freshness_gate_result: Optional[LLMValidationResult] = None
    reproducibility_check_result: Optional[ReproducibilityResult] = None
    ai_shadow_divergence: Optional[float] = None

    # Harm classification
    harm_class: Optional[HarmClass] = None
    harm_severity_score: Optional[Annotated[int, Field(ge=0, le=100)]] = None
    blast_radius_segment_count: Optional[int] = None
    harm_gate_outcome: Optional[HarmGateOutcome] = None
    simulation_completed: Optional[bool] = None

    # Accountability chain
    accountability_designer_id: Optional[str] = None
    accountability_deployer_id: Optional[str] = None
    accountability_operator_id: Optional[str] = None
    accountability_approver_id: Optional[str] = None

    # Ethics gate results
    ethics_gates_passed: Optional[list[str]] = None
    ethics_gates_failed: Optional[list[str]] = None
    ethics_gates_skipped: Optional[list[str]] = None

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
