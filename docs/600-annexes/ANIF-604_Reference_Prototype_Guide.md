# ANIF-604: Reference Prototype Guide

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-604                                           |
| Series       | Annex                                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-200, ANIF-602, ANIF-300, ANIF-503             |

---

## Abstract

This document is the complete guide to the ANIF reference prototype — a working, API-driven implementation of the full autonomous networking decision pipeline. It covers what the prototype demonstrates, how to run it, all available API endpoints with example requests and responses, how to extend it, and the mapping between prototype code and ANIF specification documents.

---

## 1. Introduction

### 1.1 Purpose

The ANIF reference prototype is the executable version of the ANIF specification. It demonstrates that the full decision pipeline — from intent submission through governance-gated action execution to immutable audit logging — works in practice as specified. This guide enables developers and evaluators to run, test, and extend the prototype.

### 1.2 Scope

This guide covers:

- What the prototype is and is not
- Prerequisites and quick start
- All API endpoints with example curl requests and responses
- Test suite execution
- Extending the prototype (new adapters, new policies)
- Mapping from code modules to ANIF specification documents

### 1.3 What the prototype is NOT

The prototype is explicitly **not**:

- Production-ready software for managing real network devices
- Capable of connecting to physical or virtual network infrastructure (mock adapters only)
- Persistent across restarts (in-memory storage)
- Multi-tenant or horizontally scalable
- Protected by production-grade authentication (static API key only)

These are post-prototype concerns. The prototype proves the logic; scale comes later.

### 1.4 Intended audience

Developers implementing ANIF, evaluators assessing prototype conformance, and architects extending the reference implementation.

---

## 2. Normative references

- ANIF-200 — Reference Architecture
- ANIF-602 — Implementation Guide
- ANIF-503 — Test Case Catalogue

---

## 3. Terms and definitions

| Term | Definition |
|---|---|
| Prototype | The reference implementation of the ANIF pipeline; API-driven, in-memory, mock adapters only |
| Mock adapter | A simulated network adapter that returns realistic responses without touching real infrastructure |
| Dry run | Pipeline execution with `dry_run=true`; all evaluation stages run but execution and governance approval are skipped |
| Intent hash | A deterministic hash of an intent object used by mock adapters to produce consistent outcomes for testing |

---

## 4. Quick Start

### 4.1 Prerequisites

- Docker 24.0+
- Docker Compose v2.0+
- Git
- curl or any HTTP client (for testing)

### 4.2 Running the prototype

```bash
# Clone the repository
git clone https://github.com/[org]/anif-prototype.git
cd anif-prototype

# Start the full stack
docker compose up

# The API is available at:
# http://localhost:8000
# Interactive docs (Swagger UI): http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### 4.3 Run the test suite

```bash
# Run all tests
docker compose run --rm api pytest

# Run with coverage report
docker compose run --rm api pytest --cov=anif --cov-report=term-missing

# Run only unit tests
docker compose run --rm api pytest tests/unit/

# Run only integration tests
docker compose run --rm api pytest tests/integration/
```

### 4.4 First intent in 60 seconds

```bash
# Submit a valid intent and run the full pipeline
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key" \
  -d '{
    "service": "payments",
    "environment": "prod",
    "objectives": {
      "latency_ms": 50,
      "availability_percent": 99.99
    },
    "constraints": {
      "region": "EU",
      "encryption": true,
      "allowed_zones": ["zone-a", "zone-b"]
    },
    "policies": ["zero_trust", "pci_compliant"],
    "priority": "critical"
  }'
```

---

## 5. API Reference

All endpoints return a consistent response envelope:

```json
{
  "status": "ok | error",
  "data": {},
  "errors": [],
  "trace_id": "uuid"
}
```

### 5.1 Intent Validation

#### POST /validate-intent

Validates an intent against the schema and custom rules. Assigns an `intent_id` on success.

**Request:**
```bash
curl -X POST http://localhost:8000/validate-intent \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key" \
  -d '{
    "service": "payments",
    "environment": "prod",
    "objectives": {"latency_ms": 50, "availability_percent": 99.99},
    "constraints": {"region": "EU", "encryption": true, "allowed_zones": ["zone-a", "zone-b"]},
    "policies": ["zero_trust", "pci_compliant"],
    "priority": "critical"
  }'
```

**Response (valid):** HTTP 200
```json
{
  "status": "ok",
  "data": {
    "valid": true,
    "intent_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "errors": [],
    "warnings": []
  },
  "errors": [],
  "trace_id": "a1b2c3d4-..."
}
```

**Response (invalid — pci_compliant + encryption:false):** HTTP 422
```json
{
  "status": "error",
  "data": {
    "valid": false,
    "intent_id": null,
    "errors": [
      {
        "field": "constraints.encryption",
        "message": "pci_compliant policy requires encryption: true"
      }
    ],
    "warnings": []
  },
  "errors": ["Validation failed"],
  "trace_id": "a1b2c3d4-..."
}
```

#### GET /intent/{intent_id}

Returns a stored intent and its current processing status.

```bash
curl http://localhost:8000/intent/f47ac10b-58cc-4372-a567-0e02b2c3d479 \
  -H "X-API-Key: dev-key"
```

---

### 5.2 Policy Evaluation

#### POST /evaluate-policy

Evaluates a validated intent against a policy set.

**Request:**
```bash
curl -X POST http://localhost:8000/evaluate-policy \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key" \
  -d '{
    "intent_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "intent": { ... },
    "policy_set": [
      {
        "name": "pci_compliant",
        "precedence": "compliance",
        "rules": [
          {"condition": "constraints.encryption:equals:false", "action": "deny"}
        ]
      }
    ],
    "dry_run": false
  }'
```

**Response:** HTTP 200
```json
{
  "status": "ok",
  "data": {
    "overall_result": "pass",
    "policy_results": [
      {
        "policy": "pci_compliant",
        "result": "pass",
        "violated_rule": null,
        "rationale": "All rules passed"
      }
    ],
    "conflicts": [],
    "resolved_policy_set": ["pci_compliant", "zero_trust"]
  },
  "errors": [],
  "trace_id": "..."
}
```

---

### 5.3 Risk Scoring

#### POST /score-risk

Computes risk and trust scores for a validated, policy-evaluated intent.

**Request:**
```bash
curl -X POST http://localhost:8000/score-risk \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key" \
  -d '{
    "intent_id": "f47ac10b-...",
    "intent": { ... },
    "policy_result": { "overall_result": "pass", "policy_results": [...] },
    "network_state": { "status": "healthy" }
  }'
```

**Response:** HTTP 200
```json
{
  "status": "ok",
  "data": {
    "risk_score": 35,
    "trust_score": 90,
    "safety_decision": "allow",
    "justification": [
      {"factor": "environment=prod", "contribution": 30, "source": "intent.environment"},
      {"factor": "priority=critical", "contribution": -10, "source": "intent.priority"},
      {"factor": "no policy failures", "contribution": 0, "source": "policy_result"},
      {"factor": "network_state=healthy", "contribution": 0, "source": "network_state"},
      {"factor": "action_type=reroute_traffic", "contribution": 15, "source": "decision"}
    ],
    "threshold_applied": "prod"
  },
  "errors": [],
  "trace_id": "..."
}
```

---

### 5.4 Decision Engine

#### POST /decide

Returns a bounded action recommendation.

**Response:** HTTP 200
```json
{
  "status": "ok",
  "data": {
    "recommended_action": "reroute_traffic",
    "confidence_score": 87,
    "risk_level": "medium",
    "mode": "auto",
    "reasoning_chain": [
      {"step": 1, "description": "Check safety_decision", "decision": "allow — proceed", "rationale": "risk_score=35, below warn threshold of 40"},
      {"step": 2, "description": "Evaluate availability objective", "decision": "high availability required", "rationale": "availability_percent=99.99 >= 99.99"},
      {"step": 3, "description": "Select action type", "decision": "reroute_traffic", "rationale": "high availability + latency_ms=50 satisfies reroute_traffic preference rule"}
    ],
    "rollback_plan": "Restore original routing table entries. Estimated rollback time: 30 seconds."
  },
  "errors": [],
  "trace_id": "..."
}
```

---

### 5.5 Governance Gate

#### POST /governance/check

Runs the mode gate check.

**Request body:** `{ "intent_id": "...", "decision_result": {...}, "operator_context": {"user_id": "eng-1", "roles": ["network_engineer"], "environment": "prod"} }`

**Response:** `{ "mode": "auto", "reason": "all governance rules passed", "approval_ticket": null, "guardrail_applied": null }`

#### POST /governance/approve/{ticket_id}

Approves a pending governance ticket. Requires `approver_role: senior_engineer`.

#### POST /governance/reject/{ticket_id}

Rejects a pending ticket with a required `reason` field.

---

### 5.6 Action Execution

#### POST /execute

Executes an approved action.

**Response:** HTTP 200
```json
{
  "status": "ok",
  "data": {
    "execution_id": "exec-uuid",
    "action_type": "reroute_traffic",
    "status": "success",
    "adapter_response": {"message": "Traffic rerouted via zone-b", "affected_routes": 3},
    "duration_ms": 127,
    "rollback_available": true
  },
  "errors": [],
  "trace_id": "..."
}
```

#### POST /rollback/{intent_id}

Independently triggers rollback for a previously executed action.

#### GET /execution/{execution_id}

Returns full execution history including any rollback events.

---

### 5.7 Audit Log

#### GET /audit/{intent_id}

Returns all audit records for an intent in chronological order. Response time MUST be < 100ms.

#### GET /audit/{intent_id}/why

Returns a human-readable explanation of every decision made for the intent.

**Response example:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "f47ac10b-...",
    "explanation": "Intent for service 'payments' in environment 'prod' was submitted at 2026-04-07T10:00:00Z.\n\nVALIDATION (pass): Intent passed all schema and custom validation rules. intent_id assigned.\n\nPOLICY (pass): All 2 policies evaluated. zero_trust: pass. pci_compliant: pass. No conflicts detected.\n\nRISK SCORING (allow): risk_score=35, trust_score=90. Environment=prod added 30 points. No policy failures. Network state healthy. Score below warn threshold of 40 — safety_decision: allow.\n\nDECISION (auto): reroute_traffic selected. High availability (99.99%) and latency objective (50ms) satisfied reroute preference. Rollback plan documented.\n\nGOVERNANCE (auto): All mode gate rules passed. Operator 'eng-1' has network_engineer role. trust_score=90 >= 60. Auto execution approved.\n\nEXECUTION (success): reroute_traffic executed in 127ms. 3 routes affected. Rollback available."
  },
  "errors": [],
  "trace_id": "..."
}
```

#### GET /audit

Filterable audit query. Query parameters: `stage`, `outcome`, `date_from`, `date_to`, `operator_id`.

```bash
curl "http://localhost:8000/audit?stage=governance&outcome=escalated&date_from=2026-04-07" \
  -H "X-API-Key: dev-key"
```

---

### 5.8 Full Pipeline Orchestration

#### POST /orchestrate

Runs the full pipeline in a single call. Add `?dry_run=true` to skip execution.

```bash
# Full pipeline
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key" \
  -d '{ ... intent ... }'

# Dry run (no execution)
curl -X POST "http://localhost:8000/orchestrate?dry_run=true" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key" \
  -d '{ ... intent ... }'
```

**Response includes** `pipeline_summary` + full `stages` output + `audit_url`.

If the pipeline halts early, response includes `halted_at: "risk"` (or whichever stage blocked).

#### GET /orchestrate/{intent_id}/status

Returns the current pipeline state for an in-progress or completed orchestration.

---

### 5.9 Feedback Analysis

#### GET /feedback/analysis

Analyses the last N executions (default N=50) and returns tuning suggestions.

```bash
curl "http://localhost:8000/feedback/analysis?n=100" \
  -H "X-API-Key: dev-key"
```

**Response includes:** `false_positive_rate`, `block_rate`, `frequent_policy_failures`, `suggested_tuning` (read-only — never auto-applied).

#### POST /feedback/accept/{suggestion_id}

Records human acceptance of a tuning suggestion (audit logged).

#### POST /feedback/reject/{suggestion_id}

Records rejection with a required `reason` (audit logged).

---

## 6. Mock Adapter Behaviour

Mock adapters simulate real network device responses without contacting actual infrastructure. Success/failure outcomes are **deterministic based on intent hash** — the same intent always produces the same simulated outcome, ensuring tests are reproducible.

| Action Type | Base Success Rate | Determinism Mechanism | Requires Pre-approved Ticket |
|---|---|---|---|
| reroute_traffic | 90% | intent_hash % 10 >= 1 | No |
| apply_qos | 95% | intent_hash % 20 >= 1 | No |
| scale_bandwidth | 85% | intent_hash % 20 >= 3 | No |
| isolate_segment | 80% | intent_hash % 10 >= 2 | Yes — always |

Simulated latency: configurable, default 50–200ms (seeded random based on intent_hash for reproducibility).

On simulated failure: rollback is automatically attempted and the result is recorded in the audit log.

---

## 7. Code to Spec Mapping

| Module | Location | Implements |
|---|---|---|
| Intent validation | `src/anif/intent/` | ANIF-301, ANIF-300 |
| Policy engine | `src/anif/policy/` | ANIF-302, ANIF-303 |
| Risk scoring | `src/anif/risk/` | ANIF-304 |
| Decision engine | `src/anif/decision/` | ANIF-305 |
| Action executors | `src/anif/actions/` | ANIF-306 |
| Mock adapters | `src/anif/actions/adapters/` | ANIF-306 (adapter layer) |
| Governance gate | `src/anif/governance/` | ANIF-404, ANIF-406 |
| Audit service | `src/anif/audit/` | ANIF-107 |
| Orchestrator | `src/anif/api/orchestrate.py` | ANIF-200 (pipeline flow) |
| API routers | `src/anif/api/` | ANIF-204 (FastAPI) |
| Schemas (YAML) | `schemas/` | ANIF-600 |
| Pydantic models | `src/anif/*/models.py` | ANIF-202 |

---

## 8. Extending the Prototype

### 8.1 Adding a new action adapter

1. Create `src/anif/actions/adapters/my_adapter.py`
2. Implement the adapter interface: `execute(action, parameters) -> ExecutionResult` and `rollback(intent_id) -> RollbackResult`
3. Register the adapter in `src/anif/actions/registry.py`
4. Add adapter unit tests in `tests/unit/test_my_adapter.py`

The adapter MUST NOT access any module outside `src/anif/actions/`. It MUST declare its capabilities (which action types it supports) in its manifest.

### 8.2 Adding a new policy

1. Add the policy name to the `policies` enum in `schemas/intent_schema.yml`
2. Create the policy definition using the condition syntax: `field_path:operator:value`
3. Assign a `precedence` category: `compliance | security | availability | performance`
4. Add unit tests in `tests/unit/test_policy_engine.py` with deterministic fixtures
5. Verify no conflicts with existing policies using the conflict detection tests

### 8.3 Adding a custom risk factor

1. Add the factor to the risk factor registry in `src/anif/risk/factors.py`
2. Define the contribution formula (integer points)
3. Add to the justification output
4. Write unit tests asserting exact numeric outputs for the new factor

---

## 9. Known Limitations

| Limitation | Impact | Future Work |
|---|---|---|
| In-memory storage only | All data lost on restart | Persistent store (PostgreSQL, Redis) |
| Static API key auth | No per-user identity | OAuth2 / mTLS |
| Single process | No horizontal scaling | Async task queue (Celery, Kafka) |
| Mock adapters only | No real network effects | Vendor adapter plugins |
| No UI or dashboard | API-only interaction | Web dashboard |
| No distributed audit | Single node audit log | Distributed append-only store |

---

## 5. Conformance Requirements

The reference prototype MUST pass all test cases defined in ANIF-503 at L3 conformance level. The prototype SHOULD be used as the baseline for assessing conformance claims.

---

## 6. Security Considerations

The prototype uses a static API key (`X-API-Key` header) for all requests. This is sufficient for local development and evaluation. The prototype MUST NOT be deployed in any production environment or connected to real network infrastructure without replacing the authentication mechanism with production-grade auth (OAuth2, mTLS).

The prototype does not implement TLS termination — run behind a TLS-terminating reverse proxy if exposed beyond localhost.

---

## 7. Operational Considerations

The prototype is designed to run locally via `docker compose up` with no external dependencies. All state is in-memory and resets on container restart. For persistent evaluation across restarts, implement the persistent store extension described in ANIF-602.

---

## Appendix A: Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ANIF_API_KEY` | `dev-key` | Static API key for authentication |
| `ANIF_LOG_LEVEL` | `INFO` | Structured log level (DEBUG/INFO/WARNING/ERROR) |
| `ANIF_LOG_FORMAT` | `json` | Log format (json or text) |
| `ANIF_MOCK_LATENCY_MIN_MS` | `50` | Minimum mock adapter latency |
| `ANIF_MOCK_LATENCY_MAX_MS` | `200` | Maximum mock adapter latency |
| `ANIF_RISK_PROD_WARN` | `40` | Production warn threshold |
| `ANIF_RISK_PROD_BLOCK` | `70` | Production block threshold |
| `ANIF_RISK_NONPROD_WARN` | `60` | Non-production warn threshold |
| `ANIF_RISK_NONPROD_BLOCK` | `85` | Non-production block threshold |
| `ANIF_TICKET_EXPIRY_MINUTES` | `15` | Governance approval ticket expiry |

---

## Appendix B: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
