# Claude Workspace Design — auto_networking Platform

**Date:** 2026-04-12
**Status:** Approved
**Repo:** auto_networking
**Companion spec repo:** Autonomous-Networking-Infrastructure-Framework-ANIF

---

## Overview

Set up the `auto_networking` repository as a fully instrumented Claude Code workspace for building the ANIF reference platform implementation. The workspace provides Claude with everything needed to build the platform autonomously: directory structure, CLAUDE.md instructions, MCP server connectivity, a 7-agent quality mesh, automated hooks, and 9 installed plugins — all wired to the Spec-Driven Development + Ralph Loop methodology.

---

## 1. Repository Directory Structure

```
auto_networking/
├── CLAUDE.md                            ← platform build instructions, agent definitions, SDD workflow
├── .claude/
│   └── settings.json                    ← MCP servers, hooks, plugin list
├── src/
│   └── anif_platform/
│       ├── __init__.py
│       ├── schemas/                     ← Pydantic models — Intent, Policy, RiskScore, AuditRecord
│       ├── audit/                       ← AuditWriter — tamper-evident records
│       ├── policy/                      ← PolicyEvaluator — deterministic evaluation
│       ├── risk/                        ← RiskScorer — 0–100 with component breakdown
│       ├── intent/                      ← IntentValidator — schema + constraint validation
│       ├── governance/                  ← GovernanceGate — routes auto/recommend/manual/council
│       ├── pipeline/                    ← Pipeline stages with rollback
│       ├── agents/                      ← AgentRegistry — lifecycle + trust level
│       ├── auth/                        ← CertificateVerifier — X.509 per-request
│       ├── ethics/                      ← EthicsEvaluator — runs before every Tier 3 action
│       ├── monitoring/                  ← SecurityMonitor — structured monitoring events
│       └── human_loop/                  ← ApprovalQueue — recommendations + override records
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── schemas/                             ← ANIF YAML schemas (intent, action, policy, risk, audit)
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/
│   └── superpowers/
│       └── specs/                       ← design documents (this file lives here)
├── pyproject.toml
└── .env.example
```

Module build order matches `CLAUDE_PLATFORM_BUILD_GUIDE.md` in the ANIF repo exactly. Each directory corresponds to one module. No module is created before its dependency is complete.

---

## 2. Tech Stack

| Technology | Version | Role |
|---|---|---|
| Python | 3.11+ | Primary language |
| FastAPI | current | REST API endpoints |
| Pydantic v2 | current | Schema validation |
| pytest + pytest-asyncio | current | TDD test framework |
| Docker + docker-compose | current | Containerisation + local integration env |
| Redis 7+ | current | Intent queue, message bus |
| PostgreSQL 15+ | current | Audit trail, risk register |
| ruff | current | Linting + auto-fix |
| black | current | Formatting |
| mypy | current | Static type checking |

---

## 3. MCP Servers

Configured in `.claude/settings.json` under `mcpServers`. All credentials reference environment variables — no secrets in config files.

| Name | Package | Purpose |
|---|---|---|
| `filesystem` | `@modelcontextprotocol/server-filesystem` | Read/write repo files with scoped access |
| `git` | `@modelcontextprotocol/server-git` | Log, diff, blame, branch operations |
| `postgres` | `@modelcontextprotocol/server-postgres` | Query audit DB + risk register live |
| `docker` | `mcp-server-docker` | Inspect containers, logs, service health |

---

## 4. Hooks

Configured in `.claude/settings.json` under `hooks`. Fire automatically — no manual invocation needed.

| Event | Matcher | Command |
|---|---|---|
| `PostToolUse` | `Edit\|Write\|MultiEdit` | `ruff check --fix <changed .py files>` |
| `PostToolUse` | `Edit\|Write\|MultiEdit` | `black <changed .py files>` |
| `PostToolUse` | `Edit\|Write\|MultiEdit` | `mypy <changed .py files>` |
| `PostToolUse` | `Edit\|Write\|MultiEdit` (`.yml`/`.json`) | `ibn-agent` intent schema lint |

Hooks run against changed files only, not the entire codebase. Output capped to prevent context flood.

---

## 5. Agent Mesh

All 7 agents are defined in `CLAUDE.md`. They are invoked via the `Agent` tool during development. Each agent has a defined trigger, scope, and prompt template in CLAUDE.md.

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
- **Trigger:** After any `.yml` or `.json` intent file is created or edited; after any intent-processing code is changed
- **Scope:** Intent files + ANIF-300/301 spec + `schemas/intent_schema.yml`
- **Dual role:**
  1. **Schema linting** — validates intent files against `schemas/intent_schema.yml`; checks all required fields (service, environment, objectives, constraints, policies, priority); validates field types, enum values, and constraint ranges
  2. **IBN best practice enforcement** — declarative over imperative (no implementation detail leakage into intents), idempotency of intent expressions, proper abstraction layer separation, correct use of objectives vs constraints vs policies, ANIF-300 and ANIF-301 compliance for both network intents (routing, QoS, segmentation, zero-trust) and infrastructure intents (compute, storage, connectivity, scaling)

---

## 6. Plugins

Nine plugins installed at workspace level:

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

---

## 7. Development Methodology

### Spec-Driven Development (SDD) + Ralph Loop

Every module follows this exact sequence:

```
1. READ    — read ANIF-NNN spec for the module; list every MUST and MUST NOT explicitly
2. GENERATE — invoke test-gen-agent → generates failing pytest stubs from MUSTs
3. VERIFY  — run tests; confirm all fail (tests that pass before implementation are invalid)
4. LOOP    — /ralph-loop "implement <module> until all tests pass" --completion-promise "COMPLETE" --max-iterations 30
5. REVIEW  — invoke spec-review-agent → every MUST covered by test + implementation
6. QUALITY — invoke best-practices-agent → SOLID, naming, DI, no god classes
7. IBN     — invoke ibn-agent (if module touches intent processing)
8. SECURE  — invoke security-agent → ANIF-840–849 + OWASP
9. COMMIT  — commit message format: `feat: implement ANIF-NNN <description>`
```

Steps 4–9 may loop. A module is not complete until steps 5, 6, and 8 all pass.

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

## 8. CLAUDE.md Structure

The `CLAUDE.md` in `auto_networking` contains:

1. **What this repo is** — platform implementation that conforms to ANIF; link to ANIF repo
2. **ANIF spec reference** — path to companion repo; which spec documents map to which modules
3. **Tech stack** — exact versions and why
4. **Module build order** — numbered list matching Section 1 directory order; no module N before N-1 complete
5. **SDD + Ralph Loop workflow** — the 9-step sequence from Section 7
6. **Agent definitions** — all 7 agents with triggers, scope, and prompt templates
7. **MCP server usage** — when to use each MCP
8. **What not to do** — no gold-plating, no features without spec coverage, no tests after code, no bare excepts, no American English in spec-adjacent comments
9. **Schema standards** — intent YAML validation rules, ibn-agent triggers

---

## 9. .env.example

Documents all required environment variables:

```
POSTGRES_URL=postgresql://user:password@localhost:5432/anif
REDIS_URL=redis://localhost:6379
ANIF_SPEC_REPO_PATH=/path/to/Autonomous-Networking-Infrastructure-Framework-ANIF
LOG_LEVEL=INFO
```

---

## 10. pyproject.toml

Defines:
- Project metadata and Python version constraint (>=3.11)
- All runtime dependencies with minimum versions
- Dev dependencies: pytest, pytest-asyncio, ruff, black, mypy
- ruff configuration: line length 100, select E/F/I/N/UP, auto-fixable rules
- mypy configuration: strict mode, disallow untyped defs
- pytest configuration: asyncio mode auto, test paths

---

## Deliverables

| Artifact | Path |
|---|---|
| CLAUDE.md | `/auto_networking/CLAUDE.md` |
| Settings | `/auto_networking/.claude/settings.json` |
| Directory skeleton | `/auto_networking/src/anif_platform/*/` |
| Test skeleton | `/auto_networking/tests/unit/` + `tests/integration/` |
| Docker config | `/auto_networking/docker/docker-compose.yml` |
| Python project | `/auto_networking/pyproject.toml` |
| Env template | `/auto_networking/.env.example` |
| ANIF schemas | `/auto_networking/schemas/` |
| This spec | `/auto_networking/docs/superpowers/specs/2026-04-12-claude-workspace-design.md` |
