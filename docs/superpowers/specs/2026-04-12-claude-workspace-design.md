# Claude Workspace Design — auto_networking Platform

**Date:** 2026-04-12
**Status:** Approved
**Repo:** auto_networking
**Companion spec repo:** Autonomous-Networking-Infrastructure-Framework-ANIF

---

## Overview

Set up the `auto_networking` repository as a fully instrumented Claude Code workspace for building the ANIF reference platform implementation. The workspace provides Claude with everything needed to build the platform autonomously: directory structure, CLAUDE.md instructions, MCP server connectivity, a 10-agent quality mesh (including architecture agent), automated hooks, 10 installed plugins, complete CI/CD pipeline, network simulation tooling, source-of-truth integration adapters, database migration management, observability stack, and frontend UI scaffolding — all wired to the Spec-Driven Development + Ralph Loop methodology.

Backend and frontend are treated as independent tracks with their own phase sequences.

---

## 1. Repository Directory Structure

```
auto_networking/
├── CLAUDE.md                            ← platform build instructions, agent definitions, SDD workflow
├── .claude/
│   └── settings.json                    ← MCP servers, hooks, plugin list
├── .github/
│   └── workflows/
│       ├── ci.yml                       ← lint, type-check, unit + integration tests, security scan, Docker build
│       ├── accessibility.yml            ← Playwright WCAG 2.1 AA audit (UI changes only)
│       ├── intent-validate.yml          ← intent schema + IBN policy check (schema/intent changes only)
│       └── compliance.yml              ← ISO 27001, HIPAA, GDPR dependency + config audit
├── src/
│   ├── anif_platform/
│   │   ├── __init__.py
│   │   ├── schemas/                     ← Pydantic models — Intent, Policy, RiskScore, AuditRecord
│   │   ├── audit/                       ← AuditWriter — tamper-evident records
│   │   ├── policy/                      ← PolicyEvaluator — deterministic evaluation
│   │   ├── risk/                        ← RiskScorer — 0–100 with component breakdown
│   │   ├── intent/                      ← IntentValidator — schema + constraint validation
│   │   ├── governance/                  ← GovernanceGate — routes auto/recommend/manual/council
│   │   ├── pipeline/                    ← Pipeline stages with rollback
│   │   ├── agents/                      ← AgentRegistry — lifecycle + trust level
│   │   ├── auth/                        ← CertificateVerifier — X.509 per-request
│   │   ├── ethics/                      ← EthicsEvaluator — runs before every Tier 3 action
│   │   ├── monitoring/                  ← SecurityMonitor — structured monitoring events
│   │   ├── human_loop/                  ← ApprovalQueue — recommendations + override records
│   │   └── sot/                         ← Source-of-Truth adapter — Nautobot / NetBox / InfraHub
│   └── anif_ui/                         ← React + TypeScript management dashboard
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       └── types/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── network/                         ← containerlab topology tests
│   └── conftest.py
├── schemas/                             ← ANIF YAML schemas (intent, action, policy, risk, audit)
├── migrations/                          ← Alembic database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── simulation/
│   ├── topologies/                      ← containerlab topology YAML files
│   └── batfish/                         ← Batfish network config snapshots
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml              ← includes postgres, redis, prometheus, grafana
├── docs/
│   ├── architecture/
│   │   ├── ARCHITECTURE.md              ← living architecture document (kept in sync by architecture-agent)
│   │   └── diagrams/                    ← draw.io XML files
│   │       ├── system-context.drawio
│   │       ├── component.drawio
│   │       ├── sequence-pipeline.drawio
│   │       ├── agent-tiers.drawio
│   │       ├── data-flow.drawio
│   │       ├── sot-integration.drawio
│   │       └── deployment.drawio
│   └── superpowers/
│       └── specs/                       ← design documents (this file lives here)
├── pyproject.toml
└── .env.example
```

Module build order matches `CLAUDE_PLATFORM_BUILD_GUIDE.md` in the ANIF repo exactly. Each directory corresponds to one module. No module is created before its dependency is complete.

---

## 2. Tech Stack

### Backend

| Technology | Version | Role |
|---|---|---|
| Python | 3.11+ | Primary language |
| FastAPI | current | REST API endpoints |
| Pydantic v2 | current | Schema validation |
| SQLAlchemy 2 | current | ORM for audit + risk models |
| Alembic | current | Database migrations |
| pytest + pytest-asyncio | current | TDD test framework |
| Docker + docker-compose | current | Containerisation + local integration env |
| Redis 7+ | current | Intent queue, message bus |
| PostgreSQL 15+ | current | Audit trail, risk register |
| ruff | current | Linting + auto-fix |
| black | current | Formatting |
| mypy | current | Static type checking |

### Frontend

| Technology | Version | Role |
|---|---|---|
| React | 18+ | UI framework |
| TypeScript | 5+ | Type safety |
| Vite | current | Build tool |
| Tailwind CSS | current | Styling |
| Playwright | current | E2E + accessibility testing |
| axe-core | current | WCAG 2.1 AA automated audit |

### Network Simulation

| Tool | Role |
|---|---|
| Containerlab | Primary — container-based topology simulation (already installed) |
| Batfish | Static network config analysis — validates configs without live devices |
| GNS3 (optional) | Alternative for appliance-based simulation via REST API |

### Observability

| Tool | Role |
|---|---|
| Prometheus | Metrics collection from platform |
| Grafana | Dashboards — intent pipeline throughput, risk scores, audit volume |

---

## 3. MCP Servers

Configured in `.claude/settings.json` under `mcpServers`. All credentials reference environment variables — no secrets in config files.

| Name | Package | Purpose |
|---|---|---|
| `filesystem` | `@modelcontextprotocol/server-filesystem` | Read/write repo files with scoped access |
| `git` | `@modelcontextprotocol/server-git` | Log, diff, blame, branch operations |
| `postgres` | `@modelcontextprotocol/server-postgres` | Query audit DB + risk register live |
| `docker` | `mcp-server-docker` | Inspect containers, logs, service health |
| `playwright` | `@playwright/mcp` | Browser automation — UI testing, WCAG accessibility audits |
| `figma` | `figma-mcp` | Read Figma designs directly into context |
| `prometheus` | `mcp-server-prometheus` | Query live metrics from running platform |
| `sot` | custom (see Section 9) | Unified source-of-truth adapter — Nautobot / NetBox / InfraHub |

---

## 4. Hooks

Configured in `.claude/settings.json` under `hooks`. Fire automatically — no manual invocation needed.

| Event | Matcher | Command |
|---|---|---|
| `PostToolUse` | `Edit\|Write\|MultiEdit` (`.py`) | `ruff check --fix <changed files>` |
| `PostToolUse` | `Edit\|Write\|MultiEdit` (`.py`) | `black <changed files>` |
| `PostToolUse` | `Edit\|Write\|MultiEdit` (`.py`) | `mypy <changed files>` |
| `PostToolUse` | `Edit\|Write\|MultiEdit` (`.yml`/`.json`) | ibn-agent intent schema lint |
| `PostToolUse` | `Edit\|Write\|MultiEdit` (SQLAlchemy models) | migration-agent detects model changes |
| `Stop` | session end | write current task context to `.claude/resume.md` |

Hooks run against changed files only, not the entire codebase. Output capped to 100 lines to prevent context flood.

---

## 5. Agent Mesh

All 9 agents are defined in `CLAUDE.md`. Invoked via the `Agent` tool during development. Each agent has a defined trigger, scope, and prompt template.

### 5.1 lint-agent
- **Trigger:** After any `.py` file edit
- **Scope:** Changed files only
- **Action:** Runs `ruff check --fix` and `black`; reports remaining violations that could not be auto-fixed

### 5.2 type-agent
- **Trigger:** After a module is marked complete
- **Scope:** Module directory
- **Action:** Deep `mypy` analysis; flags missing annotations, `Any` usage, untyped function signatures

### 5.3 security-agent
- **Trigger:** Before any commit
- **Scope:** Staged changes
- **Action:** Checks against ANIF-840–849 security requirements and OWASP Top 10; flags command injection, unvalidated input, hardcoded secrets, insecure defaults

### 5.4 test-gen-agent
- **Trigger:** When starting a new module (before implementation)
- **Scope:** Target ANIF spec document for the module
- **Action:** Reads every MUST and MUST NOT requirement from the relevant ANIF-NNN document; generates a pytest stub file with one test per requirement; confirms tests fail before implementation begins (SDD gate)

### 5.5 spec-review-agent
- **Trigger:** After a module is complete
- **Scope:** Module source + ANIF spec document
- **Action:** Maps each MUST/MUST NOT requirement to a test and to implementation code; flags any requirement with no corresponding test or implementation; blocks completion claim if coverage is incomplete

### 5.6 best-practices-agent
- **Trigger:** After any implementation
- **Scope:** Changed files
- **Action:** Enforces Python and FastAPI best practices — SOLID principles, single responsibility, no god classes, proper exception handling (no bare `except`), structured logging, dependency injection, no circular imports, consistent naming conventions, no magic numbers

### 5.7 ibn-agent
- **Trigger:** After any `.yml` or `.json` intent file is created or edited; after any intent-processing code changes
- **Scope:** Intent files + ANIF-300/301 spec + `schemas/intent_schema.yml`
- **Dual role:**
  1. **Schema linting** — validates intent files against `schemas/intent_schema.yml`; checks all required fields (service, environment, objectives, constraints, policies, priority); validates field types, enum values, and constraint ranges
  2. **IBN best practice enforcement** — declarative over imperative (no implementation detail leakage into intents), idempotency, proper abstraction layer separation, correct use of objectives vs constraints vs policies, ANIF-300/301 compliance for network intents (routing, QoS, segmentation, zero-trust) and infrastructure intents (compute, storage, connectivity, scaling)

### 5.8 compliance-agent
- **Trigger:** Before any commit touching UI, API contracts, data models, or auth
- **Scope:** Staged changes + running app (via Playwright for UI checks)
- **Checks:**
  - **WCAG 2.1 AA** — contrast ratios, ARIA labels, keyboard navigation, focus management
  - **ADA / Section 508** — disability access requirements
  - **ISO 27001** — infosec control mapping; flags missing audit logs, access controls, encryption at rest
  - **HIPAA** — data handling, audit trail completeness, minimum necessary access
  - **GDPR** — data residency constraints, consent handling, right to erasure considerations
  - **NIST CSF** — cross-references ANIF-102 mapping

### 5.9 architecture-agent
- **Trigger:** After any module is marked complete; after any schema change; after any significant architectural decision
- **Scope:** Entire repo + ANIF spec documents + `docs/architecture/`
- **Dual role:**
  1. **Documentation sync** — reads implemented code and updates the relevant ANIF spec cross-references, module README files, and the living architecture document (`docs/architecture/ARCHITECTURE.md`) to reflect what was actually built; flags any divergence between spec intent and implementation
  2. **Draw.io diagram generation** — generates or updates `.drawio` XML diagram files in `docs/architecture/diagrams/` covering:
     - System context diagram (platform boundaries, external systems)
     - Component diagram (modules, dependencies, interfaces)
     - Sequence diagrams (per pipeline stage: intent → policy → risk → decision → governance → execution)
     - Agent tier diagram (4-tier model with capabilities and boundaries)
     - Data flow diagram (intent lifecycle, audit trail flow)
     - SoT integration diagram (read/write-back boundaries)
     - Deployment diagram (Docker services, ports, networking)

Diagrams are generated as valid draw.io XML (`.drawio` files) that open directly in draw.io / diagrams.net. The agent updates existing diagrams incrementally rather than regenerating from scratch.

### 5.10 migration-agent
- **Trigger:** When SQLAlchemy models change (detected by hook)
- **Scope:** `src/anif_platform/schemas/` + `migrations/`
- **Action:** Compares current models against latest migration; generates Alembic migration script; validates migration is reversible (downgrade path exists); flags destructive operations (column drops, type changes) for human review before proceeding

---

## 6. Plugins

Eleven plugins installed at workspace level:

| Plugin | Purpose |
|---|---|
| `superpowers` | Already installed — brainstorming, TDD, planning, debugging, review skills |
| `feature-dev` | Feature development workflow with exploration + architecture agents |
| `security-guidance` | Hook-based security warnings on file edits |
| `commit-commands` | `/commit`, `/push`, `/pr` slash commands |
| `code-review` | Multi-agent PR review with confidence scoring |
| `code-simplifier` | Simplify and refine code for clarity |
| `pr-review-toolkit` | Specialised PR review agents (comments, tests, error handling, types) |
| `hookify` | Create hooks from conversation patterns |
| `skill-creator` | Build and test custom skills for the project |
| `ralph-loop` | `/ralph-loop` command — continuous self-referential iteration loops |
| `frontend-design` | Frontend design skill for UI/UX implementation |
| `agent-sdk-dev` | Agent SDK development — used when building the AI agent tier (B6–B8) |

---

## 7. Development Methodology

### Spec-Driven Development (SDD) + Ralph Loop

Every module follows this exact sequence:

```
1. READ      — read ANIF-NNN spec for the module; list every MUST and MUST NOT explicitly
2. GENERATE  — invoke test-gen-agent → generates failing pytest stubs from MUSTs
3. VERIFY    — run tests; confirm all fail (tests that pass before implementation are invalid)
4. LOOP      — /ralph-loop "implement <module> until all tests pass" --completion-promise "COMPLETE" --max-iterations 30
5. REVIEW    — invoke spec-review-agent → every MUST covered by test + implementation
6. QUALITY   — invoke best-practices-agent → SOLID, naming, DI, no god classes
7. IBN       — invoke ibn-agent (if module touches intent processing)
8. MIGRATE   — invoke migration-agent (if models changed)
9. SECURE    — invoke security-agent → ANIF-840–849 + OWASP
10. COMPLY   — invoke compliance-agent (if UI, API contract, auth, or data model touched)
11. COMMIT   — commit message format: `feat: implement ANIF-NNN <description>`
```

Steps 4–10 may loop. A module is not complete until steps 5, 6, 9, and 10 all pass.

### Rate Limit Recovery

When the Claude Pro usage limit is reached mid-session:

1. Stop hook fires automatically → writes current task + ralph-loop prompt to `.claude/resume.md`
2. Run `/schedule "resume task from .claude/resume.md" in 5.5h` before closing
3. On scheduled restart, Claude reads `.claude/resume.md` and continues the loop

### Ralph Loop Prompt Template

```
Implement the <module_name> module for the ANIF platform.

Requirements source: <ANIF-NNN document path>
Test file: <tests/unit/test_<module>.py>
Implementation target: <src/anif_platform/<module>/>

Rules:
- Every MUST requirement in ANIF-NNN must be satisfied
- Audit trail write must happen before any function returns
- No implementation without a passing test
- Run tests after every change: pytest tests/unit/test_<module>.py -v
- If tests fail, read the failure, diagnose root cause, fix, re-run
- Do not add features not covered by tests

Output <promise>COMPLETE</promise> when all tests pass and spec-review-agent approves.
```

---

## 8. CI/CD Pipeline

### `ci.yml` — runs on every push and PR

```
jobs:
  lint:        ruff check src/ tests/
  type-check:  mypy src/
  unit-tests:  pytest tests/unit/ -v --cov=src
  integration-tests:
    services: postgres:15, redis:7
    run: pytest tests/integration/ -v
  security-scan:
    run: bandit -r src/ && pip-audit
  docker-build: docker build -t anif-platform .
```

### `accessibility.yml` — runs on UI file changes only (`src/anif_ui/**`)

```
jobs:
  wcag-audit:
    run: playwright + axe-core against built UI
    fail-on: WCAG 2.1 AA violations
```

### `intent-validate.yml` — runs on schema or intent file changes (`schemas/**`, `simulation/topologies/**`)

```
jobs:
  schema-lint:   validate all intent YAML files against intent_schema.yml
  ibn-policy:    check IBN best practices (declarative, no leakage, idempotent)
  batfish-check: static analysis of any network config snapshots
```

### `compliance.yml` — runs on PRs touching auth, data models, API contracts

```
jobs:
  dependency-audit: safety check + pip-audit for CVEs
  iso27001-check:   verify audit trail fields present on all data models
  hipaa-check:      verify PHI handling rules (encryption, access log, minimum necessary)
  gdpr-check:       verify data residency env vars present + deletion endpoints exist
```

All workflows use GitHub Actions caching for pip dependencies. Integration tests use `services:` blocks — no external infrastructure required in CI.

---

## 9. Source-of-Truth (SoT) Adapter

The platform must integrate with Nautobot, NetBox, or InfraHub interchangeably. A single adapter module (`src/anif_platform/sot/`) abstracts all three behind a common interface.

The `nautobot-intent-network-app` is a separate project and is NOT integrated here. Nautobot, NetBox, and InfraHub are used purely as read sources for device and topology data. The ANIF platform owns all intent authoring, validation, policy evaluation, risk scoring, and execution independently.

### Interface

```python
class SoTAdapter(Protocol):
    def get_device(self, name: str) -> Device: ...
    def get_topology(self, site: str) -> Topology: ...
    def list_devices(self, site: str | None = None) -> list[Device]: ...
    def get_prefix(self, prefix: str) -> Prefix: ...
```

### Implementations

| Adapter | Backend | API |
|---|---|---|
| `NautobotAdapter` | Nautobot 3.x | REST + GraphQL — device inventory, IP prefixes, topology |
| `NetBoxAdapter` | NetBox 3.x+ | REST API — device inventory, IP prefixes, topology |
| `InfraHubAdapter` | InfraHub | GraphQL — device inventory, topology |

Selected at runtime via `SOT_BACKEND` environment variable (`nautobot` / `netbox` / `infrahub`).

### Custom MCP (`sot` server)

Wraps the adapter and exposes it to Claude as an MCP tool:

**Read operations:**
- `sot_get_device(name)` — fetch device record from active SoT
- `sot_get_topology(site)` — fetch site topology
- `sot_list_devices(site?)` — list all devices, optionally filtered by site
- `sot_get_prefix(prefix)` — fetch IP prefix record

**Write-back operations (metadata only):**
- `sot_tag_device(name, tag)` — add intent tag to a device (e.g. `intent:qos-prod-v2`)
- `sot_tag_interface(device, interface, tag)` — add intent tag to an interface
- `sot_tag_connection(device_a, device_b, tag)` — add intent tag to a connection/link
- `sot_comment_device(name, comment)` — add comment recording intent applied + outcome
- `sot_comment_interface(device, interface, comment)` — add comment on interface
- `sot_set_custom_field(object_type, name, field, value)` — set a custom field (e.g. `intent_status`, `last_intent_id`, `intent_applied_at`)

Write-back is **metadata only** — tags, comments, and custom fields that record which intent was applied, when, and with what outcome. The platform does not modify device configurations, IP assignments, or topology records in the SoT. All execution state is owned in PostgreSQL; the SoT write-back is a synchronisation of intent application status for operator visibility.

The MCP is a lightweight Python FastAPI server started via `docker-compose`.

---

## 10. Network Simulation

### Containerlab (primary)

- Topology YAML files live in `simulation/topologies/`
- Each topology maps to a test scenario (e.g., `bgp-intent-test.yml`, `qos-intent-test.yml`)
- Integration tests in `tests/network/` spin up topologies, submit intents, verify outcomes
- Supports CEOS, vJunos, FRR, and Linux containers

### Batfish (complementary)

- Network config snapshots in `simulation/batfish/`
- Used for static analysis — validates that generated configs are correct before pushing to live devices or containerlab
- Does not require running containers; fast feedback on config correctness
- Integrated into `intent-validate.yml` CI workflow

### GNS3 (optional)

- REST API available if appliance-level simulation is needed
- Not included in default setup; documented in `docs/simulation.md` as opt-in

---

## 11. Database Migrations (Alembic)

- `migrations/` directory at repo root
- `alembic.ini` references `DATABASE_URL` from environment
- migration-agent generates migration scripts when models change
- Every migration MUST have a `downgrade()` function — enforced by migration-agent
- Destructive operations (column drops, type changes) require explicit human approval comment in migration file before CI passes

---

## 12. Observability Stack (local dev)

Included in `docker/docker-compose.yml`:

| Service | Port | Purpose |
|---|---|---|
| Prometheus | 9090 | Scrapes metrics from platform |
| Grafana | 3000 | Dashboards — pipeline throughput, risk scores, audit volume |

Platform exposes `/metrics` endpoint (Prometheus format) via FastAPI middleware.

Prometheus MCP lets Claude query live metrics directly during development:
- `prometheus_query("anif_intent_processed_total")` — check intent throughput
- `prometheus_query("anif_risk_score_histogram")` — inspect risk score distribution

---

## 13. Frontend (React + TypeScript)

Management dashboard for network operators. Built in `src/anif_ui/`.

Key pages:
- **Intent Dashboard** — submit, view, and track intents through the pipeline
- **Approval Queue** — human-in-loop review and override interface (ANIF-404)
- **Audit Trail** — queryable audit log viewer
- **Topology View** — network topology map with intent status overlays
- **Risk Register** — live risk score dashboard

All pages must pass WCAG 2.1 AA (enforced by compliance-agent + accessibility CI workflow).

`frontend-design` skill invoked for all UI work. Playwright MCP used for live accessibility audits during development.

---

## 14. CLAUDE.md Structure

The `CLAUDE.md` in `auto_networking` contains:

1. **What this repo is** — platform implementation conforming to ANIF; link to ANIF repo; note that `nautobot-intent-network-app` is a separate project — Nautobot/NetBox/InfraHub serve as SoT (device inventory, topology, prefixes) plus receive metadata write-back (tags, comments, custom fields on devices/interfaces/connections) to record intent application status; the platform owns all intent execution independently
2. **ANIF spec reference** — path to companion repo; spec doc → module mapping table
3. **Tech stack** — exact versions and why
4. **Module build order** — numbered list; no module N before N-1 complete
5. **SDD + Ralph Loop workflow** — the 11-step sequence from Section 7
6. **Rate limit recovery** — Stop hook + `/schedule` instructions
7. **Agent definitions** — all 9 agents with triggers, scope, and prompt templates
8. **MCP server usage** — when to use each MCP
9. **SoT adapter** — how to select backend, how to test against each
10. **Network simulation** — when to use containerlab vs Batfish
11. **What not to do** — no gold-plating, no features without spec coverage, no tests after code, no bare excepts, no migration without downgrade, no destructive migration without human approval
12. **Schema standards** — intent YAML validation rules, ibn-agent triggers
13. **Platform build order** — backend phases B1–B8 and frontend phases F1–F6 with dependency rules
14. **Architecture agent** — when to invoke, which diagrams to update, living doc location

---

## 15. Environment Variables (.env.example)

```
# Database
POSTGRES_URL=postgresql://user:password@localhost:5432/anif
DATABASE_URL=postgresql://user:password@localhost:5432/anif

# Cache / Queue
REDIS_URL=redis://localhost:6379

# Source of Truth
SOT_BACKEND=nautobot                          # nautobot | netbox | infrahub
NAUTOBOT_URL=http://localhost:8080
NAUTOBOT_TOKEN=your-token-here
NETBOX_URL=http://localhost:8000
NETBOX_TOKEN=your-token-here
INFRAHUB_URL=http://localhost:8000
INFRAHUB_TOKEN=your-token-here

# Observability
PROMETHEUS_URL=http://localhost:9090

# Figma (UI design)
FIGMA_TOKEN=your-token-here

# ANIF companion repo
ANIF_SPEC_REPO_PATH=/path/to/Autonomous-Networking-Infrastructure-Framework-ANIF

# Platform
LOG_LEVEL=INFO
ENVIRONMENT=development
```

---

## 16. Platform Build Order

Backend and frontend are independent tracks. Frontend phases unlock when the corresponding backend API is ready. The architecture agent runs after every phase on both tracks.

### Backend Track

| Phase | Name | Key Components | Depends On |
|---|---|---|---|
| B1 | Foundation & Data Models | Pydantic schemas (Intent, Policy, RiskScore, AuditRecord, Action), AuditWriter | Nothing — built first |
| B2 | Core Pipeline | Intent Engine, Policy Engine, Conflict Resolution, Orchestrator skeleton | B1 |
| B3 | Risk & Decision | Risk/Trust Quantifier, Decision Engine, rollback plan generation, dry-run mode | B2 determinism proven |
| B4 | Governance & Human Controls | Governance Gate, mode routing, Approval Queue, RBAC, emergency halt | B3 |
| B5 | Execution & Rollback | 4 action executors, rollback handlers, mock adapters, adapter abstraction | B4 |
| B6 | Agent Infrastructure | Agent Registry, Lifecycle Manager, X.509 auth, cryptographic tier boundaries at API gateway | B5 |
| B7 | Ethics & Safety Gates | Ethics Evaluator, LLM Shadow, Bias/Harm detection, Agent Containment, Ethics Audit Trail | B6 |
| B8 | Councils & Learning | 3 AI Councils, Council Mode Selector, Closed-Loop Feedback, Learning Agent, Observability | B7 |

**Running alongside all backend phases:**
- SoT Adapter (Nautobot/NetBox/InfraHub) — needed from B2 for canonical state reads; write-back from B5
- CI/CD — in place from day one, expands with each phase
- Architecture agent — fires after each phase completes

### Frontend Track

| Phase | Name | Key Components | Backend Dependency |
|---|---|---|---|
| F1 | Design System | Base component library (WCAG 2.1 AA), Tailwind theme, typography, colour system, form primitives | None — starts in parallel with B1 |
| F2 | Intent Dashboard | Intent submission form, intent list view, pipeline status tracker, intent detail view | B2 (Intent API) |
| F3 | Approval Queue UI | Human-in-loop review interface, approve/reject/override controls, approval ticket timer display | B4 (Approval Queue API) |
| F4 | Audit Trail Viewer | Queryable audit log table, reasoning chain expander, intent history timeline | B2 (Audit API) |
| F5 | Topology View | Network graph canvas, intent-status node colouring, interface detail cards, intent overlay | B5 (Execution + SoT) |
| F6 | Risk & Governance Dashboard | Live risk score panels, council decision feed, ethics strikes log, observability metrics | B8 (Observability + Councils) |

### Architecture Agent Cadence

After every backend and frontend phase completes:
1. architecture-agent updates `docs/architecture/ARCHITECTURE.md`
2. architecture-agent regenerates affected `.drawio` diagrams
3. Diagrams committed alongside the phase completion commit

### Key Build Order Rules

1. **Audit first, always** — AuditWriter is B1; nothing in B2–B8 runs before it exists
2. **Prove determinism before proceeding** — Policy Engine (B2) must pass 100+ identical-input tests before B3 starts
3. **Tier boundaries are cryptographic** — Agent tier enforcement (B6) is at the API gateway via X.509 claims, not configuration
4. **Ethics gate is mandatory** — No Tier 3 action executes until B7 is complete
5. **Councils never execute** — They route decisions back to pipeline or humans; they do not act directly
6. **Human override is always available** — Emergency halt (B4) must remain operational even if the main pipeline is down
7. **Frontend is WCAG 2.1 AA from F1** — Accessibility is built into the design system, not retrofitted

---

## 17. Deliverables

| Artifact | Path |
|---|---|
| CLAUDE.md | `/auto_networking/CLAUDE.md` |
| Settings | `/auto_networking/.claude/settings.json` |
| CI/CD workflows | `/auto_networking/.github/workflows/*.yml` |
| Backend skeleton | `/auto_networking/src/anif_platform/*/` |
| Frontend skeleton | `/auto_networking/src/anif_ui/` |
| Test skeleton | `/auto_networking/tests/` |
| Alembic setup | `/auto_networking/migrations/` |
| Docker stack | `/auto_networking/docker/docker-compose.yml` |
| Simulation topologies | `/auto_networking/simulation/topologies/` |
| SoT MCP server | `/auto_networking/src/anif_platform/sot/` |
| Python project | `/auto_networking/pyproject.toml` |
| Env template | `/auto_networking/.env.example` |
| ANIF schemas | `/auto_networking/schemas/` |
| Living architecture doc | `/auto_networking/docs/architecture/ARCHITECTURE.md` |
| Draw.io diagrams (7) | `/auto_networking/docs/architecture/diagrams/*.drawio` |
| This spec | `/auto_networking/docs/superpowers/specs/2026-04-12-claude-workspace-design.md` |
