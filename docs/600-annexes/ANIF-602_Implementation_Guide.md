# ANIF-602: Implementation Guide

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-602                                           |
| Series       | Annex                                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-200, ANIF-300, ANIF-604                       |

---

## Abstract

This document is the practical implementation guide for the Autonomous Networking & Infrastructure Framework (ANIF). It provides step-by-step guidance for teams implementing ANIF modules from scratch, including prerequisites, project setup, module-by-module implementation instructions, testing strategy, and common pitfalls. Teams should work through modules in the order presented; each module is designed to be testable in isolation before integration.

---

## 1. Introduction

### 1.1 Purpose

ANIF specifications describe behaviour in normative terms. This guide translates those specifications into concrete implementation tasks with Python code guidance, test patterns, and integration sequences. The target audience is a software engineering team implementing the ANIF reference prototype or a production derivative.

### 1.2 Technology Stack

| Component       | Technology                     |
|-----------------|--------------------------------|
| Language        | Python 3.11+                   |
| Web framework   | FastAPI (latest)               |
| Data validation | Pydantic v2                    |
| Schema format   | YAML (PyYAML or ruamel.yaml)   |
| Testing         | pytest 7+                      |
| Containerisation| Docker + docker-compose        |
| Linting         | ruff                           |
| Type checking   | mypy (strict)                  |

### 1.3 Document Scope

This guide covers modules in implementation order:

1. Intent validation
2. Policy engine
3. Risk scoring
4. Decision engine
5. Governance gate
6. Action executors
7. Audit service
8. Orchestrator
9. Feedback analysis

---

## 2. Normative References

- ANIF-200: System Architecture
- ANIF-301: Intent Validation
- ANIF-302: Policy Engine
- ANIF-303: Risk Scoring
- ANIF-304: Decision Engine
- ANIF-305: Governance Gate
- ANIF-306: Action Execution
- ANIF-107: Audit and Governance
- ANIF-600: Schema Reference
- ANIF-604: Reference Prototype Guide

---

## 3. Terms and Definitions

**Module** — a self-contained Python package within `src/anif/` implementing a single pipeline stage.

**Adapter** — a class that wraps a specific network device API or simulation, implementing the `ActionAdapter` protocol.

**Mock adapter** — an adapter that simulates network operations deterministically, used in testing and the reference prototype.

**Fixture** — a static JSON or YAML file in `tests/fixtures/` used as deterministic test input.

**Deterministic** — a function that produces the same output given the same inputs, with no dependency on time, random state, or external mutable state.

---

## 4. Prerequisites and Environment Setup

### 4.1 System Requirements

- Python 3.11 or higher (`python --version`)
- Docker 24+ and docker-compose v2 (`docker compose version`)
- Git 2.40+
- 4 GB RAM minimum for full docker-compose stack
- Ports 8000 (API) and 5432 (optional: Postgres for persistent audit) available

### 4.2 Project Setup

```bash
# Clone the repository
git clone https://github.com/your-org/anif-prototype.git
cd anif-prototype

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Verify installation
python -c "import anif; print('OK')"
pytest --co -q   # list tests without running them
```

### 4.3 Environment Variables

Create a `.env` file at the project root:

```bash
ANIF_ENV=dev
ANIF_LOG_LEVEL=DEBUG
ANIF_RISK_PROFILE=default
ANIF_AUDIT_BACKEND=memory   # or "postgres" for persistence
ANIF_MOCK_ADAPTER_SUCCESS_RATE=1.0   # 1.0 = always succeed
```

### 4.4 Quick Start: Docker Compose

```bash
# Start all services
docker compose up --build

# In another terminal, submit a test intent
curl -s -X POST http://localhost:8000/validate-intent \
  -H "Content-Type: application/json" \
  -d '{"service":"test","objectives":{},"constraints":{}}' | python -m json.tool

# Run the full test suite
docker compose exec api pytest tests/ -v
```

The API auto-documentation is available at `http://localhost:8000/docs` once the container is running.

---

## 5. Module Implementation Guide

### 5.1 Module 1: Intent Validation

**Start here.** This module is the most isolated — it has no dependencies on other ANIF modules.

#### 5.1.1 What to Implement

- Schema loader: reads `schemas/intent_schema.yml` at startup
- Pydantic v2 model: `Intent` with all sub-models (`Objectives`, `Constraints`)
- Validation service: validates a raw dict against the schema and returns structured errors
- FastAPI endpoint: `POST /validate-intent`
- Audit record writer: writes a record after every validation call

#### 5.1.2 Key Classes

```python
# src/anif/intent/models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class Intent(BaseModel):
    service: str
    environment: Optional[Environment] = None
    objectives: Objectives
    constraints: Constraints
    policies: Optional[List[PolicyName]] = None
    priority: Optional[Priority] = None

# src/anif/intent/validator.py
class IntentValidator:
    def validate(self, raw: dict) -> ValidationResult:
        """Returns ValidationResult with valid:bool, errors:list, warnings:list."""
        ...

# src/anif/intent/router.py  (FastAPI router)
@router.post("/validate-intent")
async def validate_intent(body: dict) -> ResponseEnvelope:
    ...
```

#### 5.1.3 Testing in Isolation

```bash
pytest tests/unit/test_intent_validator.py -v
```

Key test cases:
- Valid minimal intent passes
- Missing `service` field returns 422
- `availability_percent: 85` fails (below minimum 90)
- Unknown environment value fails
- Unknown policy name in `policies` array fails
- Valid intent produces an audit record with `stage: intent_validation` and `outcome: success`

```python
# tests/unit/test_intent_validator.py
import pytest
from anif.intent.validator import IntentValidator

def test_valid_minimal_intent():
    validator = IntentValidator()
    result = validator.validate({"service": "test", "objectives": {}, "constraints": {}})
    assert result.valid is True

def test_invalid_availability():
    validator = IntentValidator()
    result = validator.validate({
        "service": "test",
        "objectives": {"availability_percent": 85},
        "constraints": {}
    })
    assert result.valid is False
    assert any("availability_percent" in e.field for e in result.errors)
```

---

### 5.2 Module 2: Policy Engine

#### 5.2.1 What to Implement

- Policy loader: reads policy YAML files from `schemas/` and/or a configurable policy directory
- Condition parser: parses `field_path:operator:value` strings
- Condition evaluator: resolves a field path against an intent object and applies the operator
- Rule evaluator: evaluates all rules in a policy and returns the aggregate result
- Conflict detector: identifies when two policies produce contradictory outcomes for the same field
- Conflict resolver: applies resolution rules (security_wins, compliance_wins)
- FastAPI endpoint: `POST /evaluate-policy`

#### 5.2.2 Condition Parser Implementation

```python
# src/anif/policy/condition.py
from dataclasses import dataclass
from enum import Enum

class Operator(str, Enum):
    equals = "equals"
    not_equals = "not_equals"
    greater_than = "greater_than"
    less_than = "less_than"
    contains = "contains"
    not_contains = "not_contains"
    in_list = "in_list"
    not_in_list = "not_in_list"

@dataclass
class Condition:
    field_path: str
    operator: Operator
    value: str

def parse_condition(expression: str) -> Condition:
    parts = expression.split(":", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid condition expression: {expression!r}")
    return Condition(
        field_path=parts[0],
        operator=Operator(parts[1]),
        value=parts[2]
    )

def resolve_field(obj: dict, path: str):
    """Resolves a dot-separated field path against a nested dict."""
    keys = path.split(".")
    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current
```

#### 5.2.3 Testing in Isolation

```bash
pytest tests/unit/test_policy_engine.py -v
```

Key test cases:
- `encryption:equals:false` against `{"encryption": false}` returns True
- `region:in_list:EU,US` against `{"region": "APAC"}` returns False
- `latency_ms:less_than:10` against `{"latency_ms": 5}` returns True
- Policy with all-allow rules returns `passed: true`
- Policy with a deny rule returns `passed: false` with the rule cited
- Conflict between deny and allow returns conflict_detected: true
- Resolution rule CR-01 applied: security policy result takes precedence

---

### 5.3 Module 3: Risk Scoring

#### 5.3.1 What to Implement

- Risk factor registry: a list of `RiskFactor` objects, each with a condition and a weight
- Factor evaluator: checks each factor's condition against the intent and telemetry context
- Score accumulator: sums weights, caps at 100
- Threshold applier: compares score to the active threshold profile
- Trust scorer: computes trust from operator credentials and telemetry freshness (simplified: use a static 70 in the prototype)
- FastAPI endpoint: `POST /score-risk`

#### 5.3.2 Risk Factor Registry

Define factors as data, not code:

```python
# src/anif/risk/factors.py
from dataclasses import dataclass
from typing import Callable

@dataclass
class RiskFactor:
    name: str
    weight: int
    condition: Callable[[dict, dict], bool]  # (intent, context) -> bool

RISK_FACTORS: list[RiskFactor] = [
    RiskFactor(
        name="prod environment",
        weight=30,
        condition=lambda intent, ctx: intent.get("environment") == "prod"
    ),
    RiskFactor(
        name="staging environment",
        weight=10,
        condition=lambda intent, ctx: intent.get("environment") == "staging"
    ),
    RiskFactor(
        name="degraded network state",
        weight=20,
        condition=lambda intent, ctx: ctx.get("network_state") == "degraded"
    ),
    RiskFactor(
        name="isolate_segment action",
        weight=25,
        condition=lambda intent, ctx: ctx.get("candidate_action_type") == "isolate_segment"
    ),
    RiskFactor(
        name="policy failure",
        weight=15,
        condition=lambda intent, ctx: ctx.get("policy_passed") is False
    ),
    RiskFactor(
        name="encryption disabled",
        weight=10,
        condition=lambda intent, ctx: intent.get("constraints", {}).get("encryption") is False
    ),
    RiskFactor(
        name="critical priority",
        weight=5,
        condition=lambda intent, ctx: intent.get("priority") == "critical"
    ),
    RiskFactor(
        name="high availability target",
        weight=5,
        condition=lambda intent, ctx:
            (intent.get("objectives", {}).get("availability_percent") or 0) >= 99.9
    ),
]
```

#### 5.3.3 Testing in Isolation

```bash
pytest tests/unit/test_risk_scorer.py -v
```

Key test cases:
- prod intent scores exactly 30 (no other factors)
- prod + degraded + isolate_segment scores exactly 75
- Score of 75 with default thresholds produces `safety_decision: block`
- Score of 45 with default thresholds produces `safety_decision: warn`
- Score of 20 with default thresholds produces `safety_decision: allow`
- Score never exceeds 100 (accumulation capped)
- justification array lists exactly the factors that contributed

---

### 5.4 Module 4: Decision Engine

#### 5.4.1 What to Implement

- Decision resolver: maps (safety_decision, policy_passed, priority) to a decision mode
- Action recommender: given the intent, selects the most appropriate `action_type`
- FastAPI endpoint: `POST /decide`

#### 5.4.2 Decision Resolution Table

| safety_decision | policy_passed | priority | mode          |
|----------------|---------------|----------|---------------|
| allow          | true          | any      | auto_approve  |
| warn           | true          | critical | auto_approve  |
| warn           | true          | non-critical | manual_review |
| warn           | false         | any      | manual_review |
| block          | any           | any      | block         |

#### 5.4.3 Testing in Isolation

```bash
pytest tests/unit/test_decision_engine.py -v
```

Key test cases:
- allow + policy_passed=true → auto_approve
- warn + policy_passed=true + critical → auto_approve (priority override)
- warn + policy_passed=true + high → manual_review
- warn + policy_passed=false + critical → manual_review (policy failure overrides priority)
- block + any → block with recommended_action=null

---

### 5.5 Module 5: Governance Gate

#### 5.5.1 What to Implement

- Governance evaluator: maps decision mode to governance action
- Ticket manager: creates, stores, and retrieves approval tickets
- In-memory ticket store (for prototype); replace with DB for production
- FastAPI endpoints: `POST /governance/check`, `POST /governance/approve/{ticket_id}`, `POST /governance/reject/{ticket_id}`

#### 5.5.2 Governance Logic

```python
# src/anif/governance/gate.py
def evaluate(decision_mode: str, risk_score: int, priority: str) -> GovernanceResult:
    if decision_mode == "auto_approve":
        return GovernanceResult(
            governance_result="approved",
            ticket_id=None,
            approved_by="system:auto"
        )
    elif decision_mode == "manual_review":
        ticket = create_ticket(...)
        return GovernanceResult(
            governance_result="pending",
            ticket_id=ticket.id,
            escalated_to="network-ops-team"
        )
    else:  # block
        return GovernanceResult(
            governance_result="blocked",
            ticket_id=None
        )
```

#### 5.5.3 Testing in Isolation

- auto_approve mode returns `governance_result: approved` with no ticket
- manual_review mode creates a ticket and returns `governance_result: pending`
- Approving a ticket changes its status to `approved`
- Rejecting a ticket changes its status to `rejected`
- Approving an expired ticket returns an error
- Approving a non-existent ticket returns 404

---

### 5.6 Module 6: Action Executors and Mock Adapters

#### 5.6.1 What to Implement

- `ActionAdapter` protocol: defines `execute(action, intent) -> ExecutionResult` and `rollback(execution_id) -> RollbackResult`
- `MockAdapter` base: a deterministic mock that always succeeds (or fails at a configured rate)
- Concrete mock adapters per action type: `MockQosAdapter`, `MockRerouteAdapter`, `MockBandwidthAdapter`, `MockIsolateAdapter`
- Adapter registry: maps action_type strings to adapter instances
- FastAPI endpoints: `POST /execute`, `POST /rollback/{intent_id}`, `GET /execution/{execution_id}`

#### 5.6.2 Adapter Protocol

```python
# src/anif/actions/adapter.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class ActionAdapter(Protocol):
    action_type: str

    def execute(
        self,
        action: dict,
        intent: dict,
        dry_run: bool = False
    ) -> dict:
        """Execute the action. Returns execution result dict."""
        ...

    def rollback(self, execution_id: str) -> dict:
        """Roll back a previous execution. Returns rollback result dict."""
        ...
```

#### 5.6.3 Mock Adapter Implementation Pattern

```python
# src/anif/actions/mock_adapter.py
import hashlib, uuid
from datetime import datetime, timezone

class MockQosAdapter:
    action_type = "apply_qos"

    def execute(self, action: dict, intent: dict, dry_run: bool = False) -> dict:
        execution_id = str(uuid.uuid4())
        # Determinism: success is based on intent hash, not random()
        intent_hash = int(hashlib.md5(str(intent).encode()).hexdigest(), 16)
        success = (intent_hash % 100) < int(
            os.getenv("ANIF_MOCK_ADAPTER_SUCCESS_RATE", "100")
        )
        return {
            "execution_id": execution_id,
            "outcome": "success" if (success or dry_run) else "failure",
            "adapter": "mock_qos_adapter",
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "dry_run": dry_run,
            "rollback_available": True
        }

    def rollback(self, execution_id: str) -> dict:
        return {
            "execution_id": execution_id,
            "rollback_outcome": "success",
            "rolled_back_at": datetime.now(timezone.utc).isoformat()
        }
```

#### 5.6.4 Critical Rule: Every Adapter MUST Implement rollback()

An adapter without a working `rollback()` method MUST NOT be registered. The adapter registry MUST enforce this at registration time:

```python
def register_adapter(adapter: ActionAdapter) -> None:
    if not hasattr(adapter, "rollback"):
        raise ValueError(
            f"Adapter {type(adapter).__name__} must implement rollback(). "
            "Registration rejected."
        )
    _registry[adapter.action_type] = adapter
```

#### 5.6.5 Testing in Isolation

- Each mock adapter's `execute()` returns a valid `ExecutionResult`
- `dry_run=True` always returns `outcome: success` without calling device layer
- `rollback()` returns a valid `RollbackResult`
- Adapter registry raises on registration of adapter without `rollback()`
- Unknown `action_type` returns HTTP 422

---

### 5.7 Module 7: Audit Service

#### 5.7.1 What to Implement

- `AuditRecord` Pydantic model matching `audit_record_schema`
- `AuditWriter`: writes records to the configured backend (memory or Postgres)
- `AuditReader`: retrieves records by `intent_id`
- Narrative generator: converts records into a human-readable `why` explanation
- FastAPI endpoints: `GET /audit/{intent_id}`, `GET /audit/{intent_id}/why`, `GET /audit`

#### 5.7.2 Write Discipline — Critical

The audit writer MUST be called as the last operation before a stage function returns:

```python
# CORRECT — audit written before return
async def evaluate_policy(request: PolicyRequest) -> PolicyResult:
    result = _evaluate(request)
    await audit.write(AuditRecord(
        stage="policy_evaluation",
        outcome="success" if result.passed else "failure",
        ...
    ))
    return result

# INCORRECT — return before audit write
async def evaluate_policy(request: PolicyRequest) -> PolicyResult:
    result = _evaluate(request)
    return result  # audit never written if caller crashes
    await audit.write(...)
```

#### 5.7.3 Testing in Isolation

- Writing a record returns without error and the record is retrievable
- `GET /audit/{intent_id}` returns all records for that intent in chronological order
- `GET /audit/{intent_id}/why` returns a narrative covering all stages
- Writing a record with a duplicate `record_id` raises an error
- Records written by one intent are not returned when querying another intent_id

---

### 5.8 Module 8: Orchestrator

#### 5.8.1 What to Implement

- Pipeline runner: calls modules 1–7 in sequence, passing outputs to subsequent stages
- Halt logic: stops the pipeline when any stage returns `block` or an unrecoverable `failure`
- Stage context propagator: carries `intent_id`, `trace_id`, and telemetry context across stages
- Status store: records per-intent pipeline status for `GET /orchestrate/{intent_id}/status`
- FastAPI endpoints: `POST /orchestrate`, `GET /orchestrate/{intent_id}/status`

#### 5.8.2 Pipeline Runner Pseudocode

```python
async def run_pipeline(intent: dict, dry_run: bool) -> PipelineResult:
    intent_id = str(uuid.uuid4())
    stages = []

    # Stage 1: Validate intent
    val = await intent_validator.validate(intent, intent_id=intent_id)
    stages.append(StageResult(stage="intent_validation", outcome=val.outcome))
    if not val.valid:
        return PipelineResult(pipeline_outcome="failure", halted_at="intent_validation", stages=stages)

    # Stage 2: Evaluate policies
    pol = await policy_engine.evaluate(intent, intent_id=intent_id)
    stages.append(StageResult(stage="policy_evaluation", outcome=pol.outcome))

    # Stage 3: Score risk (requires policy result)
    risk = await risk_scorer.score(intent, policy_result=pol, intent_id=intent_id)
    stages.append(StageResult(stage="risk_scoring", outcome=risk.outcome))
    if risk.safety_decision == "block":
        return PipelineResult(pipeline_outcome="blocked", halted_at="risk", stages=stages)

    # Stage 4: Decide
    decision = await decision_engine.decide(intent, risk_result=risk, policy_result=pol, intent_id=intent_id)
    stages.append(StageResult(stage="decision", outcome=decision.outcome))
    if decision.mode == "block":
        return PipelineResult(pipeline_outcome="blocked", halted_at="decision", stages=stages)

    # Stage 5: Governance
    gov = await governance_gate.check(intent, decision=decision, intent_id=intent_id)
    stages.append(StageResult(stage="governance", outcome=gov.outcome))
    if gov.governance_result == "pending":
        return PipelineResult(pipeline_outcome="escalated", ticket_id=gov.ticket_id, stages=stages)

    # Stage 6: Execute
    exec_result = await executor.execute(decision.recommended_action, intent, dry_run=dry_run, intent_id=intent_id)
    stages.append(StageResult(stage="execution", outcome=exec_result.outcome))

    return PipelineResult(
        pipeline_outcome="success",
        execution_id=exec_result.execution_id,
        stages=stages
    )
```

#### 5.8.3 Testing in Isolation

```bash
pytest tests/integration/test_orchestrator.py -v
```

Key test cases:
- Happy path intent produces `pipeline_outcome: success`
- Policy-failing intent produces `pipeline_outcome: escalated`
- High-risk intent produces `pipeline_outcome: blocked` and `halted_at: risk`
- `dry_run=true` runs all stages but execution returns `dry_run: true`
- After orchestration, `GET /orchestrate/{intent_id}/status` returns the pipeline summary

---

### 5.9 Module 9: Feedback Analysis

#### 5.9.1 What to Implement

- Execution outcome tracker: records whether executions succeeded or failed post-hoc
- Pattern analyser: identifies recurring risk factors, policy violations, or execution failures
- Feedback API: exposes analysis results and allows operators to accept or reject AI-generated suggestions
- FastAPI endpoints: `GET /feedback/analysis`, `POST /feedback/accept/{id}`, `POST /feedback/reject/{id}`

#### 5.9.2 Minimum Viable Implementation

For the prototype, feedback analysis may be a simple aggregation over audit records:

```python
def analyse() -> FeedbackAnalysis:
    records = audit_reader.get_all()
    blocked = [r for r in records if r.outcome == "blocked"]
    escalated = [r for r in records if r.outcome == "escalated"]
    return FeedbackAnalysis(
        total_intents=len({r.intent_id for r in records}),
        block_rate=len(blocked) / max(len(records), 1),
        escalation_rate=len(escalated) / max(len(records), 1),
        top_block_reasons=_top_reasons(blocked),
        suggestions=[]
    )
```

---

## 6. Testing Strategy

### 6.1 Test Structure

```
tests/
├── unit/
│   ├── test_intent_validator.py
│   ├── test_policy_engine.py
│   ├── test_condition_parser.py
│   ├── test_risk_scorer.py
│   ├── test_decision_engine.py
│   ├── test_governance_gate.py
│   ├── test_audit_service.py
│   └── test_mock_adapters.py
├── integration/
│   ├── test_orchestrator.py
│   ├── test_pipeline_happy_path.py
│   ├── test_pipeline_policy_failure.py
│   ├── test_pipeline_block.py
│   └── test_pipeline_conflict.py
└── fixtures/
    ├── intent_payments_happy.json
    ├── intent_payments_no_encryption.json
    ├── intent_core_routing_degraded.json
    └── intent_api_gateway_conflict.json
```

### 6.2 Unit Test Principles

- All unit tests are deterministic. No `random`, no `datetime.now()` without mocking, no network calls.
- Test both the happy path and all documented error cases.
- Use `pytest.mark.parametrize` for enumeration coverage.
- Each module's tests must run independently without other modules loaded.

### 6.3 Integration Test Principles

- Integration tests start the full FastAPI app using `httpx.AsyncClient` against `app` directly (no real HTTP).
- Fixtures provide canonical request bodies from `tests/fixtures/`.
- Assert exact `pipeline_outcome` values, not just HTTP status codes.
- Assert that audit records are written for every stage that ran.

### 6.4 Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=src/anif --cov-report=term-missing

# A specific test
pytest tests/unit/test_risk_scorer.py::test_prod_score -v
```

---

## 7. Common Implementation Pitfalls

### 7.1 Non-Deterministic Policy Evaluation

**Pitfall:** Using `datetime.now()`, `random()`, or external state in policy condition evaluation.

```python
# WRONG — non-deterministic
def evaluate_condition(condition: Condition, intent: dict) -> bool:
    if condition.operator == "equals":
        return resolve_field(intent, condition.field_path) == condition.value
    elif condition.operator == "time_before":
        return datetime.now() < parse(condition.value)  # non-deterministic!
```

**Fix:** Policy conditions must only evaluate against the intent object and the explicitly provided context object. Time-based or state-based conditions must be resolved to values before being passed as context, not evaluated inside the condition evaluator.

### 7.2 Missing Audit Writes

**Pitfall:** Returning from a stage before writing the audit record.

**Fix:** Use a try/finally pattern to guarantee audit writes:

```python
async def validate(intent: dict, intent_id: str) -> ValidationResult:
    start = time.monotonic_ns()
    try:
        result = _do_validate(intent)
        outcome = "success" if result.valid else "failure"
        return result
    except Exception as exc:
        outcome = "failure"
        raise
    finally:
        duration_ms = (time.monotonic_ns() - start) // 1_000_000
        await audit.write(AuditRecord(
            stage="intent_validation",
            intent_id=intent_id,
            outcome=outcome,
            duration_ms=duration_ms,
            ...
        ))
```

### 7.3 Hardcoded Strings

**Pitfall:** Using string literals for action types, stage names, policy names, or outcome values.

```python
# WRONG — hardcoded strings lead to silent failures
if action["action_type"] == "isolate_segmnet":  # typo will never be caught
    ...
```

**Fix:** Use Python enums for all categorical values and reference enum members, never string literals, in business logic.

### 7.4 Action Executors Without rollback()

**Pitfall:** Implementing `execute()` but leaving `rollback()` as a stub that raises `NotImplementedError`.

**Fix:** Every adapter must implement a functional `rollback()` before it is registered. Even if the rollback is a no-op in a mock, it must complete without error. See section 5.6.4.

### 7.5 Mutable Default Arguments in Pydantic Models

**Pitfall:**

```python
class Intent(BaseModel):
    policies: List[str] = []  # shared mutable default
```

**Fix:**

```python
from pydantic import Field
class Intent(BaseModel):
    policies: List[str] = Field(default_factory=list)
```

---

## 8. Adding a Custom Action Type

To add a new action type (e.g., `update_acl`):

1. Add `update_acl` to the `ActionType` enum in `src/anif/actions/models.py`.
2. Add `update_acl` to `action_schema.yml` under `action_type.enum`.
3. Create `src/anif/actions/adapters/mock_acl_adapter.py` implementing the `ActionAdapter` protocol.
4. Register the adapter in `src/anif/actions/registry.py`.
5. Add unit tests in `tests/unit/test_mock_acl_adapter.py`.
6. Add a fixture and integration test demonstrating the new action type.

Do not add logic for the new action type inside existing adapter classes. Each action type gets its own adapter class.

---

## 9. Adding a Custom Policy

To add a new policy (e.g., `hipaa_compliant`):

1. Create `schemas/policies/hipaa_compliant.yml` following `policy_schema`.
2. Add `hipaa_compliant` to the `PolicyName` enum in `src/anif/policy/models.py`.
3. Add `hipaa_compliant` to `intent_schema.yml` under `policies.items.enum`.
4. Add unit tests for all rules in the new policy.
5. Add an integration test fixture that exercises the new policy.

Custom policies loaded from external files at runtime (without code changes) are supported if the policy engine is configured with a policy directory path. In this case, step 2 and 3 are only required if the policy name needs to appear in intent validation.

---

## 10. Conformance Requirements

10.1 Every module MUST write an audit record before returning, including on error paths.

10.2 All categorical values (action types, stage names, policy names, outcomes) MUST use Python enums. String literals MUST NOT be used in business logic comparisons.

10.3 All adapter implementations MUST implement `rollback()` and MUST be registered only after rollback is verified.

10.4 Policy evaluation MUST be deterministic. No time-dependent, random, or externally mutable state may influence policy decisions.

10.5 All Pydantic models MUST use `Field(default_factory=...)` for mutable defaults.

---

## 11. Security Considerations

11.1 Schema files loaded from disk MUST be validated against a trusted checksum before use. Schema tampering is an attack vector.

11.2 Adapter parameters passed in action objects MUST be validated against per-adapter parameter schemas before being forwarded to any network device API.

11.3 The audit service MUST reject duplicate `record_id` values to prevent record injection attacks.

11.4 The governance approval endpoint MUST require authentication. Unauthenticated approval requests MUST return HTTP 401.

---

## 12. Operational Considerations

12.1 Module health checks should be implemented as `GET /health` endpoints returning the module's readiness to process requests.

12.2 The orchestrator MUST implement a per-intent timeout. An intent that has been in-pipeline for more than the configured timeout (default: 60 seconds) MUST be escalated and a `failure` audit record written.

12.3 In production deployments, the in-memory audit backend must be replaced with a persistent, append-only store. Postgres with row-level security is recommended.

---

## Appendix A: pyproject.toml Structure

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "anif"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.111",
    "uvicorn[standard]>=0.29",
    "pydantic>=2.7",
    "pyyaml>=6.0",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = [
    "pytest>=7",
    "pytest-asyncio>=0.23",
    "pytest-cov>=5",
    "ruff>=0.4",
    "mypy>=1.10",
]
```

---

## Appendix B: Change History

| Version | Date       | Author             | Summary       |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
