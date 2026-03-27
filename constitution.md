# ANIF Prototype — Constitution
## Project Governing Principles & Development Guidelines

**Project:** Autonomous Networking & Infrastructure Framework (ANIF) — Reference Prototype  
**Version:** 0.1.0  
**Status:** Active  

---

## What We Are Building

The ANIF prototype is the reference implementation of an intent-driven autonomous networking and infrastructure management system. It demonstrates the full decision pipeline:

```
Intent IN → Validate → Policy Check → Risk Score → Decision → Action OUT → Audit LOG
```

This is an enterprise-grade system. Every component must be production-shaped from day one — not production-scale, but production-shaped. That means correct abstractions, proper separation of concerns, audit trails, rollback paths, and deterministic behaviour throughout.

The prototype exists to prove the ANIF framework specification works in practice. It is the executable version of the documentation.

---

## Non-Negotiable Principles

Every implementation decision — architecture, API design, data model, test strategy — must honour all of the following. These are not guidelines. They are constraints.

### P-01 — Reversibility
Every autonomous action must have a defined rollback path before execution is permitted. No action executor may be implemented without a corresponding `rollback()` handler. If a rollback path cannot be defined, the action must not be implemented.

### P-02 — Auditability
No action may be taken without a complete, immutable, timestamped audit record. Audit writes happen before action execution returns. Audit records are append-only and must never be mutated or deleted by application code.

### P-03 — Determinism
Policy evaluation and risk scoring must produce identical outputs for identical inputs. No randomness, no external non-deterministic calls in the evaluation path. Tests must be able to assert exact output values, not ranges or approximations.

### P-04 — Explainability
Every automated decision must be explainable in human-readable form on demand. Every decision object must carry a `reasoning_chain` — not just a result code. The `/why` API must always be implementable for any decision the system makes.

### P-05 — Least Privilege
Autonomous agents operate with the minimum permissions required for each intent. Action executors are scoped to declared capabilities only. An executor that can reroute traffic must not also be able to isolate segments unless explicitly declared.

### P-06 — Human Override
A human operator must always be able to halt, override, or reverse any automated action. The governance engine is not optional. Every execution path passes through a mode gate: `auto | manual_review | block`.

### P-07 — Fail Safe
On uncertainty, missing data, schema violation, or system error — the default posture is halt and escalate. Never proceed on ambiguity. Return a structured error with context, not a silent failure or a best-effort guess.

### P-08 — Vendor Neutrality
The core system must not depend on any specific vendor's networking API, cloud provider SDK, or proprietary schema. Vendor integration lives exclusively in the adapter/plugin layer. Core engines operate on abstract models only.

### P-09 — Incremental Adoption
The system must be runnable in stages. A team must be able to run intent validation without the risk engine, and the risk engine without action execution. Each component exposes its own API and can be called independently.

### P-10 — Test-First
No module ships without tests. Policy evaluation, risk scoring, and decision logic are unit-tested with deterministic fixtures. Integration tests cover the full pipeline end to end. Tests are not written after — they are written as part of the implementation task.

---

## Architecture Constraints

### Language & Stack
- **Backend:** Python 3.11+ with FastAPI
- **Schema validation:** Pydantic v2 for all data models
- **Schema definitions:** YAML (intent, action, policy, risk, audit schemas)
- **Testing:** pytest with deterministic fixtures
- **Containerisation:** Docker + docker-compose for local orchestration
- **No framework magic:** explicit is better than implicit; no auto-wiring that hides data flow

### Code Quality Standards
- All public functions and classes must have docstrings
- Type hints on all function signatures — no untyped parameters
- No bare `except:` blocks — all exceptions are caught specifically and logged with context
- No `print()` in application code — use structured logging (`structlog` or `logging` with JSON formatter)
- No hardcoded strings for policy names, action types, or status codes — use enums
- Maximum function length: 40 lines. If longer, decompose.
- Maximum file length: 300 lines. If longer, split the module.

### API Design Standards
- All endpoints return a consistent envelope: `{ "status": "ok|error", "data": {}, "errors": [], "trace_id": "" }`
- All action-triggering endpoints require a `dry_run` boolean parameter
- All responses include the `intent_id` they relate to
- HTTP status codes are used correctly — 200 for success, 422 for validation failure, 409 for policy conflict, 500 for system error
- Every endpoint that can produce an audit record must do so before returning

### Schema Standards
- Schemas live in `/schemas/` as YAML files
- Pydantic models are generated from or directly mirror the YAML schemas
- All enums are declared in schemas — no magic string values in application code
- Schema changes that break existing valid intents require a version bump

### Testing Standards
- Unit tests: one file per module, `tests/unit/test_{module}.py`
- Integration tests: `tests/integration/test_{pipeline_segment}.py`
- All policy evaluation tests use fixture intents from `tests/fixtures/`
- Risk scoring tests assert exact numeric outputs, not ranges
- Every test that touches the audit log asserts the log entry exists and is correct
- Minimum coverage target: 80% on core modules (intent, policy, risk, decision)

---

## What We Are Not Building

To keep scope clear — the prototype explicitly does not include:

- A UI or dashboard (API-only)
- Real vendor network device integration (mock adapters only)
- Production-grade auth/identity (API key header is sufficient for prototype)
- A distributed message queue (synchronous pipeline only)
- Multi-tenancy
- Horizontal scaling or high-availability infrastructure

These are post-prototype concerns. The prototype proves the logic; scale comes later.

---

## Decision-Making Guidelines

When faced with a design choice, ask in order:

1. Does this violate any of P-01 through P-10? If yes, don't do it.
2. Does this make the system harder to test deterministically? If yes, find another way.
3. Does this hide the data flow or create implicit behaviour? If yes, make it explicit.
4. Does this add a dependency that couples us to a vendor or framework? If yes, abstract it.
5. Is this the simplest thing that correctly implements the spec? If not, simplify.

---

## Folder Structure

```
anif-prototype/
├── src/
│   └── anif/
│       ├── intent/          # Validation, schema, Pydantic models
│       ├── policy/          # Engine, conflict resolution, precedence
│       ├── risk/            # Risk scoring, trust quantification
│       ├── decision/        # Bounded action selection
│       ├── actions/         # Executors + rollback handlers + mock adapters
│       ├── governance/      # Mode gate, RBAC checks, approval workflow
│       ├── audit/           # Immutable audit log writer and reader
│       └── api/             # FastAPI routers and request/response models
├── schemas/                 # YAML schema definitions
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/            # Deterministic test intents and policies
├── docker-compose.yml
├── Makefile
└── README.md
```
