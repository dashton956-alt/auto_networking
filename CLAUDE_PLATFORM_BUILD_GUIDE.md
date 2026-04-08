# CLAUDE_PLATFORM_BUILD_GUIDE.md

## What This Guide Is For

This guide is for engineers — human or AI — who are **building software that implements and conforms to ANIF**. It covers how to translate ANIF MUST requirements into test cases and implementation code, the correct build order for modules, and how to avoid the most common conformance failures.

This guide is distinct from `CLAUDE_FRAMEWORK_BUILD_GUIDE.md`, which covers contributing to the ANIF documentation corpus itself.

---

## Required Skills — When to Invoke

| Skill | When |
|---|---|
| `superpowers:test-driven-development` | Before writing any module — write tests from ANIF spec first, always |
| `superpowers:executing-plans` | Working through the implementation plan task by task |
| `superpowers:requesting-code-review` | After completing each module |
| `superpowers:systematic-debugging` | Before proposing any fix — diagnose root cause first |
| `superpowers:verification-before-completion` | Before claiming a module is done |
| `superpowers:finishing-a-development-branch` | Before merging any branch |

---

## Tech Stack

| Technology | Version | Why |
|---|---|---|
| Python | 3.11+ | Type annotations, match statements, async support |
| FastAPI | Current | ANIF-300 series REST API endpoints; OpenAPI schema generation |
| Pydantic v2 | Current | Intent schema validation (ANIF-300), policy schema validation (ANIF-301) |
| pytest | Current | Test framework; required for TDD workflow |
| pytest-asyncio | Current | Async test support for pipeline stage testing |
| Docker | Current | Agent containerisation (ANIF-845) |
| docker-compose | Current | Local integration test environment |
| Redis | 7+ | Intent queue (ANIF-311), message bus |
| PostgreSQL | 15+ | Audit trail (ANIF-107), risk register (ANIF-832) |

---

## Build Order Per Module

1. **Read the ANIF spec document** for the module being built. Identify every MUST and MUST NOT requirement. List them explicitly before writing any code.
2. **Write test cases directly from the MUST requirements** — not from code that does not exist yet. Each MUST requirement should produce at least one test case. Each MUST NOT requirement should produce at least one negative test case.
3. **Run tests to confirm they fail.** Tests MUST fail before implementation begins. A test that passes without implementation is either testing the wrong thing or has a bug.
4. **Implement until tests pass.** Write the minimum implementation that satisfies the tests. Do not add features not covered by tests.
5. **Run `superpowers:requesting-code-review`.** Do not skip this step after completing a module.
6. **Run `superpowers:verification-before-completion`.** Confirm the module satisfies all MUST requirements in the ANIF spec.
7. **Commit.** Commit message format: `feat: implement ANIF-NNN [description]`.

---

## Module Build Order

Build in this order. Each module has dependencies on the preceding modules.

| Order | Module | ANIF Spec Documents | Key Deliverable |
|---|---|---|---|
| 1 | Schema definitions | ANIF-300, ANIF-600 | Pydantic models for Intent, Policy, RiskScore, AuditRecord |
| 2 | Audit trail | ANIF-107, ANIF-724 | AuditWriter — writes tamper-evident records before returning |
| 3 | Policy engine | ANIF-301, ANIF-302 | PolicyEvaluator — deterministic, same inputs → same output |
| 4 | Risk scorer | ANIF-303 | RiskScorer — returns score 0–100 with component breakdown |
| 5 | Intent validator | ANIF-300, ANIF-303 | IntentValidator — schema + constraint validation |
| 6 | Governance gate | ANIF-301 | GovernanceGate — routes to auto_execute / recommend / manual_review / council_review |
| 7 | Pipeline stages | ANIF-304–308 | Each pipeline stage as a separate module with rollback |
| 8 | Agent lifecycle | ANIF-803, ANIF-805 | AgentRegistry — manages lifecycle state and trust level |
| 9 | Authentication | ANIF-843 | CertificateVerifier — per-request X.509 verification |
| 10 | Ethics gate | ANIF-720–725 | EthicsEvaluator — runs before every Tier 3 action |
| 11 | Monitoring | ANIF-846 | SecurityMonitor — produces structured monitoring events |
| 12 | Human-in-loop | ANIF-402, ANIF-404 | ApprovalQueue — presents recommendations; records overrides |

**Dependency rule:** Never build module N before module N-1 is complete and its tests pass. The audit trail module (order 2) is a dependency of every subsequent module — every module must write to audit before returning.

---

## Key Pitfalls

**Gold-plating:** If a MUST requirement does not exist in the ANIF spec, do not implement it. Features without specification coverage are unverifiable. When a feature seems necessary but is not in the spec, write a spec change proposal and wait for approval before building.

**Tests written after code:** Tests written after implementation confirm that the code works as written. They do not confirm that the code satisfies requirements. The discipline is tests first. A developer who writes the code and then writes tests to match it has inverted the process and lost the verification value.

**Skipping audit writes:** ANIF-107 and ANIF-724 require every action to be written to the audit trail before returning. Missing audit writes are the most common conformance failure in ANIF implementations. Every `execute()` function in every module MUST call `audit_writer.write()` as its first substantive action — not its last, not on success only, not in a finally block that might be skipped. If the audit write fails, the action MUST be aborted.

**Hardcoding strings:** All action types, governance modes, lifecycle states, trust levels, and severity values MUST be enums. String comparison of these values is fragile and produces silent failures when values are changed. Define enums in `schemas/` and import them everywhere.

**Non-deterministic policy evaluation:** Policy evaluation (ANIF-301, ANIF-302) MUST be deterministic. The same intent, the same policy set, and the same timestamp MUST always produce the same governance mode output. If policy evaluation is not deterministic, audit trail replay is impossible. Do not use randomness, current time (unless evaluating time-based policy windows explicitly), or external state in the policy evaluator.

**LLM agents without deterministic shadow:** ANIF-807 requires every LLM agent to have a deterministic shadow running in parallel. An LLM agent deployed without its shadow is a conformance violation. The shadow must be implemented before the LLM component is integrated, not after.

**Missing rollback:** ANIF-308 requires every pipeline execution stage to have a rollback plan. Build the rollback implementation before the execution implementation. A stage that can execute but cannot roll back is incomplete.

**Silent failures:** Every error path MUST halt and escalate. No swallowed exceptions. No `except: pass`. No returning `None` from a function that should return a result. When a module encounters an error it cannot handle, it raises the error, writes to audit, and lets the pipeline handle escalation.

**Inference data in audit:** Audit records MUST NOT contain raw LLM inference output. Inference outputs are summarised and the summary is logged, not the full output. Raw inference output is privacy-sensitive and unbounded in size. The audit trail is for governance, not for debugging LLM behaviour.

---

## ANIF Pipeline Implementation Guide

The ANIF intent pipeline has eight stages. Each stage is a module with a defined input, output, and audit obligation.

| Stage | Input | Output | ANIF Source | Audit Obligation |
|---|---|---|---|---|
| 1. Receive | Raw intent (JSON/YAML) | Validated IntentModel | ANIF-300 | Write INTENT_RECEIVED before validation |
| 2. Validate | IntentModel | Validated IntentModel + validation result | ANIF-303 | Write INTENT_VALIDATED or INTENT_REJECTED |
| 3. Risk Score | Validated IntentModel | RiskScore (0–100 with components) | ANIF-303 | Write RISK_SCORED |
| 4. Policy Evaluate | IntentModel + RiskScore | GovernanceMode + policy_result | ANIF-301 | Write POLICY_EVALUATED |
| 5. Ethics Evaluate | IntentModel + GovernanceMode | EthicsResult (pass/flag/block) | ANIF-720–725 | Write ETHICS_EVALUATED |
| 6. Route | GovernanceMode + EthicsResult | Routing decision | ANIF-301 | Write INTENT_ROUTED |
| 7. Execute (or queue) | Validated IntentModel | ExecutionResult | ANIF-304–308 | Write EXECUTION_START, EXECUTION_COMPLETE or EXECUTION_FAILED |
| 8. Close | ExecutionResult | Closed IntentRecord | ANIF-311 | Write INTENT_CLOSED |

**Required API endpoints** (per ANIF-300 series):

| Endpoint | Method | Description |
|---|---|---|
| `/intents` | POST | Submit a new intent |
| `/intents/{id}` | GET | Retrieve intent status and record |
| `/intents/{id}/approve` | POST | Human approval for `recommend` mode |
| `/intents/{id}/reject` | POST | Human rejection |
| `/intents/{id}/override` | POST | Human override with mandatory `override_reason` |
| `/agents` | GET | List registered agents with trust level and lifecycle state |
| `/agents/{id}/suspend` | POST | Suspend an agent (transitions to SUSPENDED state) |
| `/audit` | GET | Query audit records (paginated, with filter parameters) |

---

## Testing Standards for ANIF Conformance

Map ANIF test cases directly to pytest test modules.

| ANIF Test Category | ANIF Source | pytest Location | What to Test |
|---|---|---|---|
| TC-001: Intent schema validation | ANIF-300 | `tests/test_intent_schema.py` | Valid intents accepted; invalid intents rejected with correct error |
| TC-002: Policy evaluation | ANIF-301 | `tests/test_policy_engine.py` | Deterministic output; correct governance mode per policy configuration |
| TC-003: Ethics constraint enforcement | ANIF-720–725 | `tests/test_ethics_gate.py` | P-01 through P-06 constraints enforce correctly; strikes applied on violation |
| TC-004: Audit trail completeness | ANIF-107 | `tests/test_audit_trail.py` | Every action produces audit record; records are tamper-evident |
| TC-005: Human override | ANIF-402 | `tests/test_human_override.py` | Override takes effect within 5 seconds; override_reason is mandatory |

Additional test categories required for ANIF-820 deployment gates:

- Prompt injection tests (PI-01 to PI-05) — tested via `tests/security/test_injection.py`
- Adversarial input tests (AI-01 to AI-05) — tested via `tests/security/test_adversarial.py`
- Conflict detection tests (AC-01 to AC-05) — tested via `tests/test_conflict_detection.py`

---

## Exploratory Spikes

Spikes are permitted for genuine unknowns — integration points that cannot be designed without empirical investigation. Rules:

- Maximum spike duration: 2 hours
- Spike output: a written note describing what was learned and what the implementation approach should be
- Spike code: discarded after the note is written; never promoted to production
- If the spike reveals that the ANIF spec is incomplete or ambiguous: write a spec change proposal and pause implementation until the spec is clarified

Spikes are not an excuse to skip TDD. "I spiked it and it worked" is not a substitute for tests.
