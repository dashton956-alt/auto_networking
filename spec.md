# ANIF Prototype — Feature Specification
## 001-anif-core-pipeline

**Spec version:** 0.1.0  
**Status:** Draft  
**Feature branch:** `001-anif-core-pipeline`  

---

## Overview

Build the ANIF reference prototype — a working, API-driven implementation of the full autonomous networking decision pipeline. The system accepts a network intent, validates it, evaluates it against policies, scores its risk, makes a bounded decision, optionally executes an action, and records everything to an immutable audit log.

Every stage is independently callable via its own API endpoint. The full pipeline is also callable as a single orchestrated flow via `/orchestrate`.

---

## Background & Context

### What Is an Intent?

An intent is a declarative statement of what a network or infrastructure service should achieve — not how. For example:

```yaml
service: payments
environment: prod
objectives:
  latency_ms: 50
  availability_percent: 99.99
constraints:
  region: EU
  encryption: true
  allowed_zones: [zone-a, zone-b]
policies:
  - zero_trust
  - pci_compliant
priority: critical
```

The system's job is to take this intent and determine whether and how to act on it — safely, transparently, and with a full audit trail.

### Existing Schemas (already defined in repo)

The following schemas exist and must be used as the basis for all data models:

- `schemas/intent_schema.yml` — service, environment, objectives, constraints, policies, priority
- `schemas/action_schema.yml` — action_type (reroute_traffic, apply_qos, scale_bandwidth, isolate_segment), parameters, risk_level
- `schemas/policy_schema.yml` — name, rules (condition, action: allow/deny/warn)

New schemas to be created as part of this feature:
- `schemas/risk_score_schema.yml` — risk_score, trust_score, safety_decision, justification
- `schemas/audit_record_schema.yml` — record_id, intent_id, timestamp, stage, input, output, outcome

---

## User Stories

---

### US-01: Intent Submission & Validation

**As a** network engineer or automation system,  
**I want to** submit a network intent via API and receive immediate validation feedback,  
**So that** I know whether my intent is structurally valid and schema-compliant before any policy evaluation occurs.

#### Acceptance criteria

- `POST /validate-intent` accepts a JSON body matching `intent_schema.yml`
- Response includes: `valid: true/false`, list of `errors` (field path + message for each), `intent_id` (UUID assigned on receipt), `warnings` (non-blocking issues)
- If the intent is invalid, no further processing occurs and no audit record is created for downstream stages
- If the intent is valid, an audit record is written for the validation stage
- Invalid intents return HTTP 422 with structured errors — not 500
- Custom validation rules enforced beyond schema:
  - `prod` environment requires `priority: critical` or `high`
  - `pci_compliant` policy requires `encryption: true`
  - `availability_percent` of 99.99 or above requires at least 2 `allowed_zones`
  - `latency_ms` below 10 triggers a warning (flagged but not blocked)
- `GET /intent/{intent_id}` returns the stored intent and its current processing status

#### Example valid intent (from repo)
```json
{
  "service": "payments",
  "environment": "prod",
  "objectives": { "latency_ms": 50, "availability_percent": 99.99 },
  "constraints": { "region": "EU", "encryption": true, "allowed_zones": ["zone-a", "zone-b"] },
  "policies": ["zero_trust", "pci_compliant"],
  "priority": "critical"
}
```

#### Example invalid intent (custom rule violation)
```json
{
  "service": "payments",
  "environment": "prod",
  "objectives": { "latency_ms": 50, "availability_percent": 99.99 },
  "constraints": { "region": "EU", "encryption": false },
  "policies": ["pci_compliant"],
  "priority": "critical"
}
```
Expected: HTTP 422, error on `constraints.encryption` — "pci_compliant policy requires encryption: true"

---

### US-02: Policy Evaluation

**As a** governance system,  
**I want to** evaluate a validated intent against a set of policy rules,  
**So that** I know which policies pass, which fail, and which conflict — before any action is taken.

#### Acceptance criteria

- `POST /evaluate-policy` accepts `{ intent_id, intent, policy_set }` where `policy_set` is a list of policies matching `policy_schema.yml`
- Response includes: `overall_result: pass|fail|warn`, list of `policy_results` (policy name, result, violated rule, rationale for each), `conflicts` list (policies that contradict each other), `resolved_policy_set` (the winning set after conflict resolution)
- Policy evaluation is fully deterministic — same inputs always produce same outputs
- Conflict resolution uses explicit precedence order: `compliance > security > availability > performance`
- If two policies of equal precedence conflict, both are flagged and escalation is triggered (result: `manual_review`)
- A `dry_run: true` parameter prevents audit record creation
- Audit record written on non-dry-run evaluation
- Built-in policies to implement (minimum set):
  - `zero_trust`: deny unless explicit allow on all constraints
  - `no_public_ingress`: deny if no `allowed_zones` specified
  - `pci_compliant`: deny if `encryption: false`
  - `data_residency`: deny if `region` not in approved list for the service

#### Policy conflict example
Policy A (compliance): deny if encryption=false  
Policy B (performance): allow if latency_ms < 20 regardless of encryption  
→ Conflict detected. Compliance wins. Result: deny. Rationale recorded.

---

### US-03: Risk & Trust Scoring

**As a** decision engine,  
**I want to** receive a risk score and trust score for a validated, policy-evaluated intent,  
**So that** I can determine the appropriate execution mode (auto / manual review / block) before any action is taken.

#### Acceptance criteria

- `POST /score-risk` accepts `{ intent_id, intent, policy_result, network_state }` where `network_state` is a mock object representing current topology health
- Response includes:
  - `risk_score`: integer 0–100 (0 = no risk, 100 = maximum risk)
  - `trust_score`: integer 0–100 (0 = no trust, 100 = full trust)
  - `safety_decision`: `allow | warn | block`
  - `justification`: list of factors with their individual contribution and source
  - `threshold_applied`: which threshold set was used (prod vs non-prod)
- Scoring is deterministic — same inputs, same scores, always
- Risk factors to implement (minimum set):
  - Environment weight: `prod` adds 30 points base risk
  - Priority weight: `critical` reduces trust score by 10 (higher stakes)
  - Policy failures: each failed policy adds 15 points risk
  - Policy warnings: each warning adds 5 points risk
  - Network state: `degraded` state adds 20 points risk, `healthy` adds 0
  - Action type risk: `isolate_segment` = high (+25), `reroute_traffic` = medium (+15), `apply_qos` = low (+5), `scale_bandwidth` = low (+5)
- Threshold sets:
  - Prod: block if risk_score ≥ 70, warn if ≥ 40, allow if < 40
  - Non-prod: block if risk_score ≥ 85, warn if ≥ 60, allow if < 60
- Audit record written on every score call

---

### US-04: Decision Engine

**As an** orchestration system,  
**I want to** receive a bounded action recommendation given a validated intent, policy result, and risk score,  
**So that** the system selects the safest appropriate action from a predefined set — with no free-form generation.

#### Acceptance criteria

- `POST /decide` accepts `{ intent_id, intent, policy_result, risk_score_result }`
- Response includes:
  - `recommended_action`: one of the four action types from `action_schema.yml` or `null` if blocked
  - `confidence_score`: integer 0–100
  - `risk_level`: `low | medium | high` (from action schema)
  - `mode`: `auto | manual_review | block`
  - `reasoning_chain`: ordered list of decision steps with rationale at each step
  - `rollback_plan`: description of how this action would be reversed
- Decision logic is a deterministic, bounded decision tree — no AI/ML model in this path
- The engine may ONLY select from the four predefined action types: `reroute_traffic`, `apply_qos`, `scale_bandwidth`, `isolate_segment`
- Decision tree logic (minimum):
  - If `safety_decision = block` → mode: block, recommended_action: null
  - If `safety_decision = warn` → mode: manual_review
  - If `availability_percent ≥ 99.99` and `latency_ms ≤ 50` → prefer `reroute_traffic`
  - If `latency_ms` objective is primary concern → prefer `apply_qos`
  - If network state is degraded → prefer `reroute_traffic` over `scale_bandwidth`
  - If `isolate_segment` is selected → always escalate to `manual_review` regardless of risk score
- `rollback_plan` is required for every non-null `recommended_action`
- Audit record written for every decision

---

### US-05: Governance Gate

**As a** human operator,  
**I want** every candidate action to pass through a governance mode gate before execution,  
**So that** I can be confident that high-risk or policy-flagged actions require explicit human approval.

#### Acceptance criteria

- `POST /governance/check` accepts `{ intent_id, decision_result, operator_context }` where `operator_context` includes `user_id`, `roles: []`, `environment`
- Response includes: `mode: auto|manual_review|block`, `reason`, `approval_ticket` (if manual_review), `guardrail_applied` (which rule triggered the mode)
- Mode gate rules (all must be implemented):
  - If `recommended_action = isolate_segment` → always `manual_review`
  - If `risk_score ≥ 70` → always `manual_review`
  - If `environment = prod` and `mode = auto` → only allow if `trust_score ≥ 60`
  - If operator role does not include `network_engineer` or `automation_agent` → `block`
  - If `safety_decision = block` → `block` regardless of roles
- Approval ticket schema: `{ ticket_id, intent_id, decision_summary, risk_score, requested_by, created_at, expires_at, status: pending|approved|rejected }`
- `POST /governance/approve/{ticket_id}` marks a ticket approved (requires `approver_role: senior_engineer` or above)
- `POST /governance/reject/{ticket_id}` marks a ticket rejected with a required `reason`
- Approved tickets expire after 15 minutes — expired approvals require re-submission
- All governance decisions written to audit log

---

### US-06: Action Execution (Mock Adapters)

**As an** automation system,  
**I want to** execute an approved action against a mock network adapter,  
**So that** the full pipeline is exercised end-to-end without requiring real network devices.

#### Acceptance criteria

- `POST /execute` accepts `{ intent_id, decision_result, governance_result }` — only processes if `governance_result.mode = auto` or an approved ticket exists
- Mock adapters implement the four action types and return a realistic success/failure response with latency simulation (configurable, default 50–200ms random within a seed)
- Each adapter implements `execute()` and `rollback()` — rollback must be callable independently via `POST /rollback/{intent_id}`
- Execution response includes: `execution_id`, `action_type`, `status: success|failed|partial`, `adapter_response`, `duration_ms`, `rollback_available: true/false`
- On failure, rollback is attempted automatically and the outcome recorded
- `GET /execution/{execution_id}` returns full execution history including any rollback events
- All execution events — start, success, failure, rollback — written to audit log
- Mock adapter behaviour:
  - `reroute_traffic`: succeeds 90% of the time (deterministic based on intent hash for testing)
  - `apply_qos`: succeeds 95% of the time
  - `scale_bandwidth`: succeeds 85% of the time
  - `isolate_segment`: succeeds 80% of the time, always requires pre-approved ticket

---

### US-07: Audit Log

**As a** compliance officer or senior engineer,  
**I want to** query a complete, immutable audit log of every decision and action taken by the system,  
**So that** I can trace the full reasoning chain for any intent from submission to outcome.

#### Acceptance criteria

- Every stage (validate, policy, risk, decision, governance, execute, rollback) writes an audit record
- Audit records are append-only — no update or delete endpoints exist
- Audit record schema (minimum fields):
  ```json
  {
    "record_id": "uuid",
    "intent_id": "uuid",
    "timestamp": "ISO-8601",
    "stage": "validate|policy|risk|decision|governance|execute|rollback",
    "operator_id": "string or null",
    "input_summary": {},
    "output_summary": {},
    "outcome": "success|failure|escalated|blocked",
    "reasoning_chain": [],
    "duration_ms": 0
  }
  ```
- `GET /audit/{intent_id}` returns all audit records for a given intent in chronological order
- `GET /audit/{intent_id}/why` returns a human-readable explanation of every decision made for that intent, stitched together from the reasoning chains
- `GET /audit` supports filtering by: `stage`, `outcome`, `date_from`, `date_to`, `operator_id`
- Audit store is an in-memory append-only list for the prototype (persistence is post-prototype)
- Response time for `/audit/{intent_id}` must be < 100ms

---

### US-08: Full Pipeline Orchestration

**As a** developer or integration system,  
**I want to** submit a single intent and have the entire pipeline run automatically,  
**So that** I can exercise the full system without calling each endpoint individually.

#### Acceptance criteria

- `POST /orchestrate` accepts an intent JSON and runs the full pipeline: validate → policy → risk → decision → governance → execute (if auto-approved)
- `dry_run: true` parameter runs the full pipeline but skips execution and governance approval
- Response includes the output of every stage plus a `pipeline_summary`:
  ```json
  {
    "intent_id": "uuid",
    "pipeline_summary": {
      "validation": "pass|fail",
      "policy": "pass|fail|warn",
      "risk_score": 0,
      "safety_decision": "allow|warn|block",
      "mode": "auto|manual_review|block",
      "action_taken": "action_type or null",
      "execution_status": "success|failed|pending_approval|skipped",
      "audit_url": "/audit/{intent_id}"
    },
    "stages": { ... full stage outputs ... }
  }
  ```
- Pipeline halts at the first blocking stage and returns the partial result with `halted_at` field
- Each stage result references the audit record ID written for that stage
- `GET /orchestrate/{intent_id}/status` returns the current pipeline state for a given intent

---

### US-09: Closed-Loop Feedback

**As a** policy administrator,  
**I want to** see outcome-based suggestions for policy and risk threshold tuning,  
**So that** the system improves from its execution history without requiring manual log analysis.

#### Acceptance criteria

- `GET /feedback/analysis` analyses the last N executions (default N=50) and returns:
  - `false_positive_rate`: percentage of manual_review escalations that were subsequently approved without change
  - `block_rate`: percentage of intents blocked at each stage
  - `frequent_policy_failures`: top 3 policy rules by failure frequency
  - `suggested_tuning`: list of suggestions, each with `type: threshold|policy_condition`, `current_value`, `suggested_value`, `rationale`, `confidence: low|medium|high`
- Suggestions are read-only — they are never auto-applied in the prototype
- `POST /feedback/accept/{suggestion_id}` records human acceptance of a suggestion (audit logged)
- `POST /feedback/reject/{suggestion_id}` records rejection with required reason (audit logged)
- Analysis is computed from the audit log — no separate data store needed

---

## Non-Functional Requirements

| Requirement | Target |
|---|---|
| Response time — `/validate-intent` | < 50ms |
| Response time — `/evaluate-policy` | < 100ms |
| Response time — `/score-risk` | < 50ms |
| Response time — `/decide` | < 50ms |
| Response time — `/orchestrate` (dry run) | < 500ms |
| Response time — `/audit/{intent_id}` | < 100ms |
| All policy evaluation | 100% deterministic |
| Test coverage — core modules | ≥ 80% |
| All action executors | rollback() implemented |
| All audit writes | before response returned |

---

## Out of Scope for This Feature

- Real network device integration (mock adapters only)
- UI or dashboard
- Authentication beyond a static API key header
- Persistent storage (in-memory only)
- Multi-tenancy or multi-user isolation
- ML-based risk scoring (deterministic rule engine only)
- Distributed execution or async task queue

---

## Review & Acceptance Checklist

- [ ] All 9 user stories have passing integration tests
- [ ] `/orchestrate` runs the full pipeline end-to-end without errors
- [ ] `/orchestrate?dry_run=true` runs without triggering any execution
- [ ] Policy evaluation is verified deterministic (same input = same output across 100 calls)
- [ ] Risk scoring produces exact values matching the formula in US-03
- [ ] `isolate_segment` action always triggers `manual_review` mode
- [ ] Rollback is callable for all four action types
- [ ] Audit log contains a record for every stage of a completed orchestration
- [ ] `/audit/{intent_id}/why` returns human-readable reasoning
- [ ] All Pydantic models mirror their YAML schema counterparts
- [ ] No hardcoded strings — all action types, policy names, and status codes use enums
- [ ] All functions have type hints and docstrings
- [ ] Test coverage ≥ 80% on intent, policy, risk, decision modules
- [ ] `docker-compose up` starts the full system with no manual steps
- [ ] README documents all endpoints with example requests and responses
