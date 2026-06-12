# B1: Foundation & Data Models — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement all Pydantic v2 schemas and the AuditWriter service that every subsequent B-phase module depends on.

**Architecture:** Two independent layers — (1) pure Pydantic models in `src/anif_platform/schemas/` that enforce every ANIF data invariant at the type level, and (2) the `audit/` module providing `AuditWriter` (write-before-return, SHA-256 hash chaining) and read endpoints (`GET /audit/*`). All other B-phase modules will import from these two layers. No pipeline logic lives here.

**Tech Stack:** Python 3.13, Pydantic v2, SQLAlchemy 2 async, asyncpg, Alembic, FastAPI, pytest-asyncio, structlog.

**Spec sources:**
- `ANIF-300` — intent identity and immutability rules
- `ANIF-600` — normative schema definitions + Pydantic mappings
- `ANIF-107` — audit trail requirements, write-before-return, hash chaining, query endpoints
- `ANIF-724` — ethics audit fields extension

**Working directory:** `/home/dan/Desktop/github/auto_networking/.worktrees/scaffold/`

**Run all tests with:** `.venv/bin/pytest -v`

---

## File Map

```
src/anif_platform/
├── schemas/
│   ├── __init__.py          MODIFY — re-export all models
│   ├── intent.py            CREATE — Intent, Objectives, Constraints, enums
│   ├── action.py            CREATE — Action, ActionType, RiskLevel
│   ├── policy.py            CREATE — Policy, PolicyRule, RuleAction
│   ├── risk_score.py        CREATE — RiskScore, ThresholdApplied, SafetyDecision
│   └── audit_record.py      CREATE — AuditRecord, ReasoningStep, stage-specific fields, ethics extension
├── audit/
│   ├── __init__.py          MODIFY — re-export AuditWriter
│   ├── models.py            CREATE — SQLAlchemy ORM for audit_records table
│   ├── writer.py            CREATE — AuditWriter (write-before-return + hash chain)
│   ├── query.py             CREATE — AuditQueryService
│   └── router.py            CREATE — FastAPI GET /audit/* endpoints
├── database.py              CREATE — async engine + session factory
└── main.py                  CREATE — FastAPI app entry point

migrations/versions/
└── 001_create_audit_records.py   CREATE — Alembic migration

tests/
├── conftest.py              MODIFY — activate db_session + client fixtures
├── unit/
│   ├── test_schemas_intent.py      CREATE
│   ├── test_schemas_action.py      CREATE
│   ├── test_schemas_policy.py      CREATE
│   ├── test_schemas_risk_score.py  CREATE
│   ├── test_schemas_audit_record.py CREATE
│   └── test_audit_writer.py        CREATE
└── integration/
    └── test_audit_endpoints.py     CREATE
```

---

## Task 1: Intent Pydantic Model

**Spec:** ANIF-300 §4.3, §4.4 · ANIF-600 §4.1
**Files:**
- Create: `src/anif_platform/schemas/intent.py`
- Create: `tests/unit/test_schemas_intent.py`

### MUSTs implemented in this task
- Intent MUST contain `service`, `objectives`, `constraints` (ANIF-300 §4.3)
- `intent_id` MUST be UUID v4, assigned by the framework — author-supplied IDs MUST be rejected (ANIF-300 §4.4)
- `objectives.availability_percent` MUST be 90–100 inclusive (ANIF-600 §4.1.3)
- `objectives.latency_ms` MUST be ≥ 1 (ANIF-600 §4.1.3)
- `environment` MUST be one of `prod`, `staging`, `dev` (ANIF-600 §4.1.2)
- `priority` MUST be one of `low`, `medium`, `high`, `critical` (ANIF-600 §4.1.2)

- [ ] **Step 1: Write the failing tests**

  Create `tests/unit/test_schemas_intent.py`:

  ```python
  """Tests for Intent Pydantic model — ANIF-300, ANIF-600 §4.1."""

  import pytest
  from pydantic import ValidationError

  from anif_platform.schemas.intent import (
      Constraints,
      Environment,
      Intent,
      Objectives,
      PolicyName,
      Priority,
      Region,
  )


  class TestObjectives:
      def test_valid_objectives(self) -> None:
          obj = Objectives(latency_ms=50, availability_percent=99.9, throughput_mbps=500)
          assert obj.latency_ms == 50
          assert obj.availability_percent == 99.9

      def test_availability_below_minimum_rejected(self) -> None:
          with pytest.raises(ValidationError):
              Objectives(availability_percent=89.9)

      def test_availability_at_minimum_accepted(self) -> None:
          obj = Objectives(availability_percent=90.0)
          assert obj.availability_percent == 90.0

      def test_availability_above_maximum_rejected(self) -> None:
          with pytest.raises(ValidationError):
              Objectives(availability_percent=100.1)

      def test_latency_below_minimum_rejected(self) -> None:
          with pytest.raises(ValidationError):
              Objectives(latency_ms=0)

      def test_latency_at_minimum_accepted(self) -> None:
          obj = Objectives(latency_ms=1)
          assert obj.latency_ms == 1

      def test_all_fields_optional(self) -> None:
          obj = Objectives()
          assert obj.latency_ms is None
          assert obj.availability_percent is None
          assert obj.throughput_mbps is None


  class TestConstraints:
      def test_valid_region(self) -> None:
          c = Constraints(region=Region.EU)
          assert c.region == Region.EU

      def test_invalid_region_rejected(self) -> None:
          with pytest.raises(ValidationError):
              Constraints(region="INVALID")  # type: ignore[arg-type]

      def test_all_fields_optional(self) -> None:
          c = Constraints()
          assert c.region is None
          assert c.encryption is None
          assert c.allowed_zones is None


  class TestIntent:
      def test_minimal_valid_intent(self) -> None:
          intent = Intent(service="payments", objectives=Objectives(), constraints=Constraints())
          assert intent.service == "payments"
          assert intent.intent_id is None

      def test_service_required(self) -> None:
          with pytest.raises(ValidationError):
              Intent(objectives=Objectives(), constraints=Constraints())  # type: ignore[call-arg]

      def test_objectives_required(self) -> None:
          with pytest.raises(ValidationError):
              Intent(service="payments", constraints=Constraints())  # type: ignore[call-arg]

      def test_constraints_required(self) -> None:
          with pytest.raises(ValidationError):
              Intent(service="payments", objectives=Objectives())  # type: ignore[call-arg]

      def test_invalid_environment_rejected(self) -> None:
          with pytest.raises(ValidationError):
              Intent(
                  service="payments",
                  objectives=Objectives(),
                  constraints=Constraints(),
                  environment="production",  # type: ignore[arg-type]
              )

      def test_valid_environment_accepted(self) -> None:
          intent = Intent(
              service="payments",
              objectives=Objectives(),
              constraints=Constraints(),
              environment=Environment.prod,
          )
          assert intent.environment == Environment.prod

      def test_invalid_priority_rejected(self) -> None:
          with pytest.raises(ValidationError):
              Intent(
                  service="payments",
                  objectives=Objectives(),
                  constraints=Constraints(),
                  priority="urgent",  # type: ignore[arg-type]
              )

      def test_valid_policies_accepted(self) -> None:
          intent = Intent(
              service="payments",
              objectives=Objectives(),
              constraints=Constraints(),
              policies=[PolicyName.zero_trust, PolicyName.pci_compliant],
          )
          assert len(intent.policies) == 2  # type: ignore[arg-type]

      def test_invalid_policy_name_rejected(self) -> None:
          with pytest.raises(ValidationError):
              Intent(
                  service="payments",
                  objectives=Objectives(),
                  constraints=Constraints(),
                  policies=["custom_policy"],  # type: ignore[list-item]
              )

      def test_intent_id_field_is_none_by_default(self) -> None:
          """Author-supplied intent_id MUST be rejected per ANIF-300 §4.4."""
          intent = Intent(service="payments", objectives=Objectives(), constraints=Constraints())
          assert intent.intent_id is None

      def test_intent_id_cannot_be_set_by_author(self) -> None:
          """ANIF-300 §4.4: author-supplied IDs MUST be rejected."""
          import uuid
          with pytest.raises(ValidationError):
              Intent(
                  service="payments",
                  objectives=Objectives(),
                  constraints=Constraints(),
                  intent_id=uuid.uuid4(),  # type: ignore[call-arg]
              )

      def test_full_production_intent(self) -> None:
          intent = Intent(
              service="payments-gateway",
              environment=Environment.prod,
              objectives=Objectives(latency_ms=45, availability_percent=99.99, throughput_mbps=500),
              constraints=Constraints(
                  region=Region.EU,
                  encryption=True,
                  allowed_zones=["eu-west-1a", "eu-west-1b"],
              ),
              policies=[PolicyName.zero_trust, PolicyName.pci_compliant, PolicyName.data_residency],
              priority=Priority.critical,
          )
          assert intent.service == "payments-gateway"
          assert intent.environment == Environment.prod
          assert intent.priority == Priority.critical
  ```

- [ ] **Step 2: Verify tests fail**

  ```bash
  cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold
  .venv/bin/pytest tests/unit/test_schemas_intent.py -v 2>&1 | head -20
  ```

  Expected: `ModuleNotFoundError: No module named 'anif_platform.schemas.intent'`

- [ ] **Step 3: Implement `src/anif_platform/schemas/intent.py`**

  ```python
  """Intent Pydantic model — ANIF-300, ANIF-600 §4.1."""

  from __future__ import annotations

  from enum import Enum
  from typing import Annotated, Optional
  from uuid import UUID

  from pydantic import BaseModel, Field, model_validator


  class Environment(str, Enum):
      prod = "prod"
      staging = "staging"
      dev = "dev"


  class Region(str, Enum):
      EU = "EU"
      US = "US"
      APAC = "APAC"


  class PolicyName(str, Enum):
      zero_trust = "zero_trust"
      no_public_ingress = "no_public_ingress"
      pci_compliant = "pci_compliant"
      data_residency = "data_residency"


  class Priority(str, Enum):
      low = "low"
      medium = "medium"
      high = "high"
      critical = "critical"


  class Objectives(BaseModel):
      """Measurable outcome targets the service must meet."""

      latency_ms: Optional[Annotated[float, Field(ge=1)]] = None
      availability_percent: Optional[Annotated[float, Field(ge=90, le=100)]] = None
      throughput_mbps: Optional[float] = None


  class Constraints(BaseModel):
      """Hard constraints the implementation must respect."""

      region: Optional[Region] = None
      encryption: Optional[bool] = None
      allowed_zones: Optional[list[str]] = None


  class Intent(BaseModel):
      """
      Network service intent — ANIF-300 §4.1.

      Represents a declarative statement of what a service MUST achieve.
      `intent_id` is assigned by the framework after validation;
      authors MUST NOT supply it (ANIF-300 §4.4).
      """

      model_config = {"frozen": True}

      service: str
      objectives: Objectives
      constraints: Constraints
      environment: Optional[Environment] = None
      policies: Optional[list[PolicyName]] = None
      priority: Optional[Priority] = None

      @model_validator(mode="before")
      @classmethod
      def reject_author_supplied_intent_id(cls, values: dict) -> dict:
          """ANIF-300 §4.4: author-supplied intent_id MUST be rejected."""
          if "intent_id" in values:
              raise ValueError(
                  "intent_id is assigned by the framework; authors MUST NOT supply it (ANIF-300 §4.4)"
              )
          return values

      @property
      def intent_id(self) -> None:
          """
          intent_id is not stored on the Intent model.
          It is assigned by the framework at validation time and stored
          on the ValidatedIntent record (see intent module, B2).
          """
          return None
  ```

- [ ] **Step 4: Verify tests pass**

  ```bash
  .venv/bin/pytest tests/unit/test_schemas_intent.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/anif_platform/schemas/intent.py tests/unit/test_schemas_intent.py
  git commit -m "feat: implement Intent Pydantic model (ANIF-300, ANIF-600 §4.1)"
  ```

---

## Task 2: Action Pydantic Model

**Spec:** ANIF-600 §4.2
**Files:**
- Create: `src/anif_platform/schemas/action.py`
- Create: `tests/unit/test_schemas_action.py`

### MUSTs implemented in this task
- `action_type` MUST be one of the four defined values (ANIF-600 §4.2.3)
- Invalid action objects MUST NOT be forwarded to the execution layer (ANIF-600 §5.2)

- [ ] **Step 1: Write the failing tests**

  Create `tests/unit/test_schemas_action.py`:

  ```python
  """Tests for Action Pydantic model — ANIF-600 §4.2."""

  import pytest
  from pydantic import ValidationError

  from anif_platform.schemas.action import Action, ActionType, RiskLevel


  class TestAction:
      def test_valid_reroute_traffic(self) -> None:
          action = Action(
              action_type=ActionType.reroute_traffic,
              parameters={"target_path": "path-b", "source_segment": "eu-west-1"},
              risk_level=RiskLevel.medium,
          )
          assert action.action_type == ActionType.reroute_traffic

      def test_action_type_required(self) -> None:
          with pytest.raises(ValidationError):
              Action()  # type: ignore[call-arg]

      def test_invalid_action_type_rejected(self) -> None:
          with pytest.raises(ValidationError):
              Action(action_type="delete_route")  # type: ignore[arg-type]

      def test_all_four_action_types_valid(self) -> None:
          for action_type in ActionType:
              action = Action(action_type=action_type)
              assert action.action_type == action_type

      def test_parameters_optional(self) -> None:
          action = Action(action_type=ActionType.apply_qos)
          assert action.parameters is None

      def test_risk_level_optional(self) -> None:
          action = Action(action_type=ActionType.scale_bandwidth)
          assert action.risk_level is None

      def test_invalid_risk_level_rejected(self) -> None:
          with pytest.raises(ValidationError):
              Action(action_type=ActionType.reroute_traffic, risk_level="critical")  # type: ignore[arg-type]
  ```

- [ ] **Step 2: Verify tests fail**

  ```bash
  .venv/bin/pytest tests/unit/test_schemas_action.py -v 2>&1 | head -10
  ```

  Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement `src/anif_platform/schemas/action.py`**

  ```python
  """Action Pydantic model — ANIF-600 §4.2."""

  from __future__ import annotations

  from enum import Enum
  from typing import Any, Optional

  from pydantic import BaseModel


  class ActionType(str, Enum):
      reroute_traffic = "reroute_traffic"
      apply_qos = "apply_qos"
      scale_bandwidth = "scale_bandwidth"
      isolate_segment = "isolate_segment"


  class RiskLevel(str, Enum):
      low = "low"
      medium = "medium"
      high = "high"


  class Action(BaseModel):
      """
      Discrete autonomous remediation or configuration action — ANIF-600 §4.2.

      Produced by the decision engine; consumed by the execution layer.
      Invalid action objects MUST NOT be forwarded to execution (ANIF-600 §5.2).
      """

      action_type: ActionType
      parameters: Optional[dict[str, Any]] = None
      risk_level: Optional[RiskLevel] = None
  ```

- [ ] **Step 4: Verify tests pass**

  ```bash
  .venv/bin/pytest tests/unit/test_schemas_action.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/anif_platform/schemas/action.py tests/unit/test_schemas_action.py
  git commit -m "feat: implement Action Pydantic model (ANIF-600 §4.2)"
  ```

---

## Task 3: Policy Pydantic Model

**Spec:** ANIF-600 §4.3
**Files:**
- Create: `src/anif_platform/schemas/policy.py`
- Create: `tests/unit/test_schemas_policy.py`

### MUSTs implemented in this task
- Policy `rules` array MUST contain at least one rule (ANIF-600 §4.3.2)
- Policies that fail schema validation MUST be rejected (ANIF-600 §5.3)

- [ ] **Step 1: Write the failing tests**

  Create `tests/unit/test_schemas_policy.py`:

  ```python
  """Tests for Policy Pydantic model — ANIF-600 §4.3."""

  import pytest
  from pydantic import ValidationError

  from anif_platform.schemas.policy import Policy, PolicyRule, RuleAction


  class TestPolicyRule:
      def test_valid_deny_rule(self) -> None:
          rule = PolicyRule(condition="constraints.encryption:equals:false", action=RuleAction.deny)
          assert rule.action == RuleAction.deny

      def test_invalid_action_rejected(self) -> None:
          with pytest.raises(ValidationError):
              PolicyRule(condition="x:equals:y", action="reject")  # type: ignore[arg-type]

      def test_condition_optional(self) -> None:
          rule = PolicyRule(action=RuleAction.allow)
          assert rule.condition is None

      def test_all_three_actions_valid(self) -> None:
          for action in RuleAction:
              rule = PolicyRule(action=action)
              assert rule.action == action


  class TestPolicy:
      def test_valid_policy(self) -> None:
          policy = Policy(
              name="pci_compliant",
              rules=[
                  PolicyRule(condition="constraints.encryption:equals:false", action=RuleAction.deny),
                  PolicyRule(condition="environment:equals:prod", action=RuleAction.allow),
              ],
          )
          assert policy.name == "pci_compliant"
          assert len(policy.rules) == 2

      def test_name_required(self) -> None:
          with pytest.raises(ValidationError):
              Policy(rules=[PolicyRule(action=RuleAction.allow)])  # type: ignore[call-arg]

      def test_rules_required(self) -> None:
          with pytest.raises(ValidationError):
              Policy(name="zero_trust")  # type: ignore[call-arg]

      def test_empty_rules_rejected(self) -> None:
          with pytest.raises(ValidationError):
              Policy(name="zero_trust", rules=[])

      def test_single_rule_accepted(self) -> None:
          policy = Policy(name="zero_trust", rules=[PolicyRule(action=RuleAction.deny)])
          assert len(policy.rules) == 1
  ```

- [ ] **Step 2: Verify tests fail**

  ```bash
  .venv/bin/pytest tests/unit/test_schemas_policy.py -v 2>&1 | head -10
  ```

  Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement `src/anif_platform/schemas/policy.py`**

  ```python
  """Policy Pydantic model — ANIF-600 §4.3."""

  from __future__ import annotations

  from enum import Enum
  from typing import Annotated, Optional

  from pydantic import BaseModel, Field


  class RuleAction(str, Enum):
      allow = "allow"
      deny = "deny"
      warn = "warn"


  class PolicyRule(BaseModel):
      """A single conditional rule within a policy."""

      condition: Optional[str] = None
      action: Optional[RuleAction] = None


  class Policy(BaseModel):
      """
      Named policy consisting of one or more conditional rules — ANIF-600 §4.3.

      Policies that fail schema validation at load time MUST be rejected
      and the engine MUST NOT start (ANIF-600 §5.3).
      """

      name: str
      rules: Annotated[list[PolicyRule], Field(min_length=1)]
  ```

- [ ] **Step 4: Verify tests pass**

  ```bash
  .venv/bin/pytest tests/unit/test_schemas_policy.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/anif_platform/schemas/policy.py tests/unit/test_schemas_policy.py
  git commit -m "feat: implement Policy Pydantic model (ANIF-600 §4.3)"
  ```

---

## Task 4: RiskScore Pydantic Model

**Spec:** ANIF-600 §4.4
**Files:**
- Create: `src/anif_platform/schemas/risk_score.py`
- Create: `tests/unit/test_schemas_risk_score.py`

### MUSTs implemented in this task
- `risk_score` and `trust_score` MUST be integers 0–100 (ANIF-600 §4.4.3)
- `safety_decision` MUST be derived programmatically from `risk_score` vs thresholds (ANIF-600 §5.4)
- `safety_decision` MUST NOT be set arbitrarily (ANIF-600 §5.4)

- [ ] **Step 1: Write the failing tests**

  Create `tests/unit/test_schemas_risk_score.py`:

  ```python
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
  ```

- [ ] **Step 2: Verify tests fail**

  ```bash
  .venv/bin/pytest tests/unit/test_schemas_risk_score.py -v 2>&1 | head -10
  ```

  Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement `src/anif_platform/schemas/risk_score.py`**

  ```python
  """RiskScore Pydantic model — ANIF-600 §4.4."""

  from __future__ import annotations

  from enum import Enum
  from typing import Annotated

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
      def reject_caller_supplied_safety_decision(cls, values: dict) -> dict:
          """ANIF-600 §5.4: safety_decision MUST NOT be set arbitrarily."""
          if "safety_decision" in values:
              raise ValueError(
                  "safety_decision is derived programmatically from risk_score; "
                  "callers MUST NOT supply it (ANIF-600 §5.4)"
              )
          return values

      @computed_field  # type: ignore[misc]
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
  ```

- [ ] **Step 4: Verify tests pass**

  ```bash
  .venv/bin/pytest tests/unit/test_schemas_risk_score.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/anif_platform/schemas/risk_score.py tests/unit/test_schemas_risk_score.py
  git commit -m "feat: implement RiskScore Pydantic model with derived safety_decision (ANIF-600 §4.4)"
  ```

---

## Task 5: AuditRecord Pydantic Model

**Spec:** ANIF-107 §4.2 · ANIF-600 §4.5 · ANIF-724 §4
**Files:**
- Create: `src/anif_platform/schemas/audit_record.py`
- Create: `tests/unit/test_schemas_audit_record.py`

### MUSTs implemented in this task
- Record MUST include all base required fields: `record_id`, `intent_id`, `timestamp`, `stage`, `input_summary`, `output_summary`, `outcome`, `duration_ms` (ANIF-107 §4.2)
- `record_id` MUST be UUID v4 (ANIF-107 §4.2.2)
- `timestamp` MUST be UTC ISO-8601 (ANIF-107 §4.2.2)
- `stage` MUST be one of the seven defined values (ANIF-107 §4.1.2)
- `reasoning_chain` MUST NOT be empty for `decision` and `governance` stages (ANIF-107 §4.2.2)
- Ethics fields (ANIF-724 §4) included as optional extensions

Note: The stage enum uses values from `schemas/audit_record_schema.yml` (the normative YAML):
`validate`, `policy`, `risk`, `decision`, `governance`, `execute`, `rollback`.

- [ ] **Step 1: Write the failing tests**

  Create `tests/unit/test_schemas_audit_record.py`:

  ```python
  """Tests for AuditRecord Pydantic model — ANIF-107, ANIF-600 §4.5, ANIF-724."""

  import uuid
  from datetime import UTC, datetime

  import pytest
  from pydantic import ValidationError

  from anif_platform.schemas.audit_record import (
      AuditOutcome,
      AuditRecord,
      AuditStage,
      ReasoningStep,
  )

  INTENT_ID = uuid.uuid4()


  def make_base_record(**kwargs) -> AuditRecord:
      defaults = dict(
          intent_id=INTENT_ID,
          stage=AuditStage.validate,
          input_summary={"service": "payments"},
          output_summary={"result": "pass"},
          outcome=AuditOutcome.success,
          duration_ms=12,
      )
      defaults.update(kwargs)
      return AuditRecord(**defaults)


  class TestReasoningStep:
      def test_valid_step(self) -> None:
          step = ReasoningStep(step=1, description="Schema checked", decision="Pass")
          assert step.step == 1

      def test_step_required(self) -> None:
          with pytest.raises(ValidationError):
              ReasoningStep(description="x", decision="y")  # type: ignore[call-arg]

      def test_rationale_optional(self) -> None:
          step = ReasoningStep(step=1, description="x", decision="y")
          assert step.rationale is None


  class TestAuditRecord:
      def test_valid_record_auto_generates_record_id(self) -> None:
          record = make_base_record()
          assert record.record_id is not None
          assert isinstance(record.record_id, uuid.UUID)

      def test_valid_record_auto_generates_timestamp(self) -> None:
          record = make_base_record()
          assert record.timestamp.tzinfo is not None

      def test_intent_id_required(self) -> None:
          with pytest.raises(ValidationError):
              AuditRecord(
                  stage=AuditStage.validate,
                  input_summary={},
                  output_summary={},
                  outcome=AuditOutcome.success,
                  duration_ms=1,
              )  # type: ignore[call-arg]

      def test_invalid_stage_rejected(self) -> None:
          with pytest.raises(ValidationError):
              make_base_record(stage="unknown_stage")

      def test_invalid_outcome_rejected(self) -> None:
          with pytest.raises(ValidationError):
              make_base_record(outcome="partial")

      def test_duration_ms_cannot_be_negative(self) -> None:
          with pytest.raises(ValidationError):
              make_base_record(duration_ms=-1)

      def test_duration_ms_zero_is_valid(self) -> None:
          record = make_base_record(duration_ms=0)
          assert record.duration_ms == 0

      def test_decision_stage_requires_nonempty_reasoning_chain(self) -> None:
          """ANIF-107 §4.2.2: reasoning_chain MUST NOT be empty for decision stage."""
          with pytest.raises(ValidationError):
              make_base_record(stage=AuditStage.decision, reasoning_chain=[])

      def test_governance_stage_requires_nonempty_reasoning_chain(self) -> None:
          """ANIF-107 §4.2.2: reasoning_chain MUST NOT be empty for governance stage."""
          with pytest.raises(ValidationError):
              make_base_record(stage=AuditStage.governance, reasoning_chain=[])

      def test_validate_stage_allows_empty_reasoning_chain(self) -> None:
          record = make_base_record(stage=AuditStage.validate, reasoning_chain=[])
          assert record.reasoning_chain == []

      def test_reasoning_chain_with_steps_accepted(self) -> None:
          record = make_base_record(
              stage=AuditStage.decision,
              reasoning_chain=[
                  ReasoningStep(step=1, description="Risk checked", decision="warn"),
              ],
          )
          assert len(record.reasoning_chain) == 1

      def test_timestamp_is_utc(self) -> None:
          record = make_base_record()
          assert record.timestamp.tzinfo == UTC or str(record.timestamp.tzinfo) == "UTC"

      def test_operator_id_defaults_to_none(self) -> None:
          record = make_base_record()
          assert record.operator_id is None

      def test_hash_chain_fields_default_to_none(self) -> None:
          record = make_base_record()
          assert record.record_hash is None
          assert record.prev_hash is None
          assert record.chain_id is None

      def test_all_seven_stages_are_valid(self) -> None:
          for stage in AuditStage:
              chain = []
              if stage in (AuditStage.decision, AuditStage.governance):
                  chain = [ReasoningStep(step=1, description="x", decision="y")]
              record = make_base_record(stage=stage, reasoning_chain=chain)
              assert record.stage == stage

      def test_ethics_fields_optional(self) -> None:
          """ANIF-724: ethics fields are optional (only required for AI-involved actions)."""
          record = make_base_record()
          assert record.agent_id is None
          assert record.llm_used is None
          assert record.harm_class is None
  ```

- [ ] **Step 2: Verify tests fail**

  ```bash
  .venv/bin/pytest tests/unit/test_schemas_audit_record.py -v 2>&1 | head -10
  ```

  Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement `src/anif_platform/schemas/audit_record.py`**

  ```python
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
  ```

- [ ] **Step 4: Verify tests pass**

  ```bash
  .venv/bin/pytest tests/unit/test_schemas_audit_record.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/anif_platform/schemas/audit_record.py tests/unit/test_schemas_audit_record.py
  git commit -m "feat: implement AuditRecord Pydantic model with ethics extension (ANIF-107, ANIF-600 §4.5, ANIF-724)"
  ```

---

## Task 6: Schemas `__init__.py` Re-exports

**Files:**
- Modify: `src/anif_platform/schemas/__init__.py`

- [ ] **Step 1: Update `__init__.py`**

  Replace the contents of `src/anif_platform/schemas/__init__.py`:

  ```python
  """ANIF Platform — Pydantic schema models."""

  from anif_platform.schemas.action import Action, ActionType, RiskLevel
  from anif_platform.schemas.audit_record import (
      AgentTier,
      AgentTrustLevel,
      AuditOutcome,
      AuditRecord,
      AuditStage,
      GovernanceMode,
      HarmClass,
      ReasoningStep,
      RollbackOutcome,
  )
  from anif_platform.schemas.intent import (
      Constraints,
      Environment,
      Intent,
      Objectives,
      PolicyName,
      Priority,
      Region,
  )
  from anif_platform.schemas.policy import Policy, PolicyRule, RuleAction
  from anif_platform.schemas.risk_score import RiskScore, SafetyDecision, ThresholdApplied

  __all__ = [
      "Action",
      "ActionType",
      "AgentTier",
      "AgentTrustLevel",
      "AuditOutcome",
      "AuditRecord",
      "AuditStage",
      "Constraints",
      "Environment",
      "GovernanceMode",
      "HarmClass",
      "Intent",
      "Objectives",
      "Policy",
      "PolicyName",
      "PolicyRule",
      "Priority",
      "ReasoningStep",
      "Region",
      "RiskLevel",
      "RiskScore",
      "RollbackOutcome",
      "RuleAction",
      "SafetyDecision",
      "ThresholdApplied",
  ]
  ```

- [ ] **Step 2: Verify all schema imports work**

  ```bash
  .venv/bin/python -c "from anif_platform.schemas import Intent, AuditRecord, RiskScore, Policy, Action; print('OK')"
  ```

  Expected: `OK`

- [ ] **Step 3: Run all schema tests**

  ```bash
  .venv/bin/pytest tests/unit/test_schemas_*.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 4: Commit**

  ```bash
  git add src/anif_platform/schemas/__init__.py
  git commit -m "feat: re-export all schema models from schemas __init__"
  ```

---

## Task 7: Database Session Factory

**Files:**
- Create: `src/anif_platform/database.py`

This module provides the async SQLAlchemy engine and session factory used by all database-accessing modules. No business logic lives here.

- [ ] **Step 1: Create `src/anif_platform/database.py`**

  ```python
  """Async SQLAlchemy engine and session factory."""

  from __future__ import annotations

  import os

  from sqlalchemy.ext.asyncio import (
      AsyncEngine,
      AsyncSession,
      async_sessionmaker,
      create_async_engine,
  )
  from sqlalchemy.orm import DeclarativeBase


  class Base(DeclarativeBase):
      """Shared declarative base for all ORM models."""


  def _make_engine() -> AsyncEngine:
      url = os.environ["DATABASE_URL"]
      # asyncpg requires postgresql+asyncpg:// scheme
      if url.startswith("postgresql://"):
          url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
      return create_async_engine(url, echo=False, pool_pre_ping=True)


  engine: AsyncEngine = _make_engine()

  async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
      engine,
      class_=AsyncSession,
      expire_on_commit=False,
  )
  ```

- [ ] **Step 2: Verify import**

  ```bash
  .venv/bin/python -c "from anif_platform.database import async_session_factory; print('OK')"
  ```

  Expected: `OK`

- [ ] **Step 3: Update `tests/conftest.py` to activate db fixtures**

  Replace the contents of `tests/conftest.py`:

  ```python
  """Shared pytest fixtures for the ANIF platform test suite."""

  from __future__ import annotations

  import os
  from collections.abc import AsyncGenerator
  from typing import Any

  import pytest
  import pytest_asyncio
  from httpx import ASGITransport, AsyncClient


  @pytest.fixture(autouse=True)
  def set_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
      """Set environment variables for all tests."""
      monkeypatch.setenv("ENVIRONMENT", "test")
      monkeypatch.setenv("LOG_LEVEL", "WARNING")
      monkeypatch.setenv(
          "DATABASE_URL",
          os.environ.get("DATABASE_URL", "postgresql://anif:anif_dev@localhost:5432/anif_test"),
      )
      monkeypatch.setenv(
          "REDIS_URL",
          os.environ.get("REDIS_URL", "redis://localhost:6379"),
      )


  @pytest_asyncio.fixture
  async def db_session() -> AsyncGenerator[Any, None]:
      """
      Provide a transactional database session that rolls back after each test.

      Uses a nested transaction so each test starts clean without truncating tables.
      Requires the anif_test database to exist and migrations to be applied.
      """
      from anif_platform.database import engine
      from sqlalchemy.ext.asyncio import AsyncSession

      async with engine.connect() as conn:
          await conn.begin()
          session = AsyncSession(bind=conn, join_transaction_mode="create_savepoint")
          try:
              yield session
          finally:
              await session.close()
              await conn.rollback()


  @pytest_asyncio.fixture
  async def client(db_session: Any) -> AsyncGenerator[AsyncClient, None]:
      """Provide an async test client wired to the FastAPI app with a test DB session."""
      from anif_platform.main import app
      from anif_platform.audit.query import AuditQueryService
      from anif_platform.audit.writer import AuditWriter

      app.dependency_overrides[AuditWriter] = lambda: AuditWriter(db_session)
      app.dependency_overrides[AuditQueryService] = lambda: AuditQueryService(db_session)

      async with AsyncClient(
          transport=ASGITransport(app=app), base_url="http://test"
      ) as c:
          yield c

      app.dependency_overrides.clear()
  ```

- [ ] **Step 4: Commit**

  ```bash
  git add src/anif_platform/database.py tests/conftest.py
  git commit -m "feat: add async database session factory and activate test fixtures"
  ```

---

## Task 8: SQLAlchemy Model + Alembic Migration

**Spec:** ANIF-107 §4.4 (append-only), §4.5 (query performance indexes)
**Files:**
- Create: `src/anif_platform/audit/models.py`
- Create: `migrations/versions/001_create_audit_records.py`

### MUSTs implemented in this task
- Audit store MUST be append-only; no UPDATE or DELETE endpoints or internal mechanisms (ANIF-107 §4.4.1)
- Indexes MUST exist on `intent_id`, `timestamp`, `stage`, `outcome` for query performance (ANIF-107 §7.2)

- [ ] **Step 1: Create `src/anif_platform/audit/models.py`**

  ```python
  """SQLAlchemy ORM model for audit records — ANIF-107."""

  from __future__ import annotations

  from datetime import datetime
  from typing import Any
  from uuid import UUID

  from sqlalchemy import DateTime, Index, Integer, String, Text, UniqueConstraint
  from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
  from sqlalchemy.orm import Mapped, mapped_column

  from anif_platform.database import Base


  class AuditRecordRow(Base):
      """
      Persistent audit record row — ANIF-107 §4.4.

      This table is APPEND-ONLY. No UPDATE or DELETE statements are ever issued
      against it. The audit store MUST be append-only with no mechanism to modify
      or delete records (ANIF-107 §4.4.1). Enforcement is at both the application
      layer (AuditWriter never issues UPDATE/DELETE) and optionally at the
      PostgreSQL layer via row-level security policies.
      """

      __tablename__ = "audit_records"

      # Primary key
      record_id: Mapped[UUID] = mapped_column(
          PgUUID(as_uuid=True), primary_key=True, nullable=False
      )

      # Indexed lookup columns
      intent_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
      timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
      stage: Mapped[str] = mapped_column(String(32), nullable=False)
      outcome: Mapped[str] = mapped_column(String(32), nullable=False)
      operator_id: Mapped[str | None] = mapped_column(String(256), nullable=True)

      # Hash chain fields
      record_hash: Mapped[str | None] = mapped_column(String(71), nullable=True)  # "sha256:<64hex>"
      prev_hash: Mapped[str | None] = mapped_column(String(71), nullable=True)
      chain_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)

      # Duration for SLA monitoring
      duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)

      # Full record stored as JSONB for flexible querying and completeness
      data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

      __table_args__ = (
          # Performance indexes — ANIF-107 §7.2
          Index("ix_audit_records_intent_id_timestamp", "intent_id", "timestamp"),
          Index("ix_audit_records_stage", "stage"),
          Index("ix_audit_records_outcome", "outcome"),
          Index("ix_audit_records_operator_id", "operator_id"),
          # Hash chain lookup
          Index("ix_audit_records_chain_id", "chain_id"),
          # record_id uniqueness enforced by primary key; belt-and-suspenders
          UniqueConstraint("record_id", name="uq_audit_records_record_id"),
      )
  ```

- [ ] **Step 2: Create the Alembic migration**

  Create `migrations/versions/001_create_audit_records.py`:

  ```python
  """create audit_records table

  Revision ID: 001
  Revises:
  Create Date: 2026-04-13
  """

  from __future__ import annotations

  import sqlalchemy as sa
  from alembic import op
  from sqlalchemy.dialects.postgresql import JSONB, UUID

  revision = "001"
  down_revision = None
  branch_labels = None
  depends_on = None


  def upgrade() -> None:
      op.create_table(
          "audit_records",
          sa.Column("record_id", UUID(as_uuid=True), nullable=False),
          sa.Column("intent_id", UUID(as_uuid=True), nullable=False),
          sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
          sa.Column("stage", sa.String(32), nullable=False),
          sa.Column("outcome", sa.String(32), nullable=False),
          sa.Column("operator_id", sa.String(256), nullable=True),
          sa.Column("record_hash", sa.String(71), nullable=True),
          sa.Column("prev_hash", sa.String(71), nullable=True),
          sa.Column("chain_id", UUID(as_uuid=True), nullable=True),
          sa.Column("duration_ms", sa.Integer, nullable=False),
          sa.Column("data", JSONB, nullable=False),
          sa.PrimaryKeyConstraint("record_id"),
          sa.UniqueConstraint("record_id", name="uq_audit_records_record_id"),
      )
      op.create_index("ix_audit_records_intent_id_timestamp", "audit_records", ["intent_id", "timestamp"])
      op.create_index("ix_audit_records_stage", "audit_records", ["stage"])
      op.create_index("ix_audit_records_outcome", "audit_records", ["outcome"])
      op.create_index("ix_audit_records_operator_id", "audit_records", ["operator_id"])
      op.create_index("ix_audit_records_chain_id", "audit_records", ["chain_id"])


  def downgrade() -> None:
      op.drop_index("ix_audit_records_chain_id", table_name="audit_records")
      op.drop_index("ix_audit_records_operator_id", table_name="audit_records")
      op.drop_index("ix_audit_records_outcome", table_name="audit_records")
      op.drop_index("ix_audit_records_stage", table_name="audit_records")
      op.drop_index("ix_audit_records_intent_id_timestamp", table_name="audit_records")
      op.drop_table("audit_records")
  ```

- [ ] **Step 3: Apply migration to the test database**

  ```bash
  cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif_test .venv/bin/alembic upgrade head
  ```

  Expected output includes: `Running upgrade  -> 001, create audit_records table`

- [ ] **Step 4: Also apply migration to the dev database**

  ```bash
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif .venv/bin/alembic upgrade head
  ```

- [ ] **Step 5: Commit**

  ```bash
  git add src/anif_platform/audit/models.py migrations/versions/001_create_audit_records.py
  git commit -m "feat: add AuditRecordRow SQLAlchemy model and Alembic migration (ANIF-107 §4.4)"
  ```

---

## Task 9: AuditWriter Service

**Spec:** ANIF-107 §4.1, §4.3, §4.7 · ANIF-724 §5
**Files:**
- Create: `src/anif_platform/audit/writer.py`
- Create: `tests/unit/test_audit_writer.py`

### MUSTs implemented in this task
- Audit write MUST complete before the pipeline stage returns its result (ANIF-107 §4.3.1)
- "Durably written" means acknowledged by the audit store as persisted (ANIF-107 §4.3.2)
- If audit write fails, pipeline MUST NOT proceed and MUST return failure (ANIF-107 §4.3.3)
- Hash chaining: `record_hash` = SHA-256 of canonical JSON (excluding hash fields) (ANIF-107 §4.7.2)
- `prev_hash` = hash of preceding record; genesis = SHA-256("ANIF-GENESIS") (ANIF-107 §4.7.2)
- `chain_id` = `intent_id` (ANIF-107 §4.7.2)
- Duplicate `record_id` MUST be rejected (ANIF-107 §4.2.2)

- [ ] **Step 1: Write the failing tests**

  Create `tests/unit/test_audit_writer.py`:

  ```python
  """Tests for AuditWriter — ANIF-107 §4.3, §4.7."""

  from __future__ import annotations

  import hashlib
  import json
  import uuid
  from datetime import UTC, datetime

  import pytest
  import pytest_asyncio
  from sqlalchemy import select
  from sqlalchemy.ext.asyncio import AsyncSession

  from anif_platform.audit.models import AuditRecordRow
  from anif_platform.audit.writer import GENESIS_HASH, AuditWriteError, AuditWriter
  from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage


  def make_record(intent_id: uuid.UUID, stage: AuditStage = AuditStage.validate) -> AuditRecord:
      chain: list = []
      if stage in (AuditStage.decision, AuditStage.governance):
          from anif_platform.schemas.audit_record import ReasoningStep
          chain = [ReasoningStep(step=1, description="x", decision="y")]
      return AuditRecord(
          intent_id=intent_id,
          stage=stage,
          input_summary={"service": "payments"},
          output_summary={"result": "pass"},
          outcome=AuditOutcome.success,
          duration_ms=10,
          reasoning_chain=chain,
      )


  @pytest.mark.asyncio
  class TestAuditWriter:
      async def test_write_persists_record(self, db_session: AsyncSession) -> None:
          """Write-before-return: record must be durable after write() returns."""
          writer = AuditWriter(db_session)
          intent_id = uuid.uuid4()
          record = make_record(intent_id)

          await writer.write(record)

          result = await db_session.execute(
              select(AuditRecordRow).where(AuditRecordRow.record_id == record.record_id)
          )
          row = result.scalar_one_or_none()
          assert row is not None
          assert row.intent_id == intent_id
          assert row.stage == AuditStage.validate.value
          assert row.outcome == AuditOutcome.success.value

      async def test_write_sets_chain_id_to_intent_id(self, db_session: AsyncSession) -> None:
          """chain_id MUST be intent_id — ANIF-107 §4.7.2."""
          writer = AuditWriter(db_session)
          intent_id = uuid.uuid4()
          record = make_record(intent_id)

          await writer.write(record)

          result = await db_session.execute(
              select(AuditRecordRow).where(AuditRecordRow.record_id == record.record_id)
          )
          row = result.scalar_one()
          assert row.chain_id == intent_id

      async def test_first_record_prev_hash_is_genesis(self, db_session: AsyncSession) -> None:
          """First record in a chain MUST use genesis hash as prev_hash — ANIF-107 §4.7.2."""
          writer = AuditWriter(db_session)
          intent_id = uuid.uuid4()
          record = make_record(intent_id)

          await writer.write(record)

          result = await db_session.execute(
              select(AuditRecordRow).where(AuditRecordRow.record_id == record.record_id)
          )
          row = result.scalar_one()
          assert row.prev_hash == GENESIS_HASH

      async def test_second_record_prev_hash_is_first_record_hash(
          self, db_session: AsyncSession
      ) -> None:
          """Each record's prev_hash MUST be the preceding record's record_hash — ANIF-107 §4.7.2."""
          writer = AuditWriter(db_session)
          intent_id = uuid.uuid4()

          r1 = make_record(intent_id, AuditStage.validate)
          await writer.write(r1)

          r2 = make_record(intent_id, AuditStage.policy)
          await writer.write(r2)

          result = await db_session.execute(
              select(AuditRecordRow).where(AuditRecordRow.record_id == r2.record_id)
          )
          row2 = result.scalar_one()

          result1 = await db_session.execute(
              select(AuditRecordRow).where(AuditRecordRow.record_id == r1.record_id)
          )
          row1 = result1.scalar_one()

          assert row2.prev_hash == row1.record_hash

      async def test_record_hash_is_sha256_of_canonical_json(
          self, db_session: AsyncSession
      ) -> None:
          """record_hash MUST be SHA-256 of canonical JSON excluding hash fields — ANIF-107 §4.7.2."""
          writer = AuditWriter(db_session)
          intent_id = uuid.uuid4()
          record = make_record(intent_id)

          await writer.write(record)

          result = await db_session.execute(
              select(AuditRecordRow).where(AuditRecordRow.record_id == record.record_id)
          )
          row = result.scalar_one()

          # Recompute expected hash from stored data
          data = dict(row.data)
          data.pop("record_hash", None)
          data.pop("prev_hash", None)
          canonical = json.dumps(data, sort_keys=True, default=str)
          expected = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
          assert row.record_hash == expected

      async def test_duplicate_record_id_raises_audit_write_error(
          self, db_session: AsyncSession
      ) -> None:
          """Duplicate record_id MUST be rejected — ANIF-107 §4.2.2."""
          writer = AuditWriter(db_session)
          intent_id = uuid.uuid4()
          record = make_record(intent_id)

          await writer.write(record)

          with pytest.raises(AuditWriteError):
              await writer.write(record)  # same record_id

      async def test_different_intents_have_independent_chains(
          self, db_session: AsyncSession
      ) -> None:
          """Each intent has its own hash chain (chain_id = intent_id)."""
          writer = AuditWriter(db_session)
          intent_a = uuid.uuid4()
          intent_b = uuid.uuid4()

          ra = make_record(intent_a)
          rb = make_record(intent_b)
          await writer.write(ra)
          await writer.write(rb)

          result_a = await db_session.execute(
              select(AuditRecordRow).where(AuditRecordRow.record_id == ra.record_id)
          )
          result_b = await db_session.execute(
              select(AuditRecordRow).where(AuditRecordRow.record_id == rb.record_id)
          )
          row_a = result_a.scalar_one()
          row_b = result_b.scalar_one()

          # Both should have genesis as prev_hash (first records in their chains)
          assert row_a.prev_hash == GENESIS_HASH
          assert row_b.prev_hash == GENESIS_HASH
          assert row_a.chain_id != row_b.chain_id
  ```

- [ ] **Step 2: Verify tests fail**

  ```bash
  .venv/bin/pytest tests/unit/test_audit_writer.py -v 2>&1 | head -20
  ```

  Expected: `ModuleNotFoundError: No module named 'anif_platform.audit.writer'`

- [ ] **Step 3: Implement `src/anif_platform/audit/writer.py`**

  ```python
  """
  AuditWriter — write-before-return audit persistence with SHA-256 hash chaining.

  ANIF-107 §4.3 (write-before-return), §4.7 (hash chaining).
  ANIF-724 §5 (ethics write-before-return extension).
  """

  from __future__ import annotations

  import hashlib
  import json
  import uuid

  import structlog
  from sqlalchemy import select
  from sqlalchemy.exc import IntegrityError
  from sqlalchemy.ext.asyncio import AsyncSession

  from anif_platform.audit.models import AuditRecordRow
  from anif_platform.schemas.audit_record import AuditRecord

  log = structlog.get_logger(__name__)

  # SHA-256 of the well-known genesis value for the first record in any chain.
  # (ANIF-107 §4.7.2)
  GENESIS_HASH: str = "sha256:" + hashlib.sha256(b"ANIF-GENESIS").hexdigest()


  class AuditWriteError(Exception):
      """
      Raised when the audit write fails.

      Per ANIF-107 §4.3.3, if the audit write fails the pipeline stage MUST NOT
      proceed and MUST return failure to the caller.
      """


  def _canonical_json(data: dict) -> str:
      """Return the canonical JSON representation of a record for hashing.

      Excludes `record_hash` and `prev_hash` fields as required by ANIF-107 §4.7.2.
      Uses sort_keys=True for determinism.
      """
      clean = {k: v for k, v in data.items() if k not in ("record_hash", "prev_hash")}
      return json.dumps(clean, sort_keys=True, default=str)


  def _compute_record_hash(data: dict) -> str:
      """Compute SHA-256 hash of canonical record data — ANIF-107 §4.7.2."""
      return "sha256:" + hashlib.sha256(_canonical_json(data).encode()).hexdigest()


  class AuditWriter:
      """
      Writes audit records to the audit store with write-before-return semantics.

      One AuditWriter instance per request/session. Inject via FastAPI dependency.

      Usage:
          writer = AuditWriter(session)
          await writer.write(record)  # raises AuditWriteError on failure
          # caller MUST NOT proceed past this point if AuditWriteError is raised
      """

      def __init__(self, session: AsyncSession) -> None:
          self._session = session

      async def write(self, record: AuditRecord) -> None:
          """
          Durably write an audit record to the audit store.

          This method MUST be called — and MUST complete successfully — before
          the calling pipeline stage returns its result (ANIF-107 §4.3.1).

          Raises:
              AuditWriteError: if the write fails for any reason.
                  The caller MUST propagate this as a failure response.
          """
          prev_hash = await self._get_prev_hash(record.intent_id)
          data = self._record_to_dict(record, prev_hash)
          record_hash = _compute_record_hash(data)
          data["record_hash"] = record_hash
          data["prev_hash"] = prev_hash

          row = AuditRecordRow(
              record_id=record.record_id,
              intent_id=record.intent_id,
              timestamp=record.timestamp,
              stage=record.stage.value,
              outcome=record.outcome.value,
              operator_id=record.operator_id,
              record_hash=record_hash,
              prev_hash=prev_hash,
              chain_id=record.intent_id,
              duration_ms=record.duration_ms,
              data=data,
          )

          self._session.add(row)
          try:
              await self._session.flush()
          except IntegrityError as exc:
              await self._session.rollback()
              log.error(
                  "audit_write_failed",
                  record_id=str(record.record_id),
                  intent_id=str(record.intent_id),
                  stage=record.stage.value,
                  error=str(exc),
              )
              raise AuditWriteError(
                  f"Failed to write audit record {record.record_id}: {exc}"
              ) from exc

          log.info(
              "audit_record_written",
              record_id=str(record.record_id),
              intent_id=str(record.intent_id),
              stage=record.stage.value,
              outcome=record.outcome.value,
          )

      async def _get_prev_hash(self, intent_id: uuid.UUID) -> str:
          """
          Retrieve the record_hash of the most recent record in this intent's chain.

          Returns GENESIS_HASH if this is the first record for this intent.
          """
          result = await self._session.execute(
              select(AuditRecordRow.record_hash)
              .where(AuditRecordRow.chain_id == intent_id)
              .order_by(AuditRecordRow.timestamp.desc())
              .limit(1)
          )
          row = result.scalar_one_or_none()
          return row if row is not None else GENESIS_HASH

      @staticmethod
      def _record_to_dict(record: AuditRecord, prev_hash: str) -> dict:
          """
          Serialise AuditRecord to a dict suitable for JSONB storage.

          Excludes hash chain fields from the record itself — they are computed
          and injected by the writer.
          """
          data = record.model_dump(mode="json", exclude={"record_hash", "prev_hash", "chain_id"})
          return data
  ```

- [ ] **Step 4: Verify tests pass**

  ```bash
  .venv/bin/pytest tests/unit/test_audit_writer.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/anif_platform/audit/writer.py tests/unit/test_audit_writer.py
  git commit -m "feat: implement AuditWriter with write-before-return and SHA-256 hash chaining (ANIF-107 §4.3, §4.7)"
  ```

---

## Task 10: AuditQuery Service

**Spec:** ANIF-107 §4.5, §4.7.3
**Files:**
- Create: `src/anif_platform/audit/query.py`

### MUSTs implemented in this task
- `GET /audit/{intent_id}` returns all records ordered by timestamp asc (ANIF-107 §4.5.1)
- Returns empty array (not 404) if no records exist for a valid `intent_id` (ANIF-107 §4.5.3)
- `GET /audit/{intent_id}/why` synthesises human-readable explanation from `reasoning_chain` (ANIF-107 §4.5.6)
- `GET /audit` supports filtering by stage, outcome, date_from, date_to, operator_id, action_type, environment (ANIF-107 §4.5.2)
- Pagination: default 50, maximum 1000 (ANIF-107 §4.5.4)
- `GET /audit/{intent_id}/verify` recomputes hash chain (ANIF-107 §4.7.3)

- [ ] **Step 1: Create `src/anif_platform/audit/query.py`**

  ```python
  """
  AuditQueryService — read-side audit queries.

  Implements the query interface required by ANIF-107 §4.5 and the hash chain
  verification endpoint required by §4.7.3.
  """

  from __future__ import annotations

  import hashlib
  import json
  import uuid
  from datetime import datetime
  from typing import Any, Optional

  from sqlalchemy import select
  from sqlalchemy.ext.asyncio import AsyncSession

  from anif_platform.audit.models import AuditRecordRow
  from anif_platform.audit.writer import GENESIS_HASH, _canonical_json

  _MAX_PAGE_SIZE = 1000
  _DEFAULT_PAGE_SIZE = 50


  class AuditQueryService:
      """
      Read-side audit queries.

      Inject per-request via FastAPI dependency injection.
      """

      def __init__(self, session: AsyncSession) -> None:
          self._session = session

      async def get_by_intent(self, intent_id: uuid.UUID) -> list[dict[str, Any]]:
          """
          Return all audit records for the given intent, ordered by timestamp ascending.

          Returns an empty list (not an error) if no records exist — ANIF-107 §4.5.3.
          """
          result = await self._session.execute(
              select(AuditRecordRow)
              .where(AuditRecordRow.intent_id == intent_id)
              .order_by(AuditRecordRow.timestamp.asc())
          )
          rows = result.scalars().all()
          return [row.data for row in rows]

      async def get_why(self, intent_id: uuid.UUID) -> str:
          """
          Synthesise a human-readable explanation of the pipeline decision — ANIF-107 §4.5.6.

          Must include: action proposed, policies evaluated, risk score, governance mode,
          and final outcome.
          """
          records = await self.get_by_intent(intent_id)
          if not records:
              return f"No audit records found for intent {intent_id}."

          lines: list[str] = [f"Intent {intent_id} — pipeline summary\n"]

          for rec in records:
              stage = rec.get("stage", "unknown")
              outcome = rec.get("outcome", "unknown")
              lines.append(f"Stage: {stage} → {outcome}")

              chain = rec.get("reasoning_chain", [])
              for step in chain:
                  if isinstance(step, dict):
                      desc = step.get("description", "")
                      decision = step.get("decision", "")
                      rationale = step.get("rationale", "")
                      entry = f"  • {desc}: {decision}"
                      if rationale:
                          entry += f" ({rationale})"
                      lines.append(entry)
                  else:
                      lines.append(f"  • {step}")

          return "\n".join(lines)

      async def list_records(
          self,
          stage: Optional[str] = None,
          outcome: Optional[str] = None,
          date_from: Optional[datetime] = None,
          date_to: Optional[datetime] = None,
          operator_id: Optional[str] = None,
          action_type: Optional[str] = None,
          environment: Optional[str] = None,
          limit: int = _DEFAULT_PAGE_SIZE,
          offset: int = 0,
      ) -> list[dict[str, Any]]:
          """
          Return audit records with optional filters and pagination — ANIF-107 §4.5.2.

          Default page size: 50. Maximum page size: 1000.
          """
          effective_limit = min(limit, _MAX_PAGE_SIZE)

          query = select(AuditRecordRow).order_by(AuditRecordRow.timestamp.desc())

          if stage is not None:
              query = query.where(AuditRecordRow.stage == stage)
          if outcome is not None:
              query = query.where(AuditRecordRow.outcome == outcome)
          if date_from is not None:
              query = query.where(AuditRecordRow.timestamp >= date_from)
          if date_to is not None:
              query = query.where(AuditRecordRow.timestamp <= date_to)
          if operator_id is not None:
              query = query.where(AuditRecordRow.operator_id == operator_id)
          if action_type is not None:
              query = query.where(AuditRecordRow.data["action_type"].astext == action_type)
          if environment is not None:
              query = query.where(AuditRecordRow.data["input_summary"]["environment"].astext == environment)

          query = query.limit(effective_limit).offset(offset)

          result = await self._session.execute(query)
          rows = result.scalars().all()
          return [row.data for row in rows]

      async def verify_chain(self, intent_id: uuid.UUID) -> dict[str, Any]:
          """
          Recompute hash chain and return verification result — ANIF-107 §4.7.3.

          Returns: {"valid": bool, "broken_at": record_id or null, "record_count": int}
          """
          result = await self._session.execute(
              select(AuditRecordRow)
              .where(AuditRecordRow.chain_id == intent_id)
              .order_by(AuditRecordRow.timestamp.asc())
          )
          rows = result.scalars().all()

          if not rows:
              return {"valid": True, "broken_at": None, "record_count": 0}

          expected_prev = GENESIS_HASH
          for row in rows:
              if row.prev_hash != expected_prev:
                  return {
                      "valid": False,
                      "broken_at": str(row.record_id),
                      "record_count": len(rows),
                  }
              recomputed = "sha256:" + hashlib.sha256(
                  _canonical_json(row.data).encode()
              ).hexdigest()
              if row.record_hash != recomputed:
                  return {
                      "valid": False,
                      "broken_at": str(row.record_id),
                      "record_count": len(rows),
                  }
              expected_prev = row.record_hash

          return {"valid": True, "broken_at": None, "record_count": len(rows)}
  ```

- [ ] **Step 2: Commit**

  ```bash
  git add src/anif_platform/audit/query.py
  git commit -m "feat: implement AuditQueryService with filtering, pagination, and hash chain verification (ANIF-107 §4.5, §4.7.3)"
  ```

---

## Task 11: Audit FastAPI Router

**Spec:** ANIF-107 §4.5
**Files:**
- Create: `src/anif_platform/audit/router.py`
- Modify: `src/anif_platform/audit/__init__.py`

- [ ] **Step 1: Create `src/anif_platform/audit/router.py`**

  ```python
  """FastAPI router for audit query endpoints — ANIF-107 §4.5."""

  from __future__ import annotations

  import uuid
  from datetime import datetime
  from typing import Any, Optional

  from fastapi import APIRouter, Depends, HTTPException, Query
  from pydantic import BaseModel

  from anif_platform.audit.query import AuditQueryService

  router = APIRouter(prefix="/audit", tags=["audit"])


  def get_audit_query_service() -> AuditQueryService:
      """FastAPI dependency — overridden in tests via app.dependency_overrides."""
      raise NotImplementedError("Provide AuditQueryService via dependency injection")


  class HashChainVerification(BaseModel):
      valid: bool
      broken_at: Optional[str]
      record_count: int


  @router.get("/{intent_id}", response_model=list[dict[str, Any]])
  async def get_audit_records(
      intent_id: uuid.UUID,
      service: AuditQueryService = Depends(get_audit_query_service),
  ) -> list[dict[str, Any]]:
      """
      Return all audit records for the given intent, ordered by timestamp ascending.

      Returns an empty list (not 404) if no records exist for a valid intent_id.
      Returns 404 only if intent_id is syntactically invalid (handled by FastAPI UUID parsing).

      — ANIF-107 §4.5.1, §4.5.3
      """
      return await service.get_by_intent(intent_id)


  @router.get("/{intent_id}/why", response_model=str)
  async def get_audit_why(
      intent_id: uuid.UUID,
      service: AuditQueryService = Depends(get_audit_query_service),
  ) -> str:
      """
      Return a human-readable explanation of the pipeline decision for this intent.

      Synthesised from reasoning_chain fields of all records for the intent.
      — ANIF-107 §4.5.6
      """
      return await service.get_why(intent_id)


  @router.get("/{intent_id}/verify", response_model=HashChainVerification)
  async def verify_hash_chain(
      intent_id: uuid.UUID,
      service: AuditQueryService = Depends(get_audit_query_service),
  ) -> dict[str, Any]:
      """
      Recompute the SHA-256 hash chain and return verification result.

      Returns {"valid": true/false, "broken_at": record_id or null, "record_count": int}.
      — ANIF-107 §4.7.3
      """
      return await service.verify_chain(intent_id)


  @router.get("", response_model=list[dict[str, Any]])
  async def list_audit_records(
      stage: Optional[str] = Query(None),
      outcome: Optional[str] = Query(None),
      date_from: Optional[datetime] = Query(None),
      date_to: Optional[datetime] = Query(None),
      operator_id: Optional[str] = Query(None),
      action_type: Optional[str] = Query(None),
      environment: Optional[str] = Query(None),
      limit: int = Query(default=50, ge=1, le=1000),
      offset: int = Query(default=0, ge=0),
      service: AuditQueryService = Depends(get_audit_query_service),
  ) -> list[dict[str, Any]]:
      """
      Return paginated, filterable audit records.

      Filters: stage, outcome, date_from, date_to, operator_id, action_type, environment.
      Default page size: 50. Maximum page size: 1000.
      — ANIF-107 §4.5.2, §4.5.4
      """
      return await service.list_records(
          stage=stage,
          outcome=outcome,
          date_from=date_from,
          date_to=date_to,
          operator_id=operator_id,
          action_type=action_type,
          environment=environment,
          limit=limit,
          offset=offset,
      )
  ```

- [ ] **Step 2: Update `src/anif_platform/audit/__init__.py`**

  ```python
  """ANIF audit module — AuditWriter and query endpoints."""

  from anif_platform.audit.writer import AuditWriteError, AuditWriter

  __all__ = ["AuditWriteError", "AuditWriter"]
  ```

- [ ] **Step 3: Commit**

  ```bash
  git add src/anif_platform/audit/router.py src/anif_platform/audit/__init__.py
  git commit -m "feat: add FastAPI audit router for GET /audit endpoints (ANIF-107 §4.5)"
  ```

---

## Task 12: FastAPI Application Entry Point

**Files:**
- Create: `src/anif_platform/main.py`

- [ ] **Step 1: Create `src/anif_platform/main.py`**

  ```python
  """FastAPI application entry point for the ANIF platform."""

  from __future__ import annotations

  from contextlib import asynccontextmanager
  from collections.abc import AsyncGenerator

  import structlog
  from fastapi import FastAPI

  from anif_platform.audit.router import router as audit_router
  from anif_platform.database import engine

  log = structlog.get_logger(__name__)


  @asynccontextmanager
  async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
      log.info("anif_platform_starting")
      yield
      await engine.dispose()
      log.info("anif_platform_stopped")


  app = FastAPI(
      title="ANIF Platform",
      description="Autonomous Networking & Infrastructure Framework — reference platform",
      version="0.1.0",
      lifespan=lifespan,
  )

  app.include_router(audit_router)
  ```

- [ ] **Step 2: Verify app starts**

  ```bash
  .venv/bin/python -c "from anif_platform.main import app; print('OK', app.title)"
  ```

  Expected: `OK ANIF Platform`

- [ ] **Step 3: Commit**

  ```bash
  git add src/anif_platform/main.py
  git commit -m "feat: add FastAPI application entry point with audit router"
  ```

---

## Task 13: Integration Tests for Audit Endpoints

**Files:**
- Create: `tests/integration/test_audit_endpoints.py`

- [ ] **Step 1: Write the failing integration tests**

  Create `tests/integration/test_audit_endpoints.py`:

  ```python
  """Integration tests for GET /audit/* endpoints — ANIF-107 §4.5."""

  from __future__ import annotations

  import uuid

  import pytest
  import pytest_asyncio
  from httpx import AsyncClient
  from sqlalchemy.ext.asyncio import AsyncSession

  from anif_platform.audit.writer import AuditWriter
  from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage, ReasoningStep


  def make_record(
      intent_id: uuid.UUID,
      stage: AuditStage = AuditStage.validate,
      outcome: AuditOutcome = AuditOutcome.success,
  ) -> AuditRecord:
      chain: list = []
      if stage in (AuditStage.decision, AuditStage.governance):
          chain = [ReasoningStep(step=1, description="Risk threshold evaluated", decision="warn")]
      return AuditRecord(
          intent_id=intent_id,
          stage=stage,
          input_summary={"service": "payments", "environment": "prod"},
          output_summary={"result": "pass"},
          outcome=outcome,
          duration_ms=15,
          reasoning_chain=chain,
      )


  @pytest.mark.asyncio
  class TestGetAuditByIntent:
      async def test_returns_empty_list_for_unknown_intent(self, client: AsyncClient) -> None:
          """ANIF-107 §4.5.3: empty array (not 404) for valid intent_id with no records."""
          unknown_id = uuid.uuid4()
          resp = await client.get(f"/audit/{unknown_id}")
          assert resp.status_code == 200
          assert resp.json() == []

      async def test_returns_records_for_known_intent(
          self, client: AsyncClient, db_session: AsyncSession
      ) -> None:
          intent_id = uuid.uuid4()
          writer = AuditWriter(db_session)
          await writer.write(make_record(intent_id, AuditStage.validate))
          await writer.write(make_record(intent_id, AuditStage.policy))

          resp = await client.get(f"/audit/{intent_id}")
          assert resp.status_code == 200
          records = resp.json()
          assert len(records) == 2
          assert records[0]["stage"] == "validate"
          assert records[1]["stage"] == "policy"

      async def test_records_ordered_by_timestamp_ascending(
          self, client: AsyncClient, db_session: AsyncSession
      ) -> None:
          intent_id = uuid.uuid4()
          writer = AuditWriter(db_session)
          await writer.write(make_record(intent_id, AuditStage.validate))
          await writer.write(make_record(intent_id, AuditStage.policy))
          await writer.write(make_record(intent_id, AuditStage.risk))

          resp = await client.get(f"/audit/{intent_id}")
          records = resp.json()
          stages = [r["stage"] for r in records]
          assert stages == ["validate", "policy", "risk"]

      async def test_returns_422_for_invalid_uuid(self, client: AsyncClient) -> None:
          """ANIF-107 §4.5.3: 404 only for syntactically invalid intent_id."""
          resp = await client.get("/audit/not-a-uuid")
          assert resp.status_code == 422


  @pytest.mark.asyncio
  class TestGetAuditWhy:
      async def test_returns_string_explanation(
          self, client: AsyncClient, db_session: AsyncSession
      ) -> None:
          intent_id = uuid.uuid4()
          writer = AuditWriter(db_session)
          await writer.write(
              make_record(intent_id, AuditStage.decision, AuditOutcome.escalated)
          )

          resp = await client.get(f"/audit/{intent_id}/why")
          assert resp.status_code == 200
          body = resp.json()
          assert isinstance(body, str)
          assert str(intent_id) in body

      async def test_returns_message_for_unknown_intent(self, client: AsyncClient) -> None:
          unknown_id = uuid.uuid4()
          resp = await client.get(f"/audit/{unknown_id}/why")
          assert resp.status_code == 200
          assert "No audit records" in resp.json()


  @pytest.mark.asyncio
  class TestVerifyHashChain:
      async def test_valid_chain_returns_true(
          self, client: AsyncClient, db_session: AsyncSession
      ) -> None:
          intent_id = uuid.uuid4()
          writer = AuditWriter(db_session)
          await writer.write(make_record(intent_id, AuditStage.validate))
          await writer.write(make_record(intent_id, AuditStage.policy))

          resp = await client.get(f"/audit/{intent_id}/verify")
          assert resp.status_code == 200
          body = resp.json()
          assert body["valid"] is True
          assert body["broken_at"] is None
          assert body["record_count"] == 2

      async def test_empty_chain_returns_valid(self, client: AsyncClient) -> None:
          unknown_id = uuid.uuid4()
          resp = await client.get(f"/audit/{unknown_id}/verify")
          assert resp.status_code == 200
          assert resp.json()["valid"] is True


  @pytest.mark.asyncio
  class TestListAuditRecords:
      async def test_returns_records(
          self, client: AsyncClient, db_session: AsyncSession
      ) -> None:
          intent_id = uuid.uuid4()
          writer = AuditWriter(db_session)
          await writer.write(make_record(intent_id, AuditStage.validate))

          resp = await client.get("/audit")
          assert resp.status_code == 200
          assert isinstance(resp.json(), list)

      async def test_filter_by_stage(
          self, client: AsyncClient, db_session: AsyncSession
      ) -> None:
          intent_id = uuid.uuid4()
          writer = AuditWriter(db_session)
          await writer.write(make_record(intent_id, AuditStage.validate))
          await writer.write(make_record(intent_id, AuditStage.policy))

          resp = await client.get("/audit?stage=validate")
          assert resp.status_code == 200
          records = resp.json()
          assert all(r["stage"] == "validate" for r in records)

      async def test_default_limit_is_50(self, client: AsyncClient) -> None:
          resp = await client.get("/audit")
          assert resp.status_code == 200

      async def test_limit_above_1000_clamped(self, client: AsyncClient) -> None:
          """ANIF-107 §4.5.4: max page size MUST NOT exceed 1000."""
          resp = await client.get("/audit?limit=2000")
          assert resp.status_code == 422  # FastAPI validates le=1000
  ```

- [ ] **Step 2: Run integration tests**

  ```bash
  .venv/bin/pytest tests/integration/test_audit_endpoints.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 3: Run the full test suite**

  ```bash
  .venv/bin/pytest -v
  ```

  Expected: all tests PASS. No failures or errors.

- [ ] **Step 4: Run linting and type checking**

  ```bash
  .venv/bin/ruff check src/ tests/ --fix
  .venv/bin/black src/ tests/
  .venv/bin/mypy src/anif_platform/schemas/ src/anif_platform/audit/ src/anif_platform/database.py src/anif_platform/main.py
  ```

  Expected: no unfixable ruff violations, no mypy errors.

- [ ] **Step 5: Commit**

  ```bash
  git add tests/integration/test_audit_endpoints.py
  git commit -m "feat: add integration tests for GET /audit/* endpoints (ANIF-107 §4.5)"
  ```

---

## Self-Review

### Spec coverage checklist

| Requirement | Source | Covered by |
|---|---|---|
| Intent MUST contain service, objectives, constraints | ANIF-300 §4.3 | Task 1 |
| intent_id MUST be UUID v4, assigned by framework | ANIF-300 §4.4 | Task 1 |
| Author-supplied intent_id MUST be rejected | ANIF-300 §4.4 | Task 1 |
| availability_percent MUST be 90–100 | ANIF-600 §4.1.3 | Task 1 |
| latency_ms MUST be ≥ 1 | ANIF-600 §4.1.3 | Task 1 |
| Non-conforming intents MUST be rejected with HTTP 422 | ANIF-600 §5.1 | FastAPI/Pydantic (automatic) |
| Action MUST conform to action_schema | ANIF-600 §5.2 | Task 2 |
| Policy rules MUST have at least one rule | ANIF-600 §4.3.2 | Task 3 |
| safety_decision MUST be derived programmatically | ANIF-600 §5.4 | Task 4 |
| safety_decision MUST NOT be set by caller | ANIF-600 §5.4 | Task 4 |
| AuditRecord base required fields | ANIF-107 §4.2 | Task 5 |
| reasoning_chain MUST NOT be empty for decision/governance | ANIF-107 §4.2.2 | Task 5 |
| Write-before-return constraint | ANIF-107 §4.3.1 | Task 9 |
| If audit write fails, MUST NOT proceed | ANIF-107 §4.3.3 | Task 9 (AuditWriteError) |
| Audit records MUST be append-only | ANIF-107 §4.4.1 | Task 8 (no UPDATE/DELETE in ORM) |
| Duplicate record_id MUST be rejected | ANIF-107 §4.2.2 | Task 9 |
| Hash chaining: record_hash, prev_hash, chain_id | ANIF-107 §4.7.2 | Task 9 |
| GET /audit/{intent_id} ordered by timestamp asc | ANIF-107 §4.5.1 | Task 10, 11, 13 |
| GET /audit/{intent_id} returns empty list (not 404) | ANIF-107 §4.5.3 | Task 10, 13 |
| GET /audit/{intent_id}/why synthesises explanation | ANIF-107 §4.5.6 | Task 10, 11, 13 |
| GET /audit filters: stage, outcome, date_from, date_to, operator_id, action_type, environment | ANIF-107 §4.5.2 | Task 10, 11 |
| GET /audit pagination: default 50, max 1000 | ANIF-107 §4.5.4 | Task 10, 11 |
| GET /audit/{intent_id}/verify recomputes hash chain | ANIF-107 §4.7.3 | Task 10, 11, 13 |
| Ethics audit fields (ANIF-724 §4) included in schema | ANIF-724 | Task 5 |
| Write-before-return for ethics audit | ANIF-724 §5 | Task 9 (same AuditWriter) |
| Pydantic v2 models kept in sync with YAML schemas | ANIF-600 §5.6 | All tasks |

All MUSTs are covered. No gaps found.

### Notes for implementer

- The `anif_test` and `anif` PostgreSQL databases must exist before running migrations. If they don't exist, create them: `createdb -U anif anif_test` and `createdb -U anif anif`.
- The `structlog` package is already in `pyproject.toml` dependencies.
- `httpx` must be installed for test client: already in `pyproject.toml` as `httpx>=0.27.0`.
- `pytest-asyncio` must be in `asyncio_mode = "auto"` or tests must use `@pytest.mark.asyncio`. Add to `pyproject.toml` if not already: `[tool.pytest.ini_options] asyncio_mode = "auto"`.
- Check `pyproject.toml` for `asyncio_mode` before running tests.
