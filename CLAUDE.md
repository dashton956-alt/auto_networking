# CLAUDE.md — ANIF Platform

## What This Repo Is

This repository implements the ANIF reference platform — working software that conforms to the Autonomous Networking & Infrastructure Framework specification. It translates ANIF MUST requirements into tested, running code.

**Framework spec repo:** `/home/dan/Desktop/github/Autonomous-Networking-Infrastructure-Framework-ANIF/`
**Platform build guide:** `Autonomous-Networking-Infrastructure-Framework-ANIF/CLAUDE_PLATFORM_BUILD_GUIDE.md`

The `nautobot-intent-network-app` is a separate project. Nautobot, NetBox, and InfraHub are used here **only as sources of truth** (device inventory, topology, IP prefixes) with metadata write-back (tags, comments, custom fields on devices/interfaces/connections). This platform owns all intent authoring, validation, policy evaluation, risk scoring, execution, and audit independently.

---

## ANIF Spec → Module Mapping

| Module | ANIF Spec Documents |
|---|---|
| `src/anif_platform/schemas/` | ANIF-300, ANIF-600 |
| `src/anif_platform/audit/` | ANIF-107, ANIF-724 |
| `src/anif_platform/policy/` | ANIF-302, ANIF-303 |
| `src/anif_platform/risk/` | ANIF-304 |
| `src/anif_platform/intent/` | ANIF-300, ANIF-301 |
| `src/anif_platform/governance/` | ANIF-301, ANIF-406 |
| `src/anif_platform/pipeline/` | ANIF-305, ANIF-306, ANIF-308 |
| `src/anif_platform/agents/` | ANIF-803, ANIF-805 |
| `src/anif_platform/auth/` | ANIF-843 |
| `src/anif_platform/ethics/` | ANIF-720–725 |
| `src/anif_platform/monitoring/` | ANIF-401, ANIF-846 |
| `src/anif_platform/human_loop/` | ANIF-402, ANIF-404 |
| `src/anif_platform/sot/` | ANIF-307 |
| `src/anif_ui/` | ANIF-404 (Approval Queue UI), ANIF-402 (Audit viewer) |

---

## Tech Stack

| Technology | Version | Role |
|---|---|---|
| Python | 3.13 | Primary backend language |
| FastAPI | >=0.111 | REST API framework |
| Pydantic | v2 >=2.7 | Schema validation and serialisation |
| SQLAlchemy | 2 >=2.0.30 | ORM and database abstraction |
| Alembic | >=1.13 | Database migration management |
| pytest + pytest-asyncio | latest | Test framework |
| ruff | latest | Linting and import sorting |
| black | latest | Code formatting |
| mypy (strict) | latest | Static type checking |
| React | 18+ | Frontend UI framework |
| TypeScript | 5 | Frontend type safety |
| Vite | 5 | Frontend build tool |
| Tailwind CSS | 3 | Utility-first CSS framework |
| Playwright | latest | E2E testing and WCAG audits |
| Docker Compose | v2 | Local service orchestration |
| PostgreSQL | 15 | Primary relational database |
| Redis | 7 | Queue backend and caching |
| Prometheus + Grafana | latest | Metrics collection and dashboards |
| Containerlab | installed | Network topology simulation |
| Batfish | latest | Static network config analysis |

---

## Platform Build Order

### Backend Track (B1–B8)

| Phase | Name | Key Deliverable |
|---|---|---|
| B1 | Foundation & Data Models | Pydantic schemas + AuditWriter |
| B2 | Core Pipeline | Intent Engine + Policy Engine + Orchestrator |
| B3 | Risk & Decision | RiskScorer + DecisionEngine + dry-run |
| B4 | Governance & Human Controls | GovernanceGate + ApprovalQueue + RBAC |
| B5 | Execution & Rollback | 4 action executors + rollback handlers |
| B6 | Agent Infrastructure | AgentRegistry + X.509 auth + tier boundaries |
| B7 | Ethics & Safety | EthicsEvaluator + LLM Shadow + Containment |
| B8 | Councils & Learning | 3 AI Councils + Feedback + Learning Agent |

**Phase rules:**

- Never start phase N before phase N-1 is complete with all tests passing
- AuditWriter (B1) is a dependency of every module — must write before any function returns
- Policy Engine (B2) must prove determinism with 100+ identical-input test runs before B3 starts
- No Tier 3 action executes until B7 is complete

### Frontend Track (F1–F6)

| Phase | Name | Backend Dependency |
|---|---|---|
| F1 | Design System | Starts with B1, no backend dependency |
| F2 | Intent Dashboard | B2 (Intent API) |
| F3 | Approval Queue UI | B4 |
| F4 | Audit Trail Viewer | B2 (Audit API) |
| F5 | Topology View | B5 |
| F6 | Risk & Governance Dashboard | B8 |

All frontend phases must pass WCAG 2.1 AA before merging.

---

## Development Methodology: SDD + Ralph Loop

11-step sequence — do not skip steps:

1. **READ** — open ANIF-NNN spec; list every MUST and MUST NOT explicitly
2. **GENERATE** — invoke test-gen-agent → pytest stubs from MUSTs
3. **VERIFY** — confirm all stubs FAIL (a passing test before implementation is invalid)
4. **LOOP** — `/ralph-loop` prompt (see template below)
5. **REVIEW** — invoke spec-review-agent
6. **QUALITY** — invoke best-practices-agent
7. **IBN** — invoke ibn-agent (if intent processing touched)
8. **MIGRATE** — invoke migration-agent (if models changed)
9. **SECURE** — invoke security-agent
10. **COMPLY** — invoke compliance-agent (if UI, API contract, auth, or data model touched)
11. **COMMIT** — format: `feat: implement ANIF-NNN <description>`

### Ralph Loop Prompt Template

```
Implement the <module_name> module for the ANIF platform.

Requirements source: /home/dan/Desktop/github/Autonomous-Networking-Infrastructure-Framework-ANIF/docs/<series>/<ANIF-NNN>.md
Test file: tests/unit/test_<module>.py
Implementation target: src/anif_platform/<module>/

Rules:
- Every MUST requirement in ANIF-NNN must be satisfied
- AuditWriter.write() must be called before any function returns
- No implementation without a passing test
- Run tests after every change: .venv/bin/pytest tests/unit/test_<module>.py -v
- If tests fail, read the failure output, diagnose root cause, fix, re-run
- Do not add features not covered by ANIF-NNN requirements

Output <promise>COMPLETE</promise> when all tests pass and spec-review-agent approves.
```

---

## Rate Limit Recovery

When Claude Pro usage limit is reached:

1. Stop hook fires → writes context to `.claude/resume.md`
2. Run: `/schedule "resume task from .claude/resume.md"` in 5.5h
3. On restart, read `.claude/resume.md` and continue

---

## Agent Definitions

### lint-agent

**Trigger:** After any `.py` file edit
**Scope:** Changed files only
**Prompt template:** Run `ruff check --fix` and `black` on `<files>`, report unfixable violations

---

### type-agent

**Trigger:** After a module is marked complete
**Scope:** Module directory
**Prompt template:** Run `mypy --strict` on `src/anif_platform/<module>/`, flag missing annotations and `Any` usage

---

### security-agent

**Trigger:** Before any commit
**Scope:** Staged changes
**Prompt template:** Check against ANIF-840–849 and OWASP Top 10, flag command injection, unvalidated input, hardcoded secrets, and insecure defaults

---

### test-gen-agent

**Trigger:** When starting a new module (before implementation)
**Scope:** Target ANIF spec document
**Prompt template:** Read ANIF-NNN, extract every MUST/MUST NOT, generate pytest stub with one test per requirement, confirm all FAIL

---

### spec-review-agent

**Trigger:** After a module is complete
**Scope:** Module source + ANIF spec document
**Prompt template:** Map each MUST/MUST NOT to a test and implementation, flag any requirement with no test or implementation

---

### best-practices-agent

**Trigger:** After any implementation
**Scope:** Changed files
**Prompt template:** Check SOLID, no god classes, no bare except, dependency injection, no magic numbers, structlog, no circular imports, consistent naming

---

### ibn-agent

**Trigger:** After any `.yml`/`.json` intent file edit or intent-processing code change
**Scope:** Intent files + `schemas/intent_schema.yml` + ANIF-300/301
**Prompt template (dual role):**

- *Schema lint:* validate against `intent_schema.yml`, check all required fields (service, environment, objectives, constraints, policies, priority)
- *IBN best practices:* declarative over imperative, no implementation detail leakage, idempotency, proper layer separation, ANIF-300/301 compliance

---

### compliance-agent

**Trigger:** Before commit touching UI, API contracts, data models, or auth
**Scope:** Staged changes + running app via Playwright
**Prompt template:** Check WCAG 2.1 AA, ADA/Section 508, ISO 27001 (audit fields, access controls, encryption), HIPAA (minimum access, PHI encryption), GDPR (data residency, deletion endpoints)

---

### architecture-agent

**Trigger:** After any phase completes, schema change, or significant architectural decision
**Scope:** Entire repo + `docs/architecture/`
**Prompt template:** Update `ARCHITECTURE.md` to reflect what was built, update affected `.drawio` XML files in `docs/architecture/diagrams/` (system-context, component, sequence-pipeline, agent-tiers, data-flow, sot-integration, deployment), commit with `"docs: update architecture diagrams after <phase>"`

---

### migration-agent

**Trigger:** When SQLAlchemy models change
**Scope:** `src/anif_platform/schemas/` + `migrations/`
**Prompt template:** Run `alembic revision --autogenerate`, verify `upgrade()` is correct, verify `downgrade()` exists, flag DESTRUCTIVE operations with comment, run `alembic upgrade head` to verify

---

## MCP Server Usage

| MCP Server | When to Use |
|---|---|
| `filesystem` | Reading repo files when standard tools are insufficient |
| `git` | Checking history, blame, and diff across branches |
| `postgres` | Querying audit trail and risk register during debugging |
| `docker` | Inspecting containers, logs, and service health |
| `playwright` | UI tests, WCAG audits, screenshots for architecture docs |
| `figma` | Reading design specs before implementing UI components |
| `prometheus` | Querying live metrics during observability work |
| `sot` | Fetching device/topology data and writing back intent tags |

---

## SoT Adapter

Selected via `SOT_BACKEND` env var: `nautobot` | `netbox` | `infrahub`

**Read operations:** device inventory, topology, IP prefixes

**Write-back:** tags + comments + custom fields (`intent_status`, `last_intent_id`, `intent_applied_at`) on devices, interfaces, and connections

**Never:** modify device configs, IP assignments, or topology records

**Protocol interface:** `src/anif_platform/sot/protocol.py`

---

## Network Simulation

**Containerlab (primary):** topology files in `simulation/topologies/`

Run: `sudo containerlab deploy -t simulation/topologies/<topology>.yml`

**Batfish (complementary):** config snapshots in `simulation/batfish/`

Use for static config analysis before pushing.

---

## What Not To Do

- No gold-plating — if a MUST doesn't exist in the ANIF spec, don't implement it
- No tests after code — tests are written from spec MUSTs before implementation
- No bare except — always catch specific exception types
- No migration without `downgrade()` — every Alembic migration needs a working rollback
- No destructive migration without human approval — add `# DESTRUCTIVE` comment
- No American English — use British English (organisation, not organization)
- No module-level singletons — use dependency injection
- No forward-referencing unplanned ANIF documents
- No features not covered by tests — YAGNI

---

## Schema Standards

All intent YAML files must pass ibn-agent validation.

**Schema source:** `schemas/intent_schema.yml`

`ibn-agent` fires via `PostToolUse` hook on `.yml`/`.json` edits.

**Commit message format:** `feat: implement ANIF-NNN <description>`
