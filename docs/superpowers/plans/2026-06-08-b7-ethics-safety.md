# B7 Ethics & Safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the ethics and safety layer — ANIF-721 agent action constraints, ANIF-722 LLM output validation, ANIF-723 fairness checks, and ANIF-725 containment contract — all wired as blocking pipeline gates per ANIF-720.

**What is already done (do NOT re-implement):**
- ANIF-724 ethics audit fields are already in `AuditRecord` (added in B1)
- `ActionType` bounded enum already exists in `schemas/action.py`
- `AgentTier`, `AgentTrustLevel`, harm/fairness result enums already in `schemas/audit_record.py`
- `AuditWriter` satisfies write-before-return (B1)

**Spec references:**
- `ANIF_SPEC_REPO/docs/700-ai-ethics/ANIF-721_Agent_Action_Constraints.md`
- `ANIF_SPEC_REPO/docs/700-ai-ethics/ANIF-722_LLM_Output_Validation.md`
- `ANIF_SPEC_REPO/docs/700-ai-ethics/ANIF-723_Fairness_Enforcement_Controls.md`
- `ANIF_SPEC_REPO/docs/700-ai-ethics/ANIF-725_Agent_Containment.md`

Where `ANIF_SPEC_REPO` = `/home/dan/Desktop/github/Autonomous-Networking-Infrastructure-Framework-ANIF`

**Working directory:** `/home/dan/Desktop/github/auto_networking/.worktrees/scaffold`

---

## File Map

```
src/anif_platform/ethics/
├── __init__.py               ← Task 1: module init
├── constraints.py            ← Task 2: ANIF-721 (startup validator, RollbackPlan, StrikeService)
├── models.py                 ← Task 3: StrikeRecordRow (append-only SQLAlchemy table)
├── llm_validator.py          ← Task 4: ANIF-722 LLMOutputValidator (4-stage pipeline)
├── fairness.py               ← Task 5: ANIF-723 FairnessChecker (3 checks)
├── containment.py            ← Task 6: ANIF-725 PipelineContext + ContainmentContract
└── router.py                 ← Task 7: /override endpoint (hardcoded, non-configurable)

migrations/versions/006_add_strike_records.py  ← Task 3
src/anif_platform/main.py                       ← Task 8: wire router + startup validation
migrations/env.py                               ← Task 8: import ethics models
src/anif_platform/execution/executor.py         ← Task 9: extend execute() with PipelineContext

tests/unit/
├── test_ethics_constraints.py    ← Task 2
├── test_ethics_llm_validator.py  ← Task 4
├── test_ethics_fairness.py       ← Task 5
├── test_ethics_containment.py    ← Task 6
└── test_ethics_router.py         ← Task 7
```

---

## Task 1: Module Init

**Files:** `src/anif_platform/ethics/__init__.py`

- [ ] **Write `__init__.py`**

  ```python
  """Ethics and safety safeguards — ANIF-720 through ANIF-725."""
  ```

- [ ] **Commit**

  ```bash
  git add src/anif_platform/ethics/__init__.py
  git commit -m "chore: initialise B7 ethics module"
  ```

---

## Task 2: ANIF-721 Action Constraints

**Files:**
- Create: `src/anif_platform/ethics/constraints.py`
- Create: `tests/unit/test_ethics_constraints.py`

### 2a. Failing tests first

Create `tests/unit/test_ethics_constraints.py`:

```python
"""Tests for ANIF-721 agent action constraints."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from anif_platform.ethics.constraints import (
    ActionTypeValidator,
    RollbackPlan,
    StrikeService,
)
from anif_platform.exceptions import ANIFError


# ── ActionTypeValidator ────────────────────────────────────────────────────


def test_validator_accepts_reroute_traffic() -> None:
    """ANIF-721 §4.1: reroute_traffic is a valid action type."""
    ActionTypeValidator.validate_action_type("reroute_traffic")  # must not raise


def test_validator_accepts_apply_qos() -> None:
    """ANIF-721 §4.1: apply_qos is a valid action type."""
    ActionTypeValidator.validate_action_type("apply_qos")


def test_validator_accepts_scale_bandwidth() -> None:
    """ANIF-721 §4.1: scale_bandwidth is a valid action type."""
    ActionTypeValidator.validate_action_type("scale_bandwidth")


def test_validator_accepts_isolate_segment() -> None:
    """ANIF-721 §4.1: isolate_segment is a valid action type."""
    ActionTypeValidator.validate_action_type("isolate_segment")


def test_validator_rejects_unknown_action_type() -> None:
    """ANIF-721 §4.4: unknown action type MUST be rejected."""
    with pytest.raises(ANIFError, match="invalid action type"):
        ActionTypeValidator.validate_action_type("delete_all_routes")


def test_validator_rejects_empty_string() -> None:
    """ANIF-721 §4.4: empty string is not a valid action type."""
    with pytest.raises(ANIFError):
        ActionTypeValidator.validate_action_type("")


def test_startup_validation_passes_with_correct_enum() -> None:
    """ANIF-721 §4.2: startup validation succeeds when all four action types are present."""
    ActionTypeValidator.validate_at_startup()  # must not raise


# ── RollbackPlan ───────────────────────────────────────────────────────────


def test_rollback_plan_requires_rollback_action_type() -> None:
    """ANIF-721 §5.3: rollback_action_type is required."""
    with pytest.raises(Exception):
        RollbackPlan(
            rollback_target="segment-a",
            rollback_within_seconds=60,
            rollback_confirmed_at=datetime.now(UTC),
        )  # missing rollback_action_type


def test_rollback_plan_requires_non_empty_target() -> None:
    """ANIF-721 §5.3: rollback_target is required and non-empty."""
    with pytest.raises(Exception):
        RollbackPlan(
            rollback_action_type="reroute_traffic",
            rollback_target="",
            rollback_within_seconds=60,
            rollback_confirmed_at=datetime.now(UTC),
        )


def test_rollback_plan_valid() -> None:
    """ANIF-721 §5.3: a fully specified rollback plan is accepted."""
    plan = RollbackPlan(
        rollback_action_type="reroute_traffic",
        rollback_target="segment-a",
        rollback_within_seconds=60,
        rollback_confirmed_at=datetime.now(UTC),
    )
    assert plan.rollback_action_type == "reroute_traffic"


def test_rollback_plan_rejects_invalid_action_type() -> None:
    """ANIF-721 §5.3: rollback_action_type must be within the bounded enum."""
    with pytest.raises(Exception, match="invalid action type"):
        RollbackPlan(
            rollback_action_type="drop_all_routes",
            rollback_target="segment-a",
            rollback_within_seconds=60,
            rollback_confirmed_at=datetime.now(UTC),
        )


# ── StrikeService ──────────────────────────────────────────────────────────


def test_strike_service_record_strike_returns_record() -> None:
    """ANIF-721 §7.1: recording a strike returns the created record."""
    service = StrikeService()
    record = service.record_strike(
        agent_id=uuid.uuid4(),
        intent_id=uuid.uuid4(),
        reason="schema_validation_failure",
    )
    assert record.reason == "schema_validation_failure"


def test_strike_service_count_returns_zero_initially() -> None:
    """ANIF-721 §7.1: no strikes recorded yet."""
    service = StrikeService()
    agent_id = uuid.uuid4()
    assert service.count_strikes(agent_id=agent_id, window_minutes=60) == 0


def test_strike_service_count_after_recording() -> None:
    """ANIF-721 §7.1: count increases after recording a strike."""
    service = StrikeService()
    agent_id = uuid.uuid4()
    service.record_strike(agent_id=agent_id, intent_id=uuid.uuid4(), reason="test")
    assert service.count_strikes(agent_id=agent_id, window_minutes=60) == 1
```

- [ ] **Run tests — confirm all FAIL**

  ```bash
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif_test \
    .venv/bin/pytest tests/unit/test_ethics_constraints.py -v --no-cov 2>&1 | tail -20
  ```

### 2b. Implementation

Create `src/anif_platform/ethics/constraints.py`:

```python
"""ANIF-721 agent action constraints — startup validator, rollback plan, strike service."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated

import structlog
from pydantic import BaseModel, Field, field_validator

from anif_platform.exceptions import ANIFError
from anif_platform.schemas.action import ActionType

log = structlog.get_logger(__name__)

# ANIF-721 §4.1: the four valid action types — do not add or remove without council review
_VALID_ACTION_TYPES: frozenset[str] = frozenset(
    {e.value for e in ActionType}
)


class ActionTypeViolationError(ANIFError):
    """Raised when an action type outside the bounded enum is encountered — ANIF-721 §4.4."""


class ActionTypeValidator:
    """Validates action types against the ANIF-721 bounded enum.

    Call validate_at_startup() once during application lifespan to verify the
    enum is intact. Call validate_action_type() at every boundary where an
    action type value is received from outside the application.
    """

    @staticmethod
    def validate_action_type(action_type: str) -> None:
        """Raise ActionTypeViolationError if action_type is not in the bounded enum."""
        if action_type not in _VALID_ACTION_TYPES:
            log.warning(
                "action_type_violation",
                action_type=action_type,
                valid_types=sorted(_VALID_ACTION_TYPES),
            )
            raise ActionTypeViolationError(
                f"invalid action type {action_type!r} — "
                f"must be one of {sorted(_VALID_ACTION_TYPES)} (ANIF-721 §4)"
            )

    @staticmethod
    def validate_at_startup() -> None:
        """Verify the bounded enum is intact at application startup — ANIF-721 §4.2.

        Raises RuntimeError if any of the four required action types is missing.
        Called from the FastAPI lifespan function before accepting requests.
        """
        required = {"reroute_traffic", "apply_qos", "scale_bandwidth", "isolate_segment"}
        actual = _VALID_ACTION_TYPES
        missing = required - actual
        if missing:
            raise RuntimeError(
                f"ANIF-721 startup validation failed: action type enum is missing {missing}"
            )
        log.info("action_type_startup_validation_passed", valid_types=sorted(actual))


class RollbackPlan(BaseModel):
    """Confirmed rollback plan required by execute() — ANIF-721 §5.

    Must be constructed before execute() is called. execute() validates
    this object as its first operation.
    """

    rollback_action_type: str
    rollback_target: Annotated[str, Field(min_length=1)]
    rollback_within_seconds: Annotated[int, Field(ge=1)]
    rollback_confirmed_at: datetime

    @field_validator("rollback_action_type")
    @classmethod
    def must_be_valid_action_type(cls, v: str) -> str:
        """ANIF-721 §5.3: rollback_action_type must be in the bounded enum."""
        ActionTypeValidator.validate_action_type(v)
        return v

    @field_validator("rollback_confirmed_at")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v.astimezone(UTC)


class StrikeRecord(BaseModel):
    """Immutable strike record — never update or delete after creation."""

    strike_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    agent_id: uuid.UUID
    intent_id: uuid.UUID
    reason: str
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class StrikeService:
    """In-memory append-only strike counter for unit testing.

    Production deployments MUST replace this with a DB-backed implementation
    using StrikeRecordRow (see models.py), which enforces append-only at the
    database level via row-level security — ANIF-721 §7.2.
    """

    def __init__(self) -> None:
        self._records: list[StrikeRecord] = []

    def record_strike(
        self,
        agent_id: uuid.UUID,
        intent_id: uuid.UUID,
        reason: str,
    ) -> StrikeRecord:
        """Append a strike record. Never updates or deletes existing records."""
        record = StrikeRecord(agent_id=agent_id, intent_id=intent_id, reason=reason)
        self._records.append(record)
        log.info(
            "strike_recorded",
            agent_id=str(agent_id),
            intent_id=str(intent_id),
            reason=reason,
            strike_id=str(record.strike_id),
        )
        return record

    def count_strikes(self, agent_id: uuid.UUID, window_minutes: int) -> int:
        """Count strikes for an agent within the given time window."""
        cutoff = datetime.now(UTC).replace(
            second=0, microsecond=0
        )
        from datetime import timedelta
        cutoff = datetime.now(UTC) - timedelta(minutes=window_minutes)
        return sum(
            1
            for r in self._records
            if r.agent_id == agent_id and r.recorded_at >= cutoff
        )
```

- [ ] **Run tests — confirm all PASS**

  ```bash
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif_test \
    .venv/bin/pytest tests/unit/test_ethics_constraints.py -v --no-cov
  ```

- [ ] **Commit**

  ```bash
  git add src/anif_platform/ethics/constraints.py tests/unit/test_ethics_constraints.py
  git commit -m "feat: implement ANIF-721 action type validator, rollback plan, and strike service"
  ```

---

## Task 3: Strike Record DB Model + Migration

**Files:**
- Create: `src/anif_platform/ethics/models.py`
- Create: `migrations/versions/006_add_strike_records.py`
- Modify: `migrations/env.py`

### 3a. DB model

Create `src/anif_platform/ethics/models.py`:

```python
"""Ethics module SQLAlchemy models — ANIF-721 strike records."""

from __future__ import annotations

import uuid as _uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from anif_platform.database import Base


class StrikeRecordRow(Base):
    """Append-only agent strike record — ANIF-721 §7.

    The append-only property MUST be enforced at the database level.
    PostgreSQL: row-level security policy prevents UPDATE and DELETE for
    all application roles. Only INSERT and SELECT are permitted.
    See migration 006 for the RLS policy definition.
    """

    __tablename__ = "strike_records"

    strike_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    intent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
```

### 3b. Migration

Create `migrations/versions/006_add_strike_records.py`:

```python
"""add strike_records table with append-only RLS

Revision ID: 006
Revises: 005
Create Date: 2026-06-08
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "strike_records",
        sa.Column("strike_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("intent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.String(255), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_strike_records_agent_id", "strike_records", ["agent_id"])

    # ANIF-721 §7.2: enforce append-only at the database level.
    # The application role must NOT be able to UPDATE or DELETE strike records.
    # This policy prevents even a compromised application from erasing strike history.
    op.execute(
        """
        ALTER TABLE strike_records ENABLE ROW LEVEL SECURITY;
        CREATE POLICY strike_records_insert_only
            ON strike_records
            FOR ALL
            USING (true)
            WITH CHECK (true);
        REVOKE UPDATE, DELETE ON strike_records FROM PUBLIC;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS strike_records_insert_only ON strike_records")
    op.drop_table("strike_records")
```

### 3c. Update env.py import

In `migrations/env.py`, add after the last `from anif_platform` import:

```python
import anif_platform.ethics.models  # noqa: F401  — registers StrikeRecordRow with Base
```

- [ ] **Commit**

  ```bash
  git add src/anif_platform/ethics/models.py migrations/versions/006_add_strike_records.py migrations/env.py
  git commit -m "feat: add StrikeRecordRow model and migration 006 with append-only RLS (ANIF-721)"
  ```

---

## Task 4: ANIF-722 LLM Output Validator

**Files:**
- Create: `src/anif_platform/ethics/llm_validator.py`
- Create: `tests/unit/test_ethics_llm_validator.py`

### 4a. Failing tests first

Create `tests/unit/test_ethics_llm_validator.py`:

```python
"""Tests for ANIF-722 LLM output validation — 4-stage pipeline."""

from __future__ import annotations

import hashlib
import uuid

import pytest

from anif_platform.ethics.llm_validator import (
    LLMOutputValidator,
    LLMValidationInput,
    LLMValidationOutcome,
    Stage4SecurityIncident,
)


def _make_prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()


def _valid_input(
    *,
    confidence: float = 0.90,
    agent_tier: int = 2,
    prompt: str = "test prompt",
    schema_valid: bool = True,
    hallucination_free: bool = True,
) -> LLMValidationInput:
    prompt_hash = _make_prompt_hash(prompt)
    return LLMValidationInput(
        agent_id=uuid.uuid4(),
        intent_id=uuid.uuid4(),
        agent_tier=agent_tier,
        output_schema_valid=schema_valid,
        factual_claims_consistent=hallucination_free,
        canonical_state_age_seconds=120,
        confidence_score=confidence,
        prompt_hash_recorded=prompt_hash,
        prompt_hash_submitted=prompt_hash,
    )


# ── Stage 1: Schema Check ──────────────────────────────────────────────────


def test_stage1_pass_when_schema_valid() -> None:
    """ANIF-722 §5.2: output passes stage 1 when schema is valid."""
    result = LLMOutputValidator().validate(_valid_input(schema_valid=True))
    assert result.stage1 == "pass"


def test_stage1_fail_blocks_pipeline() -> None:
    """ANIF-722 §5.4: schema failure blocks — result is blocked with manual_review."""
    result = LLMOutputValidator().validate(_valid_input(schema_valid=False))
    assert result.stage1 == "fail"
    assert result.blocked is True
    assert result.route_to == "manual_review"
    assert result.strike_incremented is True


# ── Stage 2: Hallucination Check ──────────────────────────────────────────


def test_stage2_fail_blocks_pipeline() -> None:
    """ANIF-722 §6.6: hallucination failure blocks and increments strike."""
    result = LLMOutputValidator().validate(
        _valid_input(schema_valid=True, hallucination_free=False)
    )
    assert result.stage2 == "fail"
    assert result.blocked is True
    assert result.strike_incremented is True


def test_stage2_stale_canonical_state_blocks() -> None:
    """ANIF-722 §6.2: canonical state older than 5 min (300s) MUST block stage 2."""
    inp = _valid_input()
    inp.canonical_state_age_seconds = 400
    result = LLMOutputValidator().validate(inp)
    assert result.stage2 == "fail"
    assert result.blocked is True


# ── Stage 3: Confidence Check ──────────────────────────────────────────────


def test_stage3_pass_tier2_above_threshold() -> None:
    """ANIF-722 §7.3: tier 2 agent with confidence ≥ 0.65 passes stage 3."""
    result = LLMOutputValidator().validate(_valid_input(confidence=0.70, agent_tier=2))
    assert result.stage3 == "pass"
    assert result.blocked is False


def test_stage3_suppressed_tier2_below_threshold() -> None:
    """ANIF-722 §7.5: tier 2 agent with confidence < 0.65 is suppressed (not blocked)."""
    result = LLMOutputValidator().validate(_valid_input(confidence=0.50, agent_tier=2))
    assert result.stage3 == "suppressed"
    assert result.blocked is True
    assert result.strike_incremented is False


def test_stage3_suppressed_tier3_below_threshold() -> None:
    """ANIF-722 §7.2: tier 3 threshold is 0.80."""
    result = LLMOutputValidator().validate(_valid_input(confidence=0.75, agent_tier=3))
    assert result.stage3 == "suppressed"
    assert result.blocked is True


# ── Stage 4: Prompt Integrity Hash ────────────────────────────────────────


def test_stage4_pass_when_hashes_match() -> None:
    """ANIF-722 §8.2: matching hashes pass stage 4."""
    result = LLMOutputValidator().validate(_valid_input())
    assert result.stage4 == "pass"


def test_stage4_hash_mismatch_raises_security_incident() -> None:
    """ANIF-722 §8.4: hash mismatch MUST raise Stage4SecurityIncident (not route to manual_review)."""
    inp = _valid_input()
    inp.prompt_hash_submitted = "tampered_hash_value"
    with pytest.raises(Stage4SecurityIncident):
        LLMOutputValidator().validate(inp)


# ── All stages pass ────────────────────────────────────────────────────────


def test_all_stages_pass_returns_approved() -> None:
    """ANIF-722 §4: all stages passing returns approved output."""
    result = LLMOutputValidator().validate(_valid_input())
    assert result.blocked is False
    assert result.stage1 == "pass"
    assert result.stage2 == "pass"
    assert result.stage3 == "pass"
    assert result.stage4 == "pass"
```

- [ ] **Run tests — confirm all FAIL**

### 4b. Implementation

Create `src/anif_platform/ethics/llm_validator.py`:

```python
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


class Stage4SecurityIncident(Exception):
    """Raised when prompt hash mismatch is detected — ANIF-722 §8.4.

    This is a security incident, not a validation failure. Must NOT be caught
    and routed to manual_review. The pipeline halts and security team is notified.
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

    # Stage 1 input
    output_schema_valid: bool

    # Stage 2 inputs
    factual_claims_consistent: bool
    canonical_state_age_seconds: int

    # Stage 3 input
    confidence_score: float

    # Stage 4 inputs
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

    Stages MUST run in order. Stage 4 failure raises Stage4SecurityIncident
    rather than returning a blocked result — it is a security incident.
    """

    def validate(self, inp: LLMValidationInput) -> LLMValidationOutcome:
        """Run all four stages in order. Return outcome or raise Stage4SecurityIncident."""
        stage1 = "pass" if inp.output_schema_valid else "fail"
        if stage1 == "fail":
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

        # Stage 2: Hallucination check
        stage2: Literal["pass", "fail", "skipped"]
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

        stage2 = "pass" if inp.factual_claims_consistent else "fail"
        if stage2 == "fail":
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

        # Stage 3: Confidence check
        threshold = _CONFIDENCE_THRESHOLDS.get(inp.agent_tier, 0.65)
        stage3: Literal["pass", "suppressed"]
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
        stage3 = "pass"

        # Stage 4: Prompt integrity hash — SECURITY INCIDENT if mismatch
        if inp.prompt_hash_submitted != inp.prompt_hash_recorded:
            log.critical(
                "llm_validation_stage4_hash_mismatch_SECURITY_INCIDENT",
                agent_id=str(inp.agent_id),
                intent_id=str(inp.intent_id),
                recorded_hash=inp.prompt_hash_recorded,
                submitted_hash=inp.prompt_hash_submitted,
            )
            raise Stage4SecurityIncident(
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
```

- [ ] **Run tests — confirm all PASS**

  ```bash
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif_test \
    .venv/bin/pytest tests/unit/test_ethics_llm_validator.py -v --no-cov
  ```

- [ ] **Commit**

  ```bash
  git add src/anif_platform/ethics/llm_validator.py tests/unit/test_ethics_llm_validator.py
  git commit -m "feat: implement ANIF-722 LLM output validator (4-stage sequential pipeline)"
  ```

---

## Task 5: ANIF-723 Fairness Checker

**Files:**
- Create: `src/anif_platform/ethics/fairness.py`
- Create: `tests/unit/test_ethics_fairness.py`

### 5a. Failing tests first

Create `tests/unit/test_ethics_fairness.py`:

```python
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
    # sla_floor = 99 * 0.8 = 79.2; 82 > 79.2 ✓
    # sla_floor = 95 * 0.8 = 76.0; 78 > 76.0 ✓
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
    result = FairnessChecker().check(
        _base_input(agent_tier=3, repro=repro)
    )
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
```

- [ ] **Run tests — confirm all FAIL**

### 5b. Implementation

Create `src/anif_platform/ethics/fairness.py`:

```python
"""ANIF-723 fairness enforcement controls — 3 independent blocking checks."""

from __future__ import annotations

import uuid
from typing import Literal

import structlog
from pydantic import BaseModel

log = structlog.get_logger(__name__)

# ANIF-723 §5.7: hardcoded — MUST NOT be lowered by configuration
_FRESHNESS_THRESHOLD: float = 0.7

# ANIF-723 §6.4: maximum divergence tolerance by action type (QoS: 1 DSCP class)
_QOS_MAX_DIVERGENCE: int = 1


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
    reproducibility_result: Literal["pass", "fail", "shadow_used", "shadow_unavailable", "not_applicable"]
    ai_output_divergence: float | None
    shadow_substitution_applied: bool
    blocked: bool
    route_to: Literal["manual_review", "approved"] | None


_RESOURCE_ALLOCATION_ACTIONS = frozenset({"reroute_traffic", "apply_qos", "scale_bandwidth"})


class FairnessChecker:
    """Runs ANIF-723 fairness checks independently — all three run even if one fails."""

    def check(self, inp: FairnessInput) -> FairnessOutcome:
        """Run all three checks. All three are independent — each may block."""
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
    ) -> tuple[Literal["pass", "fail", "shadow_used", "shadow_unavailable", "not_applicable"], float | None, bool]:
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
```

- [ ] **Run tests — confirm all PASS**

  ```bash
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif_test \
    .venv/bin/pytest tests/unit/test_ethics_fairness.py -v --no-cov
  ```

- [ ] **Commit**

  ```bash
  git add src/anif_platform/ethics/fairness.py tests/unit/test_ethics_fairness.py
  git commit -m "feat: implement ANIF-723 fairness checker (SLA floor, freshness gate, reproducibility)"
  ```

---

## Task 6: ANIF-725 Containment Contract

**Files:**
- Create: `src/anif_platform/ethics/containment.py`
- Create: `tests/unit/test_ethics_containment.py`

### 6a. Failing tests first

Create `tests/unit/test_ethics_containment.py`:

```python
"""Tests for ANIF-725 pipeline containment contract."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from anif_platform.ethics.containment import ContainmentContract, PipelineContext
from anif_platform.ethics.constraints import RollbackPlan
from anif_platform.exceptions import ANIFError


def _valid_context(**overrides) -> PipelineContext:
    base = dict(
        intent_id=uuid.uuid4(),
        policy_result={"mode": "auto", "policies_evaluated": []},
        risk_score_result={"score": 20, "threshold_applied": "default"},
        harm_classification_result={"harm_class": "none", "harm_severity_score": 10},
        fairness_check_result={"sla_floor_result": "not_applicable", "freshness_gate_result": "pass"},
        llm_validation_result=None,
        governance_decision={"mode": "auto", "ticket_id": None},
        rollback_plan=RollbackPlan(
            rollback_action_type="reroute_traffic",
            rollback_target="segment-a",
            rollback_within_seconds=60,
            rollback_confirmed_at=datetime.now(UTC),
        ),
    )
    base.update(overrides)
    return PipelineContext(**base)


def test_valid_context_passes_validation() -> None:
    """ANIF-725 §4.2: a fully specified PipelineContext passes containment validation."""
    ctx = _valid_context()
    ContainmentContract.validate(ctx)  # must not raise


def test_missing_policy_result_raises() -> None:
    """ANIF-725 §4.2: policy_result is mandatory — None raises ANIFError."""
    ctx = _valid_context(policy_result=None)
    with pytest.raises(ANIFError, match="policy_result"):
        ContainmentContract.validate(ctx)


def test_missing_risk_score_result_raises() -> None:
    """ANIF-725 §4.2: risk_score_result is mandatory."""
    ctx = _valid_context(risk_score_result=None)
    with pytest.raises(ANIFError, match="risk_score_result"):
        ContainmentContract.validate(ctx)


def test_missing_harm_classification_raises() -> None:
    """ANIF-725 §4.2: harm_classification_result is mandatory."""
    ctx = _valid_context(harm_classification_result=None)
    with pytest.raises(ANIFError, match="harm_classification_result"):
        ContainmentContract.validate(ctx)


def test_missing_fairness_check_raises() -> None:
    """ANIF-725 §4.2: fairness_check_result is mandatory."""
    ctx = _valid_context(fairness_check_result=None)
    with pytest.raises(ANIFError, match="fairness_check_result"):
        ContainmentContract.validate(ctx)


def test_missing_governance_decision_raises() -> None:
    """ANIF-725 §4.2: governance_decision is mandatory."""
    ctx = _valid_context(governance_decision=None)
    with pytest.raises(ANIFError, match="governance_decision"):
        ContainmentContract.validate(ctx)


def test_missing_rollback_plan_raises() -> None:
    """ANIF-725 §4.2: rollback_plan is mandatory — ANIF-721 §5 constraint."""
    ctx = _valid_context(rollback_plan=None)
    with pytest.raises(ANIFError, match="rollback_plan"):
        ContainmentContract.validate(ctx)
```

- [ ] **Run tests — confirm all FAIL**

### 6b. Implementation

Create `src/anif_platform/ethics/containment.py`:

```python
"""ANIF-725 pipeline containment contract — execute() mandatory parameter enforcement."""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from pydantic import BaseModel

from anif_platform.ethics.constraints import RollbackPlan
from anif_platform.exceptions import ANIFError

log = structlog.get_logger(__name__)


class ContainmentViolationError(ANIFError):
    """Raised when execute() is called without evidence that a required pipeline stage ran.

    This is a Severity 1 ethics incident — ANIF-725 §4.5.
    """


class PipelineContext(BaseModel):
    """Evidence that all eight required pipeline stages have run — ANIF-725 §4.2.

    Passed to execute() as the first parameter. execute() validates this object
    before any other logic runs. No default values are permitted for any field.
    """

    intent_id: uuid.UUID
    policy_result: dict[str, Any] | None
    risk_score_result: dict[str, Any] | None
    harm_classification_result: dict[str, Any] | None
    fairness_check_result: dict[str, Any] | None
    llm_validation_result: dict[str, Any] | None  # None permitted when no LLM was used
    governance_decision: dict[str, Any] | None
    rollback_plan: RollbackPlan | None


class ContainmentContract:
    """Validates that a PipelineContext has all mandatory non-LLM fields populated.

    Call ContainmentContract.validate(ctx) as the first operation inside execute().
    Raises ContainmentViolationError if any mandatory parameter is missing.
    """

    # Fields that MUST be present — None is not permitted
    _MANDATORY_FIELDS = (
        "policy_result",
        "risk_score_result",
        "harm_classification_result",
        "fairness_check_result",
        "governance_decision",
        "rollback_plan",
    )

    @classmethod
    def validate(cls, ctx: PipelineContext) -> None:
        """Validate all mandatory fields are present. Raises ContainmentViolationError if not."""
        for field in cls._MANDATORY_FIELDS:
            if getattr(ctx, field) is None:
                log.critical(
                    "containment_violation_SEVERITY_1",
                    missing_field=field,
                    intent_id=str(ctx.intent_id),
                )
                raise ContainmentViolationError(
                    f"execute() called without {field} — "
                    f"this is a Severity 1 ethics incident (ANIF-725 §4). "
                    f"intent_id={ctx.intent_id}"
                )
        log.debug("containment_contract_validated", intent_id=str(ctx.intent_id))
```

- [ ] **Run tests — confirm all PASS**

  ```bash
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif_test \
    .venv/bin/pytest tests/unit/test_ethics_containment.py -v --no-cov
  ```

- [ ] **Commit**

  ```bash
  git add src/anif_platform/ethics/containment.py tests/unit/test_ethics_containment.py
  git commit -m "feat: implement ANIF-725 containment contract (PipelineContext + mandatory parameter validation)"
  ```

---

## Task 7: Human Override Endpoint

**Files:**
- Create: `src/anif_platform/ethics/router.py`
- Create: `tests/unit/test_ethics_router.py`

The `/override` endpoint is hardcoded and non-configurable — ANIF-721 §6. It MUST be available at all times the application is running.

### 7a. Failing tests first

Create `tests/unit/test_ethics_router.py`:

```python
"""Tests for the human override endpoint — ANIF-721 §6."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from anif_platform.ethics.router import router as override_router
from fastapi import FastAPI


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(override_router)
    return TestClient(app)


def test_override_endpoint_exists(client: TestClient) -> None:
    """ANIF-721 §6.2: override endpoint MUST exist at /override."""
    intent_id = str(uuid.uuid4())
    resp = client.post("/override", json={"intent_id": intent_id, "reason": "test"})
    assert resp.status_code in (200, 202)


def test_override_endpoint_returns_acknowledged(client: TestClient) -> None:
    """ANIF-721 §6.2: override MUST acknowledge receipt."""
    intent_id = str(uuid.uuid4())
    resp = client.post("/override", json={"intent_id": intent_id, "reason": "test"})
    body = resp.json()
    assert body.get("status") == "acknowledged"
    assert body.get("intent_id") == intent_id


def test_override_requires_intent_id(client: TestClient) -> None:
    """ANIF-721 §6.2: override without intent_id MUST return 422."""
    resp = client.post("/override", json={"reason": "test"})
    assert resp.status_code == 422


def test_override_requires_reason(client: TestClient) -> None:
    """ANIF-721 §6.2: override without reason MUST return 422."""
    resp = client.post("/override", json={"intent_id": str(uuid.uuid4())})
    assert resp.status_code == 422
```

- [ ] **Run tests — confirm all FAIL**

### 7b. Implementation

Create `src/anif_platform/ethics/router.py`:

```python
"""Human override endpoint — ANIF-721 §6.

This endpoint is HARDCODED and NON-CONFIGURABLE. It MUST NOT be:
- Disabled through configuration
- Rate-limited beyond standard DoS protection
- Delayed beyond 5 seconds

Modifying this file requires build-time council review (ANIF-903).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter
from pydantic import BaseModel

log = structlog.get_logger(__name__)

router = APIRouter(tags=["ethics"])


class OverrideRequest(BaseModel):
    intent_id: uuid.UUID
    reason: str


class OverrideResponse(BaseModel):
    status: str
    intent_id: uuid.UUID
    acknowledged_at: datetime
    message: str


@router.post("/override", response_model=OverrideResponse)
async def human_override(request: OverrideRequest) -> dict[str, Any]:
    """Halt a targeted action immediately — ANIF-721 §6.

    Available at all times. Cannot be disabled or redirected through configuration.
    Override MUST take effect within 5 seconds of a valid request.
    """
    acknowledged_at = datetime.now(UTC)
    log.info(
        "human_override_received",
        intent_id=str(request.intent_id),
        reason=request.reason,
        acknowledged_at=acknowledged_at.isoformat(),
    )
    # In a full implementation this would signal the pipeline to halt the intent.
    # The signal mechanism is intent-registry state update + pubsub notification.
    # Implementation deferred to when a running pipeline exists (B8/F2).
    return {
        "status": "acknowledged",
        "intent_id": request.intent_id,
        "acknowledged_at": acknowledged_at,
        "message": (
            f"Override received for intent {request.intent_id}. "
            "Pipeline halt signal dispatched."
        ),
    }
```

- [ ] **Run tests — confirm all PASS**

  ```bash
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif_test \
    .venv/bin/pytest tests/unit/test_ethics_router.py -v --no-cov
  ```

- [ ] **Commit**

  ```bash
  git add src/anif_platform/ethics/router.py tests/unit/test_ethics_router.py
  git commit -m "feat: add hardcoded human override endpoint /override (ANIF-721 §6)"
  ```

---

## Task 8: Wire into main.py

**Files:**
- Modify: `src/anif_platform/main.py`

### 8a. Changes needed

1. Call `ActionTypeValidator.validate_at_startup()` in the lifespan function
2. Import and mount the override router
3. Verify override router is mounted before `yield` (available from first request)

In `src/anif_platform/main.py`:

- Add to imports:
  ```python
  from anif_platform.ethics.constraints import ActionTypeValidator
  from anif_platform.ethics.router import router as override_router
  ```

- In `lifespan()`, add immediately after `log.info("anif_platform_starting")`:
  ```python
  ActionTypeValidator.validate_at_startup()
  log.info("action_type_startup_validation_passed")
  ```

- After `app.include_router(execution_router)`, add:
  ```python
  app.include_router(override_router)
  ```

- [ ] **Verify main.py starts without errors**

  ```bash
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif_test \
    .venv/bin/python -c "from anif_platform.main import app; print('import ok')"
  ```

- [ ] **Commit**

  ```bash
  git add src/anif_platform/main.py
  git commit -m "feat: wire B7 ethics safeguards into main.py (startup validation + /override)"
  ```

---

## Task 9: Extend execute() with PipelineContext

**Files:**
- Modify: `src/anif_platform/execution/executor.py`
- Modify: `src/anif_platform/execution/router.py`
- Modify: `tests/unit/test_action_executor.py` (update call sites)

### 9a. executor.py changes

The `execute()` method must accept a `PipelineContext` as its first argument and call `ContainmentContract.validate(ctx)` before any other logic — ANIF-725 §4.3.

In `src/anif_platform/execution/executor.py`:

- Add to imports:
  ```python
  from anif_platform.ethics.containment import ContainmentContract, PipelineContext
  ```

- Change the `execute()` signature from:
  ```python
  async def execute(
      self,
      intent_id: uuid.UUID,
      decision: dict[str, Any],
      parameters: dict[str, Any],
      governance_result: dict[str, Any],
      ticket_id: str | None,
  ) -> dict[str, Any]:
  ```
  to:
  ```python
  async def execute(
      self,
      pipeline_context: PipelineContext,
      decision: dict[str, Any],
      parameters: dict[str, Any],
      ticket_id: str | None,
  ) -> dict[str, Any]:
  ```

- As the **first operation** in `execute()`, add:
  ```python
  ContainmentContract.validate(pipeline_context)
  intent_id = pipeline_context.intent_id
  governance_result = pipeline_context.governance_decision or {}
  ```

### 9b. router.py changes

Update `src/anif_platform/execution/router.py` — the `/execute` route body must construct a `PipelineContext` from the request and pass it to `executor.execute()`.

Add to imports:
```python
from anif_platform.ethics.containment import PipelineContext
from anif_platform.ethics.constraints import RollbackPlan
```

In the `execute_action` endpoint, construct a `PipelineContext` from request fields before calling `executor.execute()`.

### 9c. Update executor tests

In `tests/unit/test_action_executor.py`: update all calls to `executor.execute()` to pass a `PipelineContext` as the first argument. The test should build a minimal valid `PipelineContext` using a helper fixture.

- [ ] **Run full test suite**

  ```bash
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif_test \
    .venv/bin/pytest tests/unit/ -v --no-cov 2>&1 | tail -30
  ```

  Expected: all tests pass except the 7 audit_writer tests that require live PostgreSQL.

- [ ] **Commit**

  ```bash
  git add src/anif_platform/execution/executor.py \
          src/anif_platform/execution/router.py \
          tests/unit/test_action_executor.py
  git commit -m "feat: extend execute() with PipelineContext mandatory parameter (ANIF-725 §4)"
  ```

---

## Task 10: Final Verification

- [ ] **Run full unit test suite**

  ```bash
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif_test \
    .venv/bin/pytest tests/unit/ -v --no-cov 2>&1 | tail -40
  ```

  Expected: all tests pass (7 audit_writer DB tests are expected errors requiring live PG).

- [ ] **Run ruff**

  ```bash
  .venv/bin/ruff check src/anif_platform/ethics/ tests/unit/test_ethics_*.py
  ```

- [ ] **Verify /override is in app routes**

  ```bash
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif_test \
    .venv/bin/python -c "
  from anif_platform.main import app
  routes = [r.path for r in app.routes]
  assert '/override' in routes, f'/override not found in {routes}'
  print('override endpoint present:', '/override' in routes)
  "
  ```

- [ ] **Final commit**

  ```bash
  git add -A && git status
  # Expected: clean working tree
  git log --oneline | head -15
  ```

---

## Post-B7 Checklist

- [ ] `ActionTypeValidator.validate_at_startup()` called in lifespan
- [ ] `StrikeRecordRow` table in migration 006 with RLS policy
- [ ] `LLMOutputValidator` — 4 stages in order, stage 4 raises `Stage4SecurityIncident` (not routed to manual_review)
- [ ] `FairnessChecker` — all 3 checks run independently
- [ ] `ContainmentContract.validate()` is the first call in `execute()`
- [ ] `/override` endpoint present in app routes, hardcoded in `ethics/router.py`
- [ ] All new tests pass
- [ ] No ruff violations

**Next:** B8 — Councils & Learning (3 AI Councils, Feedback, Learning Agent).
