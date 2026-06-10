# ANIF Platform — Living Architecture Document

> This document is maintained by the `architecture-agent`. Do not edit manually
> without also updating the relevant `.drawio` diagram files.

**Last updated by:** architecture-agent (post-F1 catch-up)
**Platform version:** 0.1.0 — backend phases B1–B8 complete; frontend F1 complete

---

## System Overview

The ANIF platform is a Python/FastAPI application that implements the Autonomous
Networking & Infrastructure Framework specification. It accepts network intents,
evaluates them against policies, scores their risk, makes bounded decisions,
routes them through governance (auto / manual review / block), executes approved
actions against a network adapter, and records every stage to an immutable
SHA-256 hash-chained audit trail.

A React/TypeScript UI (`src/anif_ui`) consumes the REST API. Its design system
(F1) is WCAG 2.1 AA audited via Playwright + axe-core.

---

## Pipeline

`POST /orchestrate` chains all six stages; each stage writes an audit record
before returning:

```
validate → policy → risk → decision → governance → execute
```

| Stage | Module | Failure exit |
|---|---|---|
| Validate | `intent` (IntentValidator, VAL-001–007) | `failed` |
| Policy | `policy` (PolicyEngine, deterministic) | `failed` |
| Risk | `risk` (RiskScorer) | `blocked` |
| Decision | `risk` (DecisionEngine: auto / manual_review / block) | — |
| Governance | `governance` (GovernanceGate) + `human_loop` (ApprovalQueue ticket) | `blocked` / `pending_approval` |
| Execute | `execution` (ActionExecutor + MockNetworkAdapter) | `precondition_failed` |

Dry-run mode (`dry_run: true`) stops short of execution and suppresses
policy-stage audit writes.

---

## Backend Modules

| Module | Status | Phase | ANIF Spec | Key classes |
|---|---|---|---|---|
| `schemas` | Implemented | B1 | ANIF-300, ANIF-600 | Intent, Policy, RiskScore, AuditRecord, Action |
| `audit` | Implemented | B1 | ANIF-107, ANIF-724 | AuditWriter (SHA-256 hash chain), AuditQueryService |
| `intent` | Implemented | B2 | ANIF-300, ANIF-301 | IntentValidator, IntentRegistry, GitWatcher |
| `policy` | Implemented | B2 | ANIF-302, ANIF-303 | PolicyEngine, PolicyLoader, ConditionEvaluator, ConflictResolver |
| `risk` | Implemented | B3 | ANIF-304, ANIF-305 | RiskScorer, DecisionEngine |
| `governance` | Implemented | B4 | ANIF-301, ANIF-406 | GovernanceGate (mode routing, RBAC) |
| `human_loop` | Implemented | B4 | ANIF-402, ANIF-404 | ApprovalQueue, ticket expiry loop, emergency halt |
| `execution` | Implemented | B5 | ANIF-306 | ActionExecutor, NetworkAdapter protocol, MockNetworkAdapter, rollback |
| `agents` | Implemented | B6 | ANIF-803, ANIF-805, ANIF-843 | AgentRegistry, AgentCertificate (X.509), TierBoundaryChecker |
| `auth` | API-key placeholder | B1 | ANIF-843 | `get_api_key` (X-API-Key header); X.509 gateway wiring pending |
| `ethics` | Implemented | B7 | ANIF-720–725 | ActionTypeValidator, Containment, FairnessChecker, LLMValidator, override router |
| `council` | Implemented | B8 | ANIF-902–907 | Build-time / runtime / review councils, CouncilModeSelector |
| `learning` | Implemented | B8 | ANIF-812, ANIF-905 | LearningBroker, learning package approval flow |
| `monitoring` | Implemented | B4+ | ANIF-401, ANIF-846 | Prometheus governance counters/histograms |
| `pipeline` | Implemented | B2–B5 | ANIF-305, ANIF-306, ANIF-308 | `/orchestrate` orchestrator |
| `sot` | Protocol + stubs | — | ANIF-307 | SoT protocol; Nautobot/NetBox/InfraHub adapters raise NotImplementedError |

**Cross-cutting rules in force:**

- AuditWriter is injected into every stage; records are written before any
  handler returns (ANIF-107 §4.3).
- All routers require the `X-API-Key` header (`ANIF_API_KEY` env var).
- Dependency injection throughout; `main.py` is the only composition root.

---

## REST API Surface

| Method | Path | Module |
|---|---|---|
| POST | `/orchestrate` | pipeline |
| POST | `/intent/validate-intent` | intent |
| GET | `/intent/intent/{intent_id}` | intent |
| POST | `/evaluate-policy` | policy |
| GET | `/audit` (filterable) | audit |
| GET | `/audit/{intent_id}` | audit |
| GET | `/audit/{intent_id}/why` | audit |
| GET | `/audit/{intent_id}/verify` | audit |
| POST | `/governance/check` | governance |
| GET | `/governance/tickets` | governance |
| POST | `/governance/approve/{ticket_id}` | governance |
| POST | `/governance/reject/{ticket_id}` | governance |
| POST | `/execute` | execution |
| POST | `/rollback/{intent_id}` | execution |
| POST | `/execution/{intent_id}/halt` | human_loop |
| POST | `/override` | ethics |
| POST | `/council/build-time` · `/runtime` · `/review` (+ decision/timeout) | council |
| POST | `/learning/packages` (+ approve/reject) | learning |
| POST | `/webhooks/git` | intent (GitWatcher) |

---

## Frontend

Stack: React 19, TypeScript, Vite, Tailwind CSS 3, React Router 7,
Playwright + axe-core for WCAG 2.1 AA audits.

### Design System (F1 — complete)

- Tailwind tokens: brand, status, intent, risk, chrome palettes; Inter font.
- Components: Button, Badge, Spinner, Card, Alert, Skeleton, Input, Select,
  Table, RiskMeter, CountdownTimer — all with ARIA attributes.
- AppShell layout: collapsible Sidebar + TopBar + skip-to-content link.
- Living showcase at `/design-system`; axe audit passes with 0 violations.

### Pages

| Page | Status | Phase | Backend Dependency |
|---|---|---|---|
| Design System showcase | Implemented | F1 | None |
| Intent Dashboard | Not started | F2 | B2 (Intent API) ✓ ready |
| Approval Queue | Not started | F3 | B4 ✓ ready |
| Audit Trail Viewer | Not started | F4 | B2 ✓ ready |
| Topology View | Not started | F5 | B5 ✓ ready (SoT adapters still stubbed) |
| Risk & Governance | Not started | F6 | B8 ✓ ready |

---

## Data Stores

| Table | Module | Purpose |
|---|---|---|
| `audit_records` | audit | Hash-chained immutable audit trail |
| `intents` | intent | Registered validated intents (+ Git provenance) |
| `approval_tickets` | human_loop | Manual-review tickets with expiry |
| `executed_actions` | execution | Action execution + rollback state |
| `agents`, `agent_certificates` | agents | Agent lifecycle + X.509 certs |
| `ethics_*` | ethics | Strikes, containment, override audit |
| `council_*` | council | Council sessions and decisions |
| `learning_packages` | learning | Learning packages pending approval |

Migrations: Alembic, `migrations/versions/` — every migration has a working
`downgrade()`.

---

## Diagrams

All diagrams are in `docs/architecture/diagrams/`. Open with draw.io or diagrams.net.

| File | Contents |
|---|---|
| `system-context.drawio` | Platform boundaries and external systems |
| `component.drawio` | Module breakdown and interfaces |
| `sequence-pipeline.drawio` | Intent → policy → risk → decision → governance → execution |
| `agent-tiers.drawio` | 4-tier agent model with capabilities |
| `data-flow.drawio` | Intent lifecycle and audit trail flow |
| `sot-integration.drawio` | SoT read/write-back boundaries |
| `deployment.drawio` | Docker services, ports, networking |

---

## External Systems

| System | Role | Connection |
|---|---|---|
| Nautobot / NetBox / InfraHub | Source of Truth | REST / GraphQL (read + metadata write-back) — adapters stubbed |
| PostgreSQL 15 | Audit trail, intents, tickets, agents | SQLAlchemy 2 async (asyncpg) |
| Redis 7 | Intent queue, message bus | redis-py async |
| Prometheus | Metrics collection | prometheus_client counters |
| Containerlab | Network simulation | CLI + topology YAML |
| Batfish | Static config analysis | pybatfish |

---

## Test Baseline

439 tests passing (unit + integration), 82% line coverage.
Integration tests require the Docker Postgres (`anif` / `anif_test` databases).
