# Claude Workspace Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the `auto_networking` repo as a fully instrumented Claude Code workspace ready to build the ANIF platform — all tooling, agents, MCP servers, CI/CD, and project structure in place before a single line of platform code is written.

**Architecture:** All configuration lives in `.claude/settings.json` (project-level MCP + hooks) and `CLAUDE.md` (agent definitions + build instructions). Backend (Python/FastAPI) and frontend (React/TypeScript) are independent source trees under `src/`. The workspace scaffold produces no platform logic — only the environment that will build it.

**Tech Stack:** Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, pytest, ruff, mypy, black, React 18, TypeScript 5, Vite 5, Tailwind CSS 3, Docker Compose, PostgreSQL 15, Redis 7, Prometheus, Grafana, Containerlab, Batfish, Playwright MCP, Figma MCP.

**Spec:** `docs/superpowers/specs/2026-04-12-claude-workspace-design.md`

---

## Prerequisites

Before starting Task 1, verify or install:

- [ ] **Check Python version**
  ```bash
  python3 --version
  # Expected: Python 3.13.x
  ```

- [ ] **Install Node.js + npm** (needed for React frontend and MCP servers)
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
  node --version   # Expected: v20.x.x
  npm --version    # Expected: 10.x.x
  ```

- [ ] **Install Docker + Docker Compose**
  ```bash
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker $USER
  # Log out and back in, then:
  docker --version           # Expected: Docker version 26.x.x
  docker compose version     # Expected: Docker Compose version v2.x.x
  ```

- [ ] **Install uv (fast Python package manager)**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  uv --version   # Expected: uv 0.x.x
  ```

---

## File Map

```
auto_networking/
├── .claude/
│   ├── settings.json          ← Task 5: MCP servers + hooks
│   └── resume.md              ← Task 20: rate limit recovery template
├── .github/
│   └── workflows/
│       ├── ci.yml             ← Task 9
│       ├── accessibility.yml  ← Task 10
│       ├── intent-validate.yml← Task 11
│       └── compliance.yml     ← Task 12
├── src/
│   ├── anif_platform/
│   │   ├── __init__.py        ← Task 3
│   │   ├── schemas/__init__.py
│   │   ├── audit/__init__.py
│   │   ├── policy/__init__.py
│   │   ├── risk/__init__.py
│   │   ├── intent/__init__.py
│   │   ├── governance/__init__.py
│   │   ├── pipeline/__init__.py
│   │   ├── agents/__init__.py
│   │   ├── auth/__init__.py
│   │   ├── ethics/__init__.py
│   │   ├── monitoring/__init__.py
│   │   ├── human_loop/__init__.py
│   │   └── sot/
│   │       ├── __init__.py    ← Task 18
│   │       ├── protocol.py    ← Task 18
│   │       ├── nautobot.py    ← Task 18
│   │       ├── netbox.py      ← Task 18
│   │       └── infrahub.py    ← Task 18
│   └── anif_ui/               ← Task 15: React scaffold
│       ├── package.json
│       ├── vite.config.ts
│       ├── tsconfig.json
│       ├── tailwind.config.ts
│       ├── index.html
│       └── src/
│           ├── main.tsx
│           ├── App.tsx
│           ├── components/
│           ├── pages/
│           ├── hooks/
│           └── types/
├── tests/
│   ├── conftest.py            ← Task 17
│   ├── unit/
│   └── integration/
├── schemas/                   ← Task 13: copied from ANIF repo
├── migrations/                ← Task 14: Alembic setup
│   ├── alembic.ini
│   ├── env.py
│   └── script.py.mako
├── simulation/
│   ├── topologies/            ← Task 19
│   └── batfish/               ← Task 19
├── docker/
│   ├── Dockerfile             ← Task 8
│   └── docker-compose.yml     ← Task 7
├── docs/
│   ├── architecture/
│   │   ├── ARCHITECTURE.md    ← Task 16
│   │   └── diagrams/          ← Task 16: 7 .drawio stubs
│   └── superpowers/
│       ├── plans/             ← this file
│       └── specs/
├── CLAUDE.md                  ← Task 4
├── pyproject.toml             ← Task 2
└── .env.example               ← Task 6
```

---

## Task 1: Create Directory Skeleton

**Files:** All directories listed in the file map above.

- [ ] **Create all directories**
  ```bash
  cd /home/dan/Desktop/github/auto_networking
  mkdir -p .claude
  mkdir -p .github/workflows
  mkdir -p src/anif_platform/{schemas,audit,policy,risk,intent,governance,pipeline,agents,auth,ethics,monitoring,human_loop,sot}
  mkdir -p src/anif_ui/src/{components,pages,hooks,types}
  mkdir -p tests/{unit,integration}
  mkdir -p schemas
  mkdir -p migrations/versions
  mkdir -p simulation/{topologies,batfish}
  mkdir -p docker
  mkdir -p docs/architecture/diagrams
  mkdir -p docs/superpowers/{plans,specs}
  ```

- [ ] **Verify**
  ```bash
  find . -type d | grep -v ".git" | sort
  # Expected: all directories listed in file map
  ```

- [ ] **Commit**
  ```bash
  git add -A
  git commit -m "chore: create workspace directory skeleton"
  ```

---

## Task 2: Python Project Configuration (pyproject.toml)

**Files:**
- Create: `pyproject.toml`

- [ ] **Write pyproject.toml**

  Create `/home/dan/Desktop/github/auto_networking/pyproject.toml`:
  ```toml
  [build-system]
  requires = ["hatchling"]
  build-backend = "hatchling.build"

  [project]
  name = "anif-platform"
  version = "0.1.0"
  description = "ANIF Reference Platform — autonomous networking intent pipeline"
  requires-python = ">=3.11"
  dependencies = [
      "fastapi>=0.111.0",
      "uvicorn[standard]>=0.29.0",
      "pydantic>=2.7.0",
      "pydantic-settings>=2.3.0",
      "sqlalchemy>=2.0.30",
      "asyncpg>=0.29.0",
      "psycopg2-binary>=2.9.9",
      "alembic>=1.13.1",
      "redis>=5.0.4",
      "httpx>=0.27.0",
      "cryptography>=42.0.0",
      "python-jose[cryptography]>=3.3.0",
      "prometheus-client>=0.20.0",
      "structlog>=24.1.0",
      "PyYAML>=6.0.1",
  ]

  [project.optional-dependencies]
  dev = [
      "pytest>=8.2.0",
      "pytest-asyncio>=0.23.6",
      "pytest-cov>=5.0.0",
      "ruff>=0.4.5",
      "black>=24.4.2",
      "mypy>=1.10.0",
      "types-PyYAML>=6.0.12",
      "types-redis>=4.6.0",
  ]

  [tool.ruff]
  line-length = 100
  target-version = "py311"

  [tool.ruff.lint]
  select = ["E", "F", "I", "N", "UP", "B", "SIM"]
  fixable = ["ALL"]
  ignore = ["E501"]

  [tool.ruff.lint.isort]
  known-first-party = ["anif_platform"]

  [tool.black]
  line-length = 100
  target-version = ["py311"]

  [tool.mypy]
  python_version = "3.11"
  strict = true
  disallow_untyped_defs = true
  disallow_any_generics = true
  warn_return_any = true
  warn_unused_ignores = true
  plugins = ["pydantic.mypy"]

  [[tool.mypy.overrides]]
  module = ["jose.*", "prometheus_client.*"]
  ignore_missing_imports = true

  [tool.pytest.ini_options]
  asyncio_mode = "auto"
  testpaths = ["tests"]
  addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"
  ```

- [ ] **Install dependencies with uv**
  ```bash
  cd /home/dan/Desktop/github/auto_networking
  uv venv .venv
  uv pip install -e ".[dev]"
  ```

- [ ] **Verify**
  ```bash
  .venv/bin/python -c "import fastapi, pydantic, sqlalchemy, alembic; print('all deps ok')"
  # Expected: all deps ok
  ```

- [ ] **Commit**
  ```bash
  git add pyproject.toml
  git commit -m "chore: add pyproject.toml with full dependency set"
  ```

---

## Task 3: Python Module Skeletons

**Files:** `src/anif_platform/__init__.py` and one `__init__.py` per submodule.

- [ ] **Write root __init__.py**

  Create `src/anif_platform/__init__.py`:
  ```python
  """ANIF Platform — autonomous networking intent pipeline."""

  __version__ = "0.1.0"
  ```

- [ ] **Write submodule __init__.py files**
  ```bash
  for mod in schemas audit policy risk intent governance pipeline agents auth ethics monitoring human_loop sot; do
    cat > src/anif_platform/$mod/__init__.py << 'EOF'
  """ANIF Platform module — implementation pending."""
  EOF
  done
  ```

- [ ] **Write shared exceptions module**

  Create `src/anif_platform/exceptions.py`:
  ```python
  """Platform-wide exception hierarchy."""


  class ANIFError(Exception):
      """Base exception for all ANIF platform errors."""


  class IntentValidationError(ANIFError):
      """Raised when an intent fails schema or constraint validation."""


  class PolicyEvaluationError(ANIFError):
      """Raised when policy evaluation encounters an unrecoverable error."""


  class RiskScoringError(ANIFError):
      """Raised when risk scoring cannot produce a deterministic result."""


  class AuditWriteError(ANIFError):
      """Raised when an audit record cannot be written. Halts the pipeline."""


  class GovernanceError(ANIFError):
      """Raised when governance gate encounters an invalid state."""


  class SoTAdapterError(ANIFError):
      """Raised when the source-of-truth adapter cannot reach its backend."""
  ```

- [ ] **Verify imports clean**
  ```bash
  .venv/bin/python -c "from anif_platform import __version__; print(__version__)"
  # Expected: 0.1.0
  ```

- [ ] **Commit**
  ```bash
  git add src/
  git commit -m "chore: add Python module skeleton and exception hierarchy"
  ```

---

## Task 4: CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

This is the primary instruction file Claude reads at the start of every session.

- [ ] **Write CLAUDE.md**

  Create `/home/dan/Desktop/github/auto_networking/CLAUDE.md`:
  ````markdown
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
  | Python | 3.13 | Primary language |
  | FastAPI | >=0.111 | REST API |
  | Pydantic v2 | >=2.7 | Schema validation |
  | SQLAlchemy 2 | >=2.0.30 | ORM |
  | Alembic | >=1.13 | DB migrations |
  | pytest + pytest-asyncio | current | TDD |
  | ruff | current | Lint + auto-fix |
  | black | current | Format |
  | mypy (strict) | current | Type checking |
  | React 18 + TypeScript 5 | current | Management UI |
  | Vite 5 + Tailwind 3 | current | Frontend build |
  | Playwright | current | E2E + a11y testing |
  | Docker Compose | v2 | Local dev stack |
  | PostgreSQL 15 | current | Audit trail, risk register |
  | Redis 7 | current | Intent queue, message bus |
  | Prometheus + Grafana | current | Observability |
  | Containerlab | installed | Network simulation |
  | Batfish | current | Static config analysis |

  ---

  ## Platform Build Order

  ### Backend Track

  | Phase | Name | Key Deliverable |
  |---|---|---|
  | B1 | Foundation & Data Models | Pydantic schemas + AuditWriter |
  | B2 | Core Pipeline | Intent Engine + Policy Engine + Orchestrator |
  | B3 | Risk & Decision | RiskScorer + DecisionEngine + dry-run mode |
  | B4 | Governance & Human Controls | GovernanceGate + ApprovalQueue + RBAC |
  | B5 | Execution & Rollback | 4 action executors + rollback handlers |
  | B6 | Agent Infrastructure | AgentRegistry + X.509 auth + tier boundaries |
  | B7 | Ethics & Safety | EthicsEvaluator + LLM Shadow + Containment |
  | B8 | Councils & Learning | 3 AI Councils + Feedback + Learning Agent |

  **Rules:**
  - Never start phase N before phase N-1 is complete and all tests pass.
  - AuditWriter (B1) is a dependency of every module — it must write before any function returns.
  - Policy Engine (B2) must prove determinism with 100+ identical-input test runs before B3 starts.
  - No Tier 3 action executes until B7 is complete.

  ### Frontend Track

  | Phase | Name | Backend Dependency |
  |---|---|---|
  | F1 | Design System + Component Library | None (starts with B1) |
  | F2 | Intent Dashboard | B2 (Intent API) |
  | F3 | Approval Queue UI | B4 (Approval Queue API) |
  | F4 | Audit Trail Viewer | B2 (Audit API) |
  | F5 | Topology View | B5 (Execution + SoT) |
  | F6 | Risk & Governance Dashboard | B8 (Observability + Councils) |

  All frontend phases must pass WCAG 2.1 AA before merging.

  ---

  ## Development Methodology: SDD + Ralph Loop

  Every module follows this sequence. Do not skip steps.

  ```
  1. READ      — open ANIF-NNN spec; list every MUST and MUST NOT explicitly before writing any code
  2. GENERATE  — invoke test-gen-agent → pytest stubs from MUSTs
  3. VERIFY    — run stubs; confirm all FAIL (a test that passes before implementation is invalid)
  4. LOOP      — /ralph-loop "<prompt>" --completion-promise "COMPLETE" --max-iterations 30
  5. REVIEW    — invoke spec-review-agent → every MUST has a test + implementation
  6. QUALITY   — invoke best-practices-agent → SOLID, DI, no god classes, no bare except
  7. IBN       — invoke ibn-agent (if module touches intent processing or schema)
  8. MIGRATE   — invoke migration-agent (if SQLAlchemy models changed)
  9. SECURE    — invoke security-agent → ANIF-840–849 + OWASP
  10. COMPLY   — invoke compliance-agent (if UI, API contract, auth, or data model touched)
  11. COMMIT   — `feat: implement ANIF-NNN <description>`
  ```

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

  When the Claude Pro usage limit is reached:

  1. Stop hook fires automatically → writes current task to `.claude/resume.md`
  2. Before closing, run: `/schedule "resume task from .claude/resume.md" in 5.5h`
  3. On restart, read `.claude/resume.md` and continue the loop

  ---

  ## Agent Definitions

  All agents are invoked via the `Agent` tool. Each has a defined trigger and scope.

  ### lint-agent
  **Trigger:** After any `.py` file edit
  **Scope:** Changed files only
  **Prompt:**
  ```
  Run ruff check --fix and black on these files: <files>
  Working directory: /home/dan/Desktop/github/auto_networking
  Command: .venv/bin/ruff check --fix <files> && .venv/bin/black <files>
  Report any violations that could not be auto-fixed.
  ```

  ### type-agent
  **Trigger:** After a module is marked complete
  **Scope:** Module directory
  **Prompt:**
  ```
  Run strict mypy analysis on src/anif_platform/<module>/
  Command: .venv/bin/mypy src/anif_platform/<module>/ --strict
  Flag: missing annotations, Any usage, untyped signatures.
  All must be resolved before the module is considered done.
  ```

  ### security-agent
  **Trigger:** Before any commit
  **Scope:** Staged changes
  **Prompt:**
  ```
  Review staged changes for security issues.
  Check against: ANIF-840–849 requirements, OWASP Top 10.
  Flag: command injection, unvalidated input, hardcoded secrets, insecure defaults,
  missing authentication, SQL injection, exposed internal errors.
  Spec path: /home/dan/Desktop/github/Autonomous-Networking-Infrastructure-Framework-ANIF/docs/840-ai-security/
  ```

  ### test-gen-agent
  **Trigger:** When starting a new module (before any implementation code)
  **Scope:** ANIF spec document for the module
  **Prompt:**
  ```
  Read ANIF-NNN at: /home/dan/Desktop/github/Autonomous-Networking-Infrastructure-Framework-ANIF/docs/<series>/<ANIF-NNN>.md
  Extract every MUST and MUST NOT requirement.
  Generate a pytest stub file at tests/unit/test_<module>.py with:
  - One test function per MUST requirement
  - One negative test function per MUST NOT requirement
  - Each test raises NotImplementedError (so it fails, not errors)
  - Docstring on each test stating the ANIF-NNN requirement it covers
  Run tests to confirm all FAIL before handing back.
  ```

  ### spec-review-agent
  **Trigger:** After a module is marked complete
  **Scope:** Module source + ANIF spec document
  **Prompt:**
  ```
  Map every MUST and MUST NOT in ANIF-NNN to:
  1. A test in tests/unit/test_<module>.py
  2. Implementation code in src/anif_platform/<module>/
  If any requirement has no corresponding test, list it as a gap.
  If any requirement has no implementation, list it as a gap.
  A module is NOT complete if any gap exists.
  ```

  ### best-practices-agent
  **Trigger:** After any implementation
  **Scope:** Changed files
  **Prompt:**
  ```
  Review the following files for Python and FastAPI best practices:
  <files>
  Check for violations of:
  - Single Responsibility Principle (no function/class doing more than one thing)
  - No god classes (classes > 200 lines are suspicious)
  - No bare except clauses (always catch specific exceptions)
  - Dependency injection (no module-level singletons that can't be mocked)
  - No magic numbers (constants must be named)
  - Structured logging via structlog (no print statements)
  - No circular imports
  - Consistent naming: snake_case functions/vars, PascalCase classes, UPPER_SNAKE constants
  Report violations with file:line references. Fix or explain each.
  ```

  ### ibn-agent
  **Trigger:** After any `.yml`/`.json` intent file edit; after any intent-processing code change
  **Scope:** Intent files + `schemas/intent_schema.yml` + ANIF-300/301
  **Prompt:**
  ```
  Perform dual-role intent validation:

  ROLE 1 — Schema lint:
  Validate <file> against schemas/intent_schema.yml.
  Required fields: service, environment, objectives, constraints, policies, priority.
  Check: field types, enum values, constraint ranges, no extra unknown fields.

  ROLE 2 — IBN best practices (ref: ANIF-300, ANIF-301):
  - Declarative over imperative: intents must state WHAT, not HOW
  - No implementation detail leakage (no IP addresses, interface names, vendor config in intents)
  - Idempotency: applying the same intent twice must produce the same state
  - Correct layer separation: objectives vs constraints vs policies are distinct concepts
  - Network intents: routing, QoS, segmentation, zero-trust must be expressed at service level
  - Infrastructure intents: compute, storage, connectivity, scaling at resource level

  Spec: /home/dan/Desktop/github/Autonomous-Networking-Infrastructure-Framework-ANIF/docs/300-core/
  ```

  ### compliance-agent
  **Trigger:** Before any commit touching UI, API contracts, data models, or auth
  **Scope:** Staged changes + running app (Playwright for UI)
  **Prompt:**
  ```
  Review staged changes for compliance violations:

  WCAG 2.1 AA (UI changes):
  - Contrast ratio >= 4.5:1 for normal text, >= 3:1 for large text
  - All interactive elements have ARIA labels
  - Full keyboard navigation (no mouse-only interactions)
  - Focus indicators visible

  ISO 27001 (data model / auth changes):
  - All data models have audit trail fields (created_at, updated_at, created_by)
  - Access controls documented and enforced
  - Encryption at rest for PII fields

  HIPAA (if any patient/health data paths touched):
  - Minimum necessary access enforced
  - PHI fields encrypted
  - Access log entries created for all PHI reads

  GDPR (API contract changes):
  - Data residency env vars referenced, not hardcoded
  - Deletion endpoints exist for user data

  Report violations with file:line references.
  ```

  ### architecture-agent
  **Trigger:** After any phase completes; after any schema change; after significant architectural decisions
  **Scope:** Entire repo + `docs/architecture/`
  **Prompt:**
  ```
  Update the living architecture documentation:

  1. Read docs/architecture/ARCHITECTURE.md
  2. Read the recently changed modules/files
  3. Update ARCHITECTURE.md to reflect what was actually built (not what was planned)
  4. For each affected diagram in docs/architecture/diagrams/:
     - Read the current .drawio XML
     - Update to reflect the new component/connection/flow
     - Write the updated XML back
  Diagrams to consider updating:
  - system-context.drawio (if external integrations changed)
  - component.drawio (if new modules added or interfaces changed)
  - sequence-pipeline.drawio (if pipeline flow changed)
  - agent-tiers.drawio (if agent model changed)
  - data-flow.drawio (if data flow changed)
  - sot-integration.drawio (if SoT adapter changed)
  - deployment.drawio (if docker-compose or infra changed)
  Commit changes with: "docs: update architecture diagrams after <phase>"
  ```

  ### migration-agent
  **Trigger:** When SQLAlchemy models change
  **Scope:** `src/anif_platform/schemas/` + `migrations/`
  **Prompt:**
  ```
  A SQLAlchemy model has changed. Generate an Alembic migration:
  1. Run: .venv/bin/alembic revision --autogenerate -m "<description>"
  2. Open the generated file in migrations/versions/
  3. Verify the upgrade() function is correct
  4. Verify a downgrade() function exists — if not, add one
  5. Flag any destructive operations (column drops, type changes) with a comment:
     # DESTRUCTIVE: requires human review before applying to production
  6. Run: .venv/bin/alembic upgrade head (against local dev DB)
  7. Verify migration applies cleanly
  ```

  ---

  ## MCP Server Usage

  | MCP | When to use |
  |---|---|
  | `filesystem` | Reading any file in the repo when standard tools are insufficient |
  | `git` | Checking history, blame, diff across branches |
  | `postgres` | Querying audit trail, risk register, intent state directly during debugging |
  | `docker` | Inspecting running containers, reading service logs, checking health |
  | `playwright` | Running UI tests, WCAG audits, taking screenshots for architecture docs |
  | `figma` | Reading design specs before implementing UI components |
  | `prometheus` | Querying live metrics during observability work |
  | `sot` | Fetching device/topology data and writing back intent tags during SoT module work |

  ---

  ## SoT Adapter

  Selected via `SOT_BACKEND` env var: `nautobot` | `netbox` | `infrahub`

  **Read operations:** device inventory, topology, IP prefixes.
  **Write-back:** tags + comments + custom fields (`intent_status`, `last_intent_id`, `intent_applied_at`) on devices, interfaces, and connections.
  **Never:** modify device configs, IP assignments, or topology records.

  Protocol interface: `src/anif_platform/sot/protocol.py`

  ---

  ## Network Simulation

  **Containerlab (primary):** topology files in `simulation/topologies/`. Use for integration tests that push intents and verify execution outcomes against real containers.

  **Batfish (complementary):** config snapshots in `simulation/batfish/`. Use for static analysis of generated network configs before pushing. Fast — no containers needed.

  Run containerlab topology:
  ```bash
  sudo containerlab deploy -t simulation/topologies/<topology>.yml
  ```

  ---

  ## What Not To Do

  - **No gold-plating** — if a MUST requirement does not exist in the ANIF spec, do not implement it
  - **No tests after code** — tests are written from spec MUSTs before implementation begins
  - **No bare except** — always catch specific exception types
  - **No migration without downgrade()** — every migration needs a working rollback
  - **No destructive migration without human approval** — add `# DESTRUCTIVE` comment; flag for review
  - **No American English** — use British English in all documentation and comments (organisation, not organization)
  - **No module-level singletons** — use dependency injection
  - **No forward-referencing unplanned ANIF documents** — only reference IDs in the authorised registry
  - **No features not covered by tests** — YAGNI

  ---

  ## Schema Standards

  All intent YAML files must pass ibn-agent validation.
  Schema source: `schemas/intent_schema.yml` (copied from ANIF repo).
  ibn-agent fires automatically via PostToolUse hook on `.yml`/`.json` edits.

  Commit message format: `feat: implement ANIF-NNN <description>`
  ````

- [ ] **Verify CLAUDE.md exists and is non-empty**
  ```bash
  wc -l CLAUDE.md
  # Expected: >200 lines
  ```

- [ ] **Commit**
  ```bash
  git add CLAUDE.md
  git commit -m "chore: add comprehensive CLAUDE.md with agent definitions and build order"
  ```

---

## Task 5: .claude/settings.json (MCP Servers + Hooks)

**Files:**
- Create: `.claude/settings.json`

- [ ] **Write settings.json**

  Create `/home/dan/Desktop/github/auto_networking/.claude/settings.json`:
  ```json
  {
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/dan/Desktop/github/auto_networking"],
        "env": {}
      },
      "git": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-git", "--repository", "/home/dan/Desktop/github/auto_networking"],
        "env": {}
      },
      "postgres": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres", "$POSTGRES_URL"],
        "env": {
          "POSTGRES_URL": "${POSTGRES_URL}"
        }
      },
      "docker": {
        "command": "npx",
        "args": ["-y", "mcp-server-docker"],
        "env": {}
      },
      "playwright": {
        "command": "npx",
        "args": ["-y", "@playwright/mcp"],
        "env": {}
      },
      "figma": {
        "command": "npx",
        "args": ["-y", "figma-mcp"],
        "env": {
          "FIGMA_TOKEN": "${FIGMA_TOKEN}"
        }
      },
      "prometheus": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-prometheus"],
        "env": {
          "PROMETHEUS_URL": "${PROMETHEUS_URL}"
        }
      },
      "sot": {
        "command": "python3",
        "args": ["-m", "anif_platform.sot.mcp_server"],
        "env": {
          "SOT_BACKEND": "${SOT_BACKEND}",
          "NAUTOBOT_URL": "${NAUTOBOT_URL}",
          "NAUTOBOT_TOKEN": "${NAUTOBOT_TOKEN}",
          "NETBOX_URL": "${NETBOX_URL}",
          "NETBOX_TOKEN": "${NETBOX_TOKEN}",
          "INFRAHUB_URL": "${INFRAHUB_URL}",
          "INFRAHUB_TOKEN": "${INFRAHUB_TOKEN}"
        }
      }
    },
    "hooks": {
      "PostToolUse": [
        {
          "matcher": "Edit|Write|MultiEdit",
          "hooks": [
            {
              "type": "command",
              "command": "bash -c 'cd /home/dan/Desktop/github/auto_networking && files=$(git diff --name-only 2>/dev/null | grep \"\\.py$\" | head -20 | tr \"\\n\" \" \"); if [ -n \"$files\" ]; then .venv/bin/ruff check --fix $files 2>&1 | head -40; .venv/bin/black $files 2>&1 | head -20; .venv/bin/mypy $files 2>&1 | head -40; fi'"
            }
          ]
        },
        {
          "matcher": "Edit|Write|MultiEdit",
          "hooks": [
            {
              "type": "command",
              "command": "bash -c 'cd /home/dan/Desktop/github/auto_networking && files=$(git diff --name-only 2>/dev/null | grep -E \"\\.(yml|yaml|json)$\" | grep -v \".github\" | head -10 | tr \"\\n\" \" \"); if [ -n \"$files\" ]; then echo \"Intent/schema files changed: $files — run ibn-agent to validate\"; fi'"
            }
          ]
        }
      ],
      "Stop": [
        {
          "hooks": [
            {
              "type": "command",
              "command": "bash -c 'cd /home/dan/Desktop/github/auto_networking && echo \"# Claude Resume Context\\n\\nSession stopped: $(date)\\n\\n## Last task in progress\\n\\n(Fill in manually or check git log)\\n\\n## Active ralph-loop prompt\\n\\n(Copy your active /ralph-loop prompt here before closing)\\n\" > .claude/resume.md'"
            }
          ]
        }
      ]
    }
  }
  ```

- [ ] **Commit**
  ```bash
  git add .claude/settings.json
  git commit -m "chore: add .claude/settings.json with MCP servers and hooks"
  ```

---

## Task 6: Install Plugins

**Files:** Modifies `~/.claude/settings.json` (user-level, not project-level)

These plugins are installed at user level and available in all sessions.

- [ ] **Install plugins via Claude Code plugin manager**

  Run each of these in the Claude Code terminal (or via `! <command>` in the prompt):
  ```bash
  claude plugin install feature-dev
  claude plugin install security-guidance
  claude plugin install commit-commands
  claude plugin install code-review
  claude plugin install code-simplifier
  claude plugin install pr-review-toolkit
  claude plugin install hookify
  claude plugin install skill-creator
  claude plugin install ralph-loop
  claude plugin install frontend-design
  claude plugin install agent-sdk-dev
  ```

- [ ] **Verify plugins listed**
  ```bash
  claude plugin list
  # Expected: superpowers, feature-dev, security-guidance, commit-commands,
  #           code-review, code-simplifier, pr-review-toolkit, hookify,
  #           skill-creator, ralph-loop, frontend-design, agent-sdk-dev
  ```

- [ ] **Commit**
  ```bash
  git commit -m "chore: document plugin installation (plugins are user-level)" --allow-empty
  ```

---

## Task 7: Docker Compose Stack

**Files:**
- Create: `docker/docker-compose.yml`
- Create: `docker/Dockerfile`

- [ ] **Write docker-compose.yml**

  Create `/home/dan/Desktop/github/auto_networking/docker/docker-compose.yml`:
  ```yaml
  version: "3.9"

  services:
    postgres:
      image: postgres:15-alpine
      environment:
        POSTGRES_USER: anif
        POSTGRES_PASSWORD: anif_dev
        POSTGRES_DB: anif
      ports:
        - "5432:5432"
      volumes:
        - postgres_data:/var/lib/postgresql/data
      healthcheck:
        test: ["CMD-SHELL", "pg_isready -U anif"]
        interval: 5s
        timeout: 5s
        retries: 5

    redis:
      image: redis:7-alpine
      ports:
        - "6379:6379"
      healthcheck:
        test: ["CMD", "redis-cli", "ping"]
        interval: 5s
        timeout: 3s
        retries: 5

    prometheus:
      image: prom/prometheus:latest
      ports:
        - "9090:9090"
      volumes:
        - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      command:
        - "--config.file=/etc/prometheus/prometheus.yml"
        - "--storage.tsdb.retention.time=7d"

    grafana:
      image: grafana/grafana:latest
      ports:
        - "3001:3000"
      environment:
        GF_SECURITY_ADMIN_PASSWORD: anif_dev
        GF_USERS_ALLOW_SIGN_UP: "false"
      volumes:
        - grafana_data:/var/lib/grafana
      depends_on:
        - prometheus

    platform:
      build:
        context: ..
        dockerfile: docker/Dockerfile
      ports:
        - "8000:8000"
      environment:
        POSTGRES_URL: postgresql://anif:anif_dev@postgres:5432/anif
        REDIS_URL: redis://redis:6379
        LOG_LEVEL: INFO
        ENVIRONMENT: development
      depends_on:
        postgres:
          condition: service_healthy
        redis:
          condition: service_healthy

  volumes:
    postgres_data:
    grafana_data:
  ```

- [ ] **Write prometheus.yml**

  Create `/home/dan/Desktop/github/auto_networking/docker/prometheus.yml`:
  ```yaml
  global:
    scrape_interval: 15s
    evaluation_interval: 15s

  scrape_configs:
    - job_name: "anif-platform"
      static_configs:
        - targets: ["platform:8000"]
      metrics_path: "/metrics"
  ```

- [ ] **Write Dockerfile**

  Create `/home/dan/Desktop/github/auto_networking/docker/Dockerfile`:
  ```dockerfile
  FROM python:3.13-slim AS base

  WORKDIR /app

  RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      && rm -rf /var/lib/apt/lists/*

  COPY pyproject.toml .
  RUN pip install --no-cache-dir uv && \
      uv pip install --system -e "."

  FROM base AS dev
  RUN uv pip install --system -e ".[dev]"
  COPY . .
  CMD ["uvicorn", "anif_platform.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  FROM base AS production
  COPY src/ src/
  CMD ["uvicorn", "anif_platform.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
  ```

- [ ] **Commit**
  ```bash
  git add docker/
  git commit -m "chore: add Docker Compose stack (postgres, redis, prometheus, grafana, platform)"
  ```

---

## Task 8: Environment Variables Template

**Files:**
- Create: `.env.example`

- [ ] **Write .env.example**

  Create `/home/dan/Desktop/github/auto_networking/.env.example`:
  ```bash
  # ── Database ──────────────────────────────────────────────────────────────────
  POSTGRES_URL=postgresql://anif:anif_dev@localhost:5432/anif
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif

  # ── Cache / Queue ─────────────────────────────────────────────────────────────
  REDIS_URL=redis://localhost:6379

  # ── Source of Truth ───────────────────────────────────────────────────────────
  # Select backend: nautobot | netbox | infrahub
  SOT_BACKEND=nautobot

  NAUTOBOT_URL=http://localhost:8080
  NAUTOBOT_TOKEN=your-nautobot-token-here

  NETBOX_URL=http://localhost:8000
  NETBOX_TOKEN=your-netbox-token-here

  INFRAHUB_URL=http://localhost:8000
  INFRAHUB_TOKEN=your-infrahub-token-here

  # ── Observability ─────────────────────────────────────────────────────────────
  PROMETHEUS_URL=http://localhost:9090

  # ── Frontend / Design ─────────────────────────────────────────────────────────
  FIGMA_TOKEN=your-figma-token-here

  # ── Platform ──────────────────────────────────────────────────────────────────
  LOG_LEVEL=INFO
  ENVIRONMENT=development

  # ── ANIF Companion Repo ───────────────────────────────────────────────────────
  ANIF_SPEC_REPO_PATH=/home/dan/Desktop/github/Autonomous-Networking-Infrastructure-Framework-ANIF
  ```

- [ ] **Commit**
  ```bash
  git add .env.example
  git commit -m "chore: add .env.example with all required environment variables"
  ```

---

## Task 9: GitHub Actions — ci.yml

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Write ci.yml**

  Create `/home/dan/Desktop/github/auto_networking/.github/workflows/ci.yml`:
  ```yaml
  name: CI

  on:
    push:
      branches: [main, "feature/**"]
    pull_request:
      branches: [main]

  jobs:
    lint:
      name: Lint
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: "3.13"
            cache: "pip"
        - run: pip install uv && uv pip install --system ruff black
        - run: ruff check src/ tests/
        - run: black --check src/ tests/

    type-check:
      name: Type Check
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: "3.13"
            cache: "pip"
        - run: pip install uv && uv pip install --system -e ".[dev]"
        - run: mypy src/ --strict

    unit-tests:
      name: Unit Tests
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: "3.13"
            cache: "pip"
        - run: pip install uv && uv pip install --system -e ".[dev]"
        - run: pytest tests/unit/ -v --cov=src --cov-report=xml
        - uses: codecov/codecov-action@v4
          with:
            files: ./coverage.xml

    integration-tests:
      name: Integration Tests
      runs-on: ubuntu-latest
      services:
        postgres:
          image: postgres:15-alpine
          env:
            POSTGRES_USER: anif
            POSTGRES_PASSWORD: anif_dev
            POSTGRES_DB: anif
          options: >-
            --health-cmd pg_isready
            --health-interval 5s
            --health-timeout 5s
            --health-retries 5
          ports:
            - 5432:5432
        redis:
          image: redis:7-alpine
          options: >-
            --health-cmd "redis-cli ping"
            --health-interval 5s
            --health-timeout 3s
            --health-retries 5
          ports:
            - 6379:6379
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: "3.13"
            cache: "pip"
        - run: pip install uv && uv pip install --system -e ".[dev]"
        - run: pytest tests/integration/ -v
          env:
            POSTGRES_URL: postgresql://anif:anif_dev@localhost:5432/anif
            REDIS_URL: redis://localhost:6379

    security-scan:
      name: Security Scan
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: "3.13"
            cache: "pip"
        - run: pip install uv && uv pip install --system bandit pip-audit
        - run: bandit -r src/ -ll
        - run: pip-audit

    docker-build:
      name: Docker Build
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - run: docker build -f docker/Dockerfile -t anif-platform:ci .
  ```

- [ ] **Commit**
  ```bash
  git add .github/workflows/ci.yml
  git commit -m "ci: add main CI workflow (lint, type-check, unit+integration tests, security, docker)"
  ```

---

## Task 10: GitHub Actions — accessibility.yml

**Files:**
- Create: `.github/workflows/accessibility.yml`

- [ ] **Write accessibility.yml**

  Create `/home/dan/Desktop/github/auto_networking/.github/workflows/accessibility.yml`:
  ```yaml
  name: Accessibility Audit

  on:
    push:
      paths:
        - "src/anif_ui/**"
    pull_request:
      paths:
        - "src/anif_ui/**"

  jobs:
    wcag-audit:
      name: WCAG 2.1 AA Audit
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with:
            node-version: "20"
            cache: "npm"
            cache-dependency-path: src/anif_ui/package-lock.json
        - name: Install dependencies
          working-directory: src/anif_ui
          run: npm ci
        - name: Build UI
          working-directory: src/anif_ui
          run: npm run build
        - name: Install Playwright + axe
          working-directory: src/anif_ui
          run: npx playwright install --with-deps chromium
        - name: Run WCAG 2.1 AA audit
          working-directory: src/anif_ui
          run: npx playwright test --project=chromium tests/accessibility/
          env:
            CI: true
  ```

- [ ] **Commit**
  ```bash
  git add .github/workflows/accessibility.yml
  git commit -m "ci: add WCAG 2.1 AA accessibility audit workflow"
  ```

---

## Task 11: GitHub Actions — intent-validate.yml

**Files:**
- Create: `.github/workflows/intent-validate.yml`

- [ ] **Write intent-validate.yml**

  Create `/home/dan/Desktop/github/auto_networking/.github/workflows/intent-validate.yml`:
  ```yaml
  name: Intent Validation

  on:
    push:
      paths:
        - "schemas/**"
        - "simulation/topologies/**"
        - "src/anif_platform/intent/**"
        - "src/anif_platform/schemas/**"
    pull_request:
      paths:
        - "schemas/**"
        - "simulation/topologies/**"

  jobs:
    schema-lint:
      name: Intent Schema Validation
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: "3.13"
            cache: "pip"
        - run: pip install uv && uv pip install --system pydantic pyyaml jsonschema
        - name: Validate all intent YAML files against schema
          run: |
            python3 - << 'EOF'
            import yaml
            import sys
            from pathlib import Path

            schema_path = Path("schemas/intent_schema.yml")
            if not schema_path.exists():
                print("No intent_schema.yml found — skipping")
                sys.exit(0)

            schema = yaml.safe_load(schema_path.read_text())
            required_fields = {"service", "environment", "objectives", "constraints", "policies", "priority"}

            errors = []
            for intent_file in Path("simulation/topologies").rglob("*.yml"):
                data = yaml.safe_load(intent_file.read_text())
                if not isinstance(data, dict):
                    continue
                if "intent" in data:
                    intent = data["intent"]
                    missing = required_fields - set(intent.keys())
                    if missing:
                        errors.append(f"{intent_file}: missing fields: {missing}")

            if errors:
                for e in errors:
                    print(f"ERROR: {e}")
                sys.exit(1)
            print(f"All intent files valid")
            EOF

    batfish-check:
      name: Batfish Static Analysis
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: Check for Batfish snapshots
          run: |
            if [ -d "simulation/batfish" ] && [ "$(ls -A simulation/batfish)" ]; then
              echo "Batfish snapshots found — run pybatfish analysis"
              pip install pybatfish
              python3 - << 'EOF'
            from pathlib import Path
            import sys
            snapshots = list(Path("simulation/batfish").iterdir())
            print(f"Found {len(snapshots)} Batfish snapshots")
            # Full analysis added when first snapshot is committed
            EOF
            else
              echo "No Batfish snapshots yet — skipping"
            fi
  ```

- [ ] **Commit**
  ```bash
  git add .github/workflows/intent-validate.yml
  git commit -m "ci: add intent schema validation and Batfish static analysis workflow"
  ```

---

## Task 12: GitHub Actions — compliance.yml

**Files:**
- Create: `.github/workflows/compliance.yml`

- [ ] **Write compliance.yml**

  Create `/home/dan/Desktop/github/auto_networking/.github/workflows/compliance.yml`:
  ```yaml
  name: Compliance Checks

  on:
    pull_request:
      paths:
        - "src/anif_platform/auth/**"
        - "src/anif_platform/schemas/**"
        - "src/anif_platform/audit/**"
        - "src/anif_ui/**"

  jobs:
    dependency-audit:
      name: Dependency CVE Audit
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: "3.13"
        - run: pip install safety pip-audit
        - run: pip-audit --requirement <(pip freeze)

    iso27001-check:
      name: ISO 27001 Audit Trail Check
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: Verify audit trail fields on data models
          run: |
            python3 - << 'EOF'
            import ast
            import sys
            from pathlib import Path

            required_audit_fields = {"created_at", "updated_at"}
            errors = []

            for model_file in Path("src/anif_platform/schemas").rglob("*.py"):
                source = model_file.read_text()
                if "BaseModel" in source or "DeclarativeBase" in source:
                    missing = [f for f in required_audit_fields if f not in source]
                    if missing:
                        errors.append(f"{model_file}: missing audit fields: {missing}")

            if errors:
                for e in errors:
                    print(f"WARNING: {e}")
                # Non-blocking during scaffold phase — becomes blocking at B1 complete
            else:
                print("Audit field check passed")
            EOF

    hipaa-check:
      name: HIPAA Compliance Check
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: Check for bare PHI handling
          run: |
            # Flag any string containing 'patient' or 'health_record' without encryption decorator
            if grep -rn "patient\|health_record\|phi" src/ --include="*.py" | grep -v "encrypt\|#"; then
              echo "WARNING: Potential unencrypted PHI references found — review required"
            else
              echo "HIPAA check passed"
            fi
  ```

- [ ] **Commit**
  ```bash
  git add .github/workflows/compliance.yml
  git commit -m "ci: add compliance workflow (CVE audit, ISO 27001 audit trail, HIPAA check)"
  ```

---

## Task 13: Copy ANIF Schemas

**Files:**
- Copy from: `/home/dan/Desktop/github/Autonomous-Networking-Infrastructure-Framework-ANIF/schemas/`
- Copy to: `schemas/`

- [ ] **Copy all ANIF schema files**
  ```bash
  cd /home/dan/Desktop/github/auto_networking
  cp /home/dan/Desktop/github/Autonomous-Networking-Infrastructure-Framework-ANIF/schemas/*.yml schemas/
  ls schemas/
  # Expected: action_schema.yml  audit_record_schema.yml  example_intent.yml
  #           intent_schema.yml  policy_schema.yml  risk_score_schema.yml
  ```

- [ ] **Add a schemas/README.md noting the source**

  Create `schemas/README.md`:
  ```markdown
  # ANIF Schemas

  These schema files are copied from the ANIF framework specification repository.

  **Source:** `Autonomous-Networking-Infrastructure-Framework-ANIF/schemas/`

  Do not modify these files directly. Raise a change proposal in the ANIF repo first,
  then update here once the spec change is approved.

  | File | ANIF Document |
  |---|---|
  | `intent_schema.yml` | ANIF-300, ANIF-301 |
  | `policy_schema.yml` | ANIF-302 |
  | `action_schema.yml` | ANIF-306 |
  | `risk_score_schema.yml` | ANIF-304 |
  | `audit_record_schema.yml` | ANIF-107 |
  | `example_intent.yml` | ANIF-601 |
  ```

- [ ] **Commit**
  ```bash
  git add schemas/
  git commit -m "chore: copy ANIF schemas from framework spec repo"
  ```

---

## Task 14: Alembic Setup

**Files:**
- Create: `migrations/alembic.ini`
- Create: `migrations/env.py`
- Create: `migrations/script.py.mako`

- [ ] **Initialise Alembic**
  ```bash
  cd /home/dan/Desktop/github/auto_networking
  .venv/bin/alembic init migrations
  ```

- [ ] **Update migrations/env.py to use DATABASE_URL from environment**

  Edit `migrations/env.py` — replace the `run_migrations_offline` and `run_migrations_online` blocks with:
  ```python
  import os
  from logging.config import fileConfig

  from alembic import context
  from sqlalchemy import engine_from_config, pool

  config = context.config

  if config.config_file_name is not None:
      fileConfig(config.config_file_name)

  # Import all models so Alembic can detect them
  # from anif_platform.schemas import models  # uncomment when B1 starts
  target_metadata = None  # replace with Base.metadata when B1 starts


  def get_database_url() -> str:
      url = os.environ.get("DATABASE_URL")
      if not url:
          raise RuntimeError("DATABASE_URL environment variable is not set")
      return url


  def run_migrations_offline() -> None:
      url = get_database_url()
      context.configure(
          url=url,
          target_metadata=target_metadata,
          literal_binds=True,
          dialect_opts={"paramstyle": "named"},
      )
      with context.begin_transaction():
          context.run_migrations()


  def run_migrations_online() -> None:
      configuration = config.get_section(config.config_ini_section) or {}
      configuration["sqlalchemy.url"] = get_database_url()
      connectable = engine_from_config(
          configuration,
          prefix="sqlalchemy.",
          poolclass=pool.NullPool,
      )
      with connectable.connect() as connection:
          context.configure(connection=connection, target_metadata=target_metadata)
          with context.begin_transaction():
              context.run_migrations()


  if context.is_offline_mode():
      run_migrations_offline()
  else:
      run_migrations_online()
  ```

- [ ] **Verify Alembic config**
  ```bash
  cd /home/dan/Desktop/github/auto_networking
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif .venv/bin/alembic current
  # Expected: error about DB not running OR "no current revision" — both are fine at scaffold stage
  ```

- [ ] **Commit**
  ```bash
  git add migrations/
  git commit -m "chore: initialise Alembic with DATABASE_URL env var support"
  ```

---

## Task 15: React Frontend Scaffold

**Files:** All files under `src/anif_ui/`

- [ ] **Initialise Vite + React + TypeScript project**
  ```bash
  cd /home/dan/Desktop/github/auto_networking/src
  npm create vite@latest anif_ui -- --template react-ts
  cd anif_ui
  npm install
  ```

- [ ] **Install Tailwind CSS**
  ```bash
  cd /home/dan/Desktop/github/auto_networking/src/anif_ui
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p
  ```

- [ ] **Install React Router and accessibility tools**
  ```bash
  npm install react-router-dom @types/react-router-dom
  npm install -D @axe-core/playwright @playwright/test
  npx playwright install chromium
  ```

- [ ] **Update tailwind.config.ts**

  Edit `src/anif_ui/tailwind.config.ts`:
  ```typescript
  import type { Config } from "tailwindcss";

  export default {
    content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
    theme: {
      extend: {
        colors: {
          brand: {
            50: "#eff6ff",
            500: "#3b82f6",
            900: "#1e3a8a",
          },
        },
      },
    },
    plugins: [],
  } satisfies Config;
  ```

- [ ] **Update src/anif_ui/src/main.tsx**

  Replace contents of `src/anif_ui/src/main.tsx`:
  ```tsx
  import React from "react";
  import ReactDOM from "react-dom/client";
  import { BrowserRouter } from "react-router-dom";
  import App from "./App";
  import "./index.css";

  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </React.StrictMode>
  );
  ```

- [ ] **Update src/anif_ui/src/App.tsx**

  Replace contents of `src/anif_ui/src/App.tsx`:
  ```tsx
  import { Routes, Route } from "react-router-dom";

  function PlaceholderPage({ title }: { title: string }) {
    return (
      <main className="p-8">
        <h1 className="text-2xl font-bold text-brand-900">{title}</h1>
        <p className="mt-2 text-gray-600">Implementation pending — Phase {title.split(" ")[0]}</p>
      </main>
    );
  }

  export default function App() {
    return (
      <Routes>
        <Route path="/" element={<PlaceholderPage title="F2 Intent Dashboard" />} />
        <Route path="/approvals" element={<PlaceholderPage title="F3 Approval Queue" />} />
        <Route path="/audit" element={<PlaceholderPage title="F4 Audit Trail" />} />
        <Route path="/topology" element={<PlaceholderPage title="F5 Topology View" />} />
        <Route path="/governance" element={<PlaceholderPage title="F6 Risk & Governance" />} />
      </Routes>
    );
  }
  ```

- [ ] **Create accessibility test placeholder**
  ```bash
  mkdir -p src/anif_ui/tests/accessibility
  cat > src/anif_ui/tests/accessibility/wcag.spec.ts << 'EOF'
  import { test, expect } from "@playwright/test";
  import AxeBuilder from "@axe-core/playwright";

  test.describe("WCAG 2.1 AA audit", () => {
    test("home page has no accessibility violations", async ({ page }) => {
      await page.goto("/");
      const results = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa"])
        .analyze();
      expect(results.violations).toEqual([]);
    });
  });
  EOF
  ```

- [ ] **Verify build**
  ```bash
  cd /home/dan/Desktop/github/auto_networking/src/anif_ui
  npm run build
  # Expected: dist/ directory created, no build errors
  ```

- [ ] **Commit**
  ```bash
  cd /home/dan/Desktop/github/auto_networking
  git add src/anif_ui/
  git commit -m "chore: scaffold React + TypeScript frontend (Vite, Tailwind, React Router, Playwright)"
  ```

---

## Task 16: Architecture Documentation + Draw.io Stubs

**Files:**
- Create: `docs/architecture/ARCHITECTURE.md`
- Create: `docs/architecture/diagrams/*.drawio` (7 files)

- [ ] **Write ARCHITECTURE.md**

  Create `docs/architecture/ARCHITECTURE.md`:
  ```markdown
  # ANIF Platform — Living Architecture Document

  > This document is maintained by the `architecture-agent`. Do not edit manually
  > without also updating the relevant `.drawio` diagram files.

  **Last updated by:** workspace scaffold
  **Platform version:** 0.1.0 (scaffold only — no platform modules implemented yet)

  ---

  ## System Overview

  The ANIF platform is a Python/FastAPI application that implements the Autonomous
  Networking & Infrastructure Framework specification. It accepts network intents,
  evaluates them against policies, scores their risk, makes bounded decisions,
  executes approved actions, and records everything to an immutable audit trail.

  ---

  ## Backend Modules

  | Module | Status | ANIF Spec |
  |---|---|---|
  | `schemas` | Not started | ANIF-300, ANIF-600 |
  | `audit` | Not started | ANIF-107 |
  | `policy` | Not started | ANIF-302, ANIF-303 |
  | `risk` | Not started | ANIF-304 |
  | `intent` | Not started | ANIF-300, ANIF-301 |
  | `governance` | Not started | ANIF-301, ANIF-406 |
  | `pipeline` | Not started | ANIF-305–308 |
  | `agents` | Not started | ANIF-803, ANIF-805 |
  | `auth` | Not started | ANIF-843 |
  | `ethics` | Not started | ANIF-720–725 |
  | `monitoring` | Not started | ANIF-401, ANIF-846 |
  | `human_loop` | Not started | ANIF-402, ANIF-404 |
  | `sot` | Scaffold only | ANIF-307 |

  ---

  ## Frontend Pages

  | Page | Status | Backend Dependency |
  |---|---|---|
  | Intent Dashboard | Not started | B2 |
  | Approval Queue | Not started | B4 |
  | Audit Trail Viewer | Not started | B2 |
  | Topology View | Not started | B5 |
  | Risk & Governance | Not started | B8 |

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
  | Nautobot / NetBox / InfraHub | Source of Truth | REST / GraphQL (read + metadata write-back) |
  | PostgreSQL 15 | Audit trail, risk register | SQLAlchemy async |
  | Redis 7 | Intent queue, message bus | redis-py async |
  | Prometheus | Metrics collection | /metrics endpoint |
  | Containerlab | Network simulation | CLI + topology YAML |
  | Batfish | Static config analysis | pybatfish |
  ```

- [ ] **Create draw.io stub files**

  Create `docs/architecture/diagrams/system-context.drawio`:
  ```xml
  <mxfile host="app.diagrams.net" version="24.0.0">
    <diagram id="system-context" name="System Context">
      <mxGraphModel><root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>
        <mxCell id="2" value="ANIF Platform" style="rounded=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="300" y="200" width="200" height="100" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="Nautobot / NetBox / InfraHub&#xa;(Source of Truth)" style="rounded=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="600" y="100" width="180" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="4" value="Network Operator" style="shape=mxgraph.flowchart.actor;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="50" y="210" width="60" height="80" as="geometry"/>
        </mxCell>
        <mxCell id="5" value="PostgreSQL" style="shape=mxgraph.flowchart.database;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="600" y="220" width="80" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="6" value="Redis" style="shape=mxgraph.flowchart.database;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="600" y="320" width="80" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="7" value="intent submission" style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="4" target="2" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="8" value="read inventory&#xa;write-back tags" style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="2" target="3" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="9" value="audit + state" style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="2" target="5" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="10" value="intent queue" style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="2" target="6" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root></mxGraphModel>
    </diagram>
  </mxfile>
  ```

  Create the remaining 6 stub diagrams:
  ```bash
  for name in component sequence-pipeline agent-tiers data-flow sot-integration deployment; do
  cat > docs/architecture/diagrams/${name}.drawio << EOF
  <mxfile host="app.diagrams.net" version="24.0.0">
    <diagram id="${name}" name="${name}">
      <mxGraphModel><root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>
        <mxCell id="2" value="${name} — to be populated by architecture-agent after phase completion" style="text;html=1;align=center;verticalAlign=middle;resizable=0;points=[];autosize=1;" vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="500" height="60" as="geometry"/>
        </mxCell>
      </root></mxGraphModel>
    </diagram>
  </mxfile>
  EOF
  done
  ```

- [ ] **Commit**
  ```bash
  git add docs/architecture/
  git commit -m "chore: add living ARCHITECTURE.md and 7 draw.io diagram stubs"
  ```

---

## Task 17: Test Structure + conftest.py

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/unit/.gitkeep`
- Create: `tests/integration/.gitkeep`

- [ ] **Write conftest.py**

  Create `tests/conftest.py`:
  ```python
  """Shared pytest fixtures for the ANIF platform test suite."""

  import os
  from collections.abc import AsyncGenerator

  import pytest
  import pytest_asyncio
  from httpx import AsyncClient


  # ── Environment ───────────────────────────────────────────────────────────────

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


  # ── Placeholder fixtures (uncomment when modules exist) ───────────────────────

  # @pytest_asyncio.fixture
  # async def db_session() -> AsyncGenerator:
  #     """Provide a transactional database session that rolls back after each test."""
  #     from anif_platform.database import async_session_factory
  #     async with async_session_factory() as session:
  #         async with session.begin():
  #             yield session
  #             await session.rollback()


  # @pytest_asyncio.fixture
  # async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
  #     """Provide an async test client wired to the FastAPI app."""
  #     from anif_platform.main import app
  #     async with AsyncClient(app=app, base_url="http://test") as c:
  #         yield c
  ```

- [ ] **Create placeholder test to verify pytest works**

  Create `tests/unit/test_scaffold.py`:
  ```python
  """Scaffold verification test — delete when first real test is written."""


  def test_platform_version() -> None:
      """Verify the platform package imports correctly."""
      from anif_platform import __version__

      assert __version__ == "0.1.0"
  ```

- [ ] **Run tests**
  ```bash
  cd /home/dan/Desktop/github/auto_networking
  .venv/bin/pytest tests/unit/test_scaffold.py -v
  # Expected: PASSED test_scaffold.py::test_platform_version
  ```

- [ ] **Commit**
  ```bash
  git add tests/
  git commit -m "test: add conftest.py fixtures and scaffold verification test"
  ```

---

## Task 18: SoT Adapter Protocol Interface

**Files:**
- Create: `src/anif_platform/sot/protocol.py`
- Create: `src/anif_platform/sot/nautobot.py`
- Create: `src/anif_platform/sot/netbox.py`
- Create: `src/anif_platform/sot/infrahub.py`

- [ ] **Write protocol.py**

  Create `src/anif_platform/sot/protocol.py`:
  ```python
  """Source-of-Truth adapter protocol — defines the interface all SoT backends must implement."""

  from dataclasses import dataclass
  from typing import Protocol, runtime_checkable


  @dataclass
  class Device:
      name: str
      site: str
      role: str
      platform: str
      primary_ip: str | None
      tags: list[str]


  @dataclass
  class Interface:
      name: str
      device: str
      ip_address: str | None
      tags: list[str]


  @dataclass
  class Prefix:
      prefix: str
      site: str | None
      vrf: str | None


  @dataclass
  class Topology:
      site: str
      devices: list[Device]
      connections: list[tuple[str, str]]  # (device_a, device_b)


  @runtime_checkable
  class SoTAdapter(Protocol):
      """Protocol that all Source-of-Truth adapter implementations must satisfy."""

      # ── Read operations ───────────────────────────────────────────────────────

      def get_device(self, name: str) -> Device:
          """Fetch a single device record by name."""
          ...

      def list_devices(self, site: str | None = None) -> list[Device]:
          """List devices, optionally filtered by site."""
          ...

      def get_topology(self, site: str) -> Topology:
          """Fetch full site topology including devices and connections."""
          ...

      def get_prefix(self, prefix: str) -> Prefix:
          """Fetch an IP prefix record."""
          ...

      # ── Write-back operations (metadata only) ────────────────────────────────

      def tag_device(self, name: str, tag: str) -> None:
          """Add an intent tag to a device (e.g. 'intent:qos-prod-v2')."""
          ...

      def tag_interface(self, device: str, interface: str, tag: str) -> None:
          """Add an intent tag to a device interface."""
          ...

      def tag_connection(self, device_a: str, device_b: str, tag: str) -> None:
          """Add an intent tag to a connection between two devices."""
          ...

      def set_custom_field(self, object_type: str, name: str, field: str, value: str) -> None:
          """Set a custom field on a SoT object (e.g. intent_status, last_intent_id)."""
          ...
  ```

- [ ] **Write stub adapter implementations**

  Create `src/anif_platform/sot/nautobot.py`:
  ```python
  """Nautobot 3.x Source-of-Truth adapter."""

  from anif_platform.exceptions import SoTAdapterError
  from anif_platform.sot.protocol import Device, Interface, Prefix, Topology


  class NautobotAdapter:
      """Reads device/topology data from Nautobot via REST + GraphQL.

      Write-back: tags, comments, and custom fields on devices/interfaces/connections.
      Does NOT modify device configurations, IP assignments, or topology records.
      """

      def __init__(self, url: str, token: str) -> None:
          self._url = url.rstrip("/")
          self._token = token

      def get_device(self, name: str) -> Device:
          raise NotImplementedError("NautobotAdapter.get_device — implement in B2 when SoT module is built")

      def list_devices(self, site: str | None = None) -> list[Device]:
          raise NotImplementedError("NautobotAdapter.list_devices — implement in B2")

      def get_topology(self, site: str) -> Topology:
          raise NotImplementedError("NautobotAdapter.get_topology — implement in B2")

      def get_prefix(self, prefix: str) -> Prefix:
          raise NotImplementedError("NautobotAdapter.get_prefix — implement in B2")

      def tag_device(self, name: str, tag: str) -> None:
          raise NotImplementedError("NautobotAdapter.tag_device — implement in B5")

      def tag_interface(self, device: str, interface: str, tag: str) -> None:
          raise NotImplementedError("NautobotAdapter.tag_interface — implement in B5")

      def tag_connection(self, device_a: str, device_b: str, tag: str) -> None:
          raise NotImplementedError("NautobotAdapter.tag_connection — implement in B5")

      def set_custom_field(self, object_type: str, name: str, field: str, value: str) -> None:
          raise NotImplementedError("NautobotAdapter.set_custom_field — implement in B5")
  ```

  Create `src/anif_platform/sot/netbox.py`:
  ```python
  """NetBox 3.x Source-of-Truth adapter."""

  from anif_platform.sot.protocol import Device, Prefix, Topology


  class NetBoxAdapter:
      """Reads device/topology data from NetBox via REST API."""

      def __init__(self, url: str, token: str) -> None:
          self._url = url.rstrip("/")
          self._token = token

      def get_device(self, name: str) -> Device:
          raise NotImplementedError("NetBoxAdapter.get_device — implement in B2")

      def list_devices(self, site: str | None = None) -> list[Device]:
          raise NotImplementedError("NetBoxAdapter.list_devices — implement in B2")

      def get_topology(self, site: str) -> Topology:
          raise NotImplementedError("NetBoxAdapter.get_topology — implement in B2")

      def get_prefix(self, prefix: str) -> Prefix:
          raise NotImplementedError("NetBoxAdapter.get_prefix — implement in B2")

      def tag_device(self, name: str, tag: str) -> None:
          raise NotImplementedError("NetBoxAdapter.tag_device — implement in B5")

      def tag_interface(self, device: str, interface: str, tag: str) -> None:
          raise NotImplementedError("NetBoxAdapter.tag_interface — implement in B5")

      def tag_connection(self, device_a: str, device_b: str, tag: str) -> None:
          raise NotImplementedError("NetBoxAdapter.tag_connection — implement in B5")

      def set_custom_field(self, object_type: str, name: str, field: str, value: str) -> None:
          raise NotImplementedError("NetBoxAdapter.set_custom_field — implement in B5")
  ```

  Create `src/anif_platform/sot/infrahub.py`:
  ```python
  """InfraHub Source-of-Truth adapter."""

  from anif_platform.sot.protocol import Device, Prefix, Topology


  class InfraHubAdapter:
      """Reads device/topology data from InfraHub via GraphQL."""

      def __init__(self, url: str, token: str) -> None:
          self._url = url.rstrip("/")
          self._token = token

      def get_device(self, name: str) -> Device:
          raise NotImplementedError("InfraHubAdapter.get_device — implement in B2")

      def list_devices(self, site: str | None = None) -> list[Device]:
          raise NotImplementedError("InfraHubAdapter.list_devices — implement in B2")

      def get_topology(self, site: str) -> Topology:
          raise NotImplementedError("InfraHubAdapter.get_topology — implement in B2")

      def get_prefix(self, prefix: str) -> Prefix:
          raise NotImplementedError("InfraHubAdapter.get_prefix — implement in B2")

      def tag_device(self, name: str, tag: str) -> None:
          raise NotImplementedError("InfraHubAdapter.tag_device — implement in B5")

      def tag_interface(self, device: str, interface: str, tag: str) -> None:
          raise NotImplementedError("InfraHubAdapter.tag_interface — implement in B5")

      def tag_connection(self, device_a: str, device_b: str, tag: str) -> None:
          raise NotImplementedError("InfraHubAdapter.tag_connection — implement in B5")

      def set_custom_field(self, object_type: str, name: str, field: str, value: str) -> None:
          raise NotImplementedError("InfraHubAdapter.set_custom_field — implement in B5")
  ```

- [ ] **Update sot/__init__.py to expose factory**

  Edit `src/anif_platform/sot/__init__.py`:
  ```python
  """Source-of-Truth adapter — Nautobot, NetBox, or InfraHub."""

  import os

  from anif_platform.exceptions import SoTAdapterError
  from anif_platform.sot.protocol import SoTAdapter


  def get_sot_adapter() -> SoTAdapter:
      """Return the configured SoT adapter based on SOT_BACKEND env var."""
      backend = os.environ.get("SOT_BACKEND", "nautobot").lower()

      if backend == "nautobot":
          from anif_platform.sot.nautobot import NautobotAdapter
          url = os.environ.get("NAUTOBOT_URL", "")
          token = os.environ.get("NAUTOBOT_TOKEN", "")
          if not url or not token:
              raise SoTAdapterError("NAUTOBOT_URL and NAUTOBOT_TOKEN must be set when SOT_BACKEND=nautobot")
          return NautobotAdapter(url=url, token=token)  # type: ignore[return-value]

      if backend == "netbox":
          from anif_platform.sot.netbox import NetBoxAdapter
          url = os.environ.get("NETBOX_URL", "")
          token = os.environ.get("NETBOX_TOKEN", "")
          if not url or not token:
              raise SoTAdapterError("NETBOX_URL and NETBOX_TOKEN must be set when SOT_BACKEND=netbox")
          return NetBoxAdapter(url=url, token=token)  # type: ignore[return-value]

      if backend == "infrahub":
          from anif_platform.sot.infrahub import InfraHubAdapter
          url = os.environ.get("INFRAHUB_URL", "")
          token = os.environ.get("INFRAHUB_TOKEN", "")
          if not url or not token:
              raise SoTAdapterError("INFRAHUB_URL and INFRAHUB_TOKEN must be set when SOT_BACKEND=infrahub")
          return InfraHubAdapter(url=url, token=token)  # type: ignore[return-value]

      raise SoTAdapterError(f"Unknown SOT_BACKEND: {backend!r} — must be nautobot | netbox | infrahub")
  ```

- [ ] **Write tests for adapter factory**

  Create `tests/unit/test_sot_factory.py`:
  ```python
  """Tests for the SoT adapter factory."""

  import pytest

  from anif_platform.exceptions import SoTAdapterError


  def test_factory_raises_on_unknown_backend(monkeypatch: pytest.MonkeyPatch) -> None:
      monkeypatch.setenv("SOT_BACKEND", "unknown")
      from anif_platform.sot import get_sot_adapter
      with pytest.raises(SoTAdapterError, match="Unknown SOT_BACKEND"):
          get_sot_adapter()


  def test_factory_raises_on_missing_nautobot_url(monkeypatch: pytest.MonkeyPatch) -> None:
      monkeypatch.setenv("SOT_BACKEND", "nautobot")
      monkeypatch.delenv("NAUTOBOT_URL", raising=False)
      monkeypatch.delenv("NAUTOBOT_TOKEN", raising=False)
      from anif_platform.sot import get_sot_adapter
      with pytest.raises(SoTAdapterError, match="NAUTOBOT_URL"):
          get_sot_adapter()


  def test_factory_returns_nautobot_adapter(monkeypatch: pytest.MonkeyPatch) -> None:
      monkeypatch.setenv("SOT_BACKEND", "nautobot")
      monkeypatch.setenv("NAUTOBOT_URL", "http://nautobot.test")
      monkeypatch.setenv("NAUTOBOT_TOKEN", "test-token")
      from anif_platform.sot import get_sot_adapter
      from anif_platform.sot.nautobot import NautobotAdapter
      adapter = get_sot_adapter()
      assert isinstance(adapter, NautobotAdapter)
  ```

- [ ] **Run tests**
  ```bash
  .venv/bin/pytest tests/unit/test_sot_factory.py -v
  # Expected: 3 PASSED
  ```

- [ ] **Commit**
  ```bash
  git add src/anif_platform/sot/ tests/unit/test_sot_factory.py
  git commit -m "feat: add SoT adapter protocol, stub implementations, and factory"
  ```

---

## Task 19: Simulation Stubs

**Files:**
- Create: `simulation/topologies/example-bgp.yml`
- Create: `simulation/batfish/README.md`

- [ ] **Write example containerlab topology**

  Create `simulation/topologies/example-bgp.yml`:
  ```yaml
  # Example containerlab topology for BGP intent testing
  # Reference: simulation/README.md
  # Run: sudo containerlab deploy -t simulation/topologies/example-bgp.yml

  name: anif-bgp-test

  topology:
    nodes:
      router-a:
        kind: linux
        image: frrouting/frr:latest
        binds:
          - simulation/topologies/config/router-a/frr.conf:/etc/frr/frr.conf

      router-b:
        kind: linux
        image: frrouting/frr:latest
        binds:
          - simulation/topologies/config/router-b/frr.conf:/etc/frr/frr.conf

    links:
      - endpoints: ["router-a:eth1", "router-b:eth1"]

  # Intent to test:
  # service: transit-routing
  # environment: test
  # objectives:
  #   convergence_seconds: 30
  # policies:
  #   - bgp_prefix_filter
  ```

- [ ] **Write Batfish README**

  Create `simulation/batfish/README.md`:
  ```markdown
  # Batfish Network Config Analysis

  This directory contains network configuration snapshots for static analysis with Batfish.

  ## What Batfish Does

  Batfish analyses network configurations without running devices. It validates:
  - BGP session correctness
  - ACL reachability
  - Route propagation
  - Intent compliance (does the config match the declared intent?)

  ## Adding a Snapshot

  Create a subdirectory with the snapshot name and add device configs:

  ```
  simulation/batfish/
  └── my-snapshot/
      ├── configs/
      │   ├── router-a.cfg
      │   └── router-b.cfg
      └── hosts/
          └── hosts.json
  ```

  ## Running Analysis

  ```bash
  pip install pybatfish
  python3 simulation/batfish/analyse.py my-snapshot
  ```

  Batfish analysis runs in the `intent-validate` CI workflow automatically.
  ```

- [ ] **Commit**
  ```bash
  git add simulation/
  git commit -m "chore: add containerlab topology stub and Batfish snapshot directory"
  ```

---

## Task 20: Rate Limit Recovery Template

**Files:**
- Create: `.claude/resume.md`

- [ ] **Write resume.md template**

  Create `.claude/resume.md`:
  ```markdown
  # Claude Resume Context

  > This file is written by the Stop hook when the session ends.
  > On restart, read this file and continue from where you left off.

  ## Session stopped at
  (populated by Stop hook)

  ## Active task
  (describe the task in progress when the session ended)

  ## Active ralph-loop prompt
  (paste the full /ralph-loop prompt here before closing so it can be resumed)

  ## Files changed in this session (not yet committed)
  (git status output — populated by Stop hook)

  ## Next step
  (what to do first when the session resumes)
  ```

- [ ] **Commit**
  ```bash
  git add .claude/resume.md
  git commit -m "chore: add rate limit recovery template (.claude/resume.md)"
  ```

---

## Task 21: Final Verification

- [ ] **Run full lint check**
  ```bash
  cd /home/dan/Desktop/github/auto_networking
  .venv/bin/ruff check src/ tests/
  # Expected: no errors (or only style warnings)
  ```

- [ ] **Run type check**
  ```bash
  .venv/bin/mypy src/ --ignore-missing-imports
  # Expected: no errors
  ```

- [ ] **Run all tests**
  ```bash
  .venv/bin/pytest tests/unit/ -v --no-cov
  # Expected: test_scaffold.py::test_platform_version PASSED
  #           test_sot_factory.py::test_factory_raises_on_unknown_backend PASSED
  #           test_sot_factory.py::test_factory_raises_on_missing_nautobot_url PASSED
  #           test_sot_factory.py::test_factory_returns_nautobot_adapter PASSED
  ```

- [ ] **Verify directory structure**
  ```bash
  find . -not -path "./.git/*" -not -path "./.venv/*" -not -path "./src/anif_ui/node_modules/*" -not -path "./src/anif_ui/dist/*" | sort
  # Expected: all files from the File Map at the top of this plan
  ```

- [ ] **Verify CLAUDE.md is readable by Claude**
  ```bash
  wc -l CLAUDE.md .claude/settings.json
  # Expected: CLAUDE.md > 200 lines, settings.json > 50 lines
  ```

- [ ] **Final commit**
  ```bash
  git add -A
  git status
  # Expected: clean working tree or only .env file (which should never be committed)
  git log --oneline | head -25
  # Expected: all task commits visible
  ```

---

## Post-Scaffold Checklist

After all 21 tasks complete, the workspace is ready for platform development. Verify:

- [ ] `CLAUDE.md` present and contains all 10 agent definitions
- [ ] `.claude/settings.json` present with MCP servers and hooks
- [ ] All 11 plugins installed (`claude plugin list`)
- [ ] `pyproject.toml` present, `uv pip install -e ".[dev]"` succeeds
- [ ] `docker/docker-compose.yml` present (run `docker compose up` when Docker is installed)
- [ ] All 4 GitHub Actions workflows present in `.github/workflows/`
- [ ] `migrations/` present with `env.py` and `alembic.ini`
- [ ] `schemas/` contains 6 ANIF schema files
- [ ] `src/anif_ui/` builds cleanly (`npm run build`)
- [ ] `docs/architecture/diagrams/` contains 7 `.drawio` files
- [ ] `tests/unit/` passes all tests
- [ ] `.claude/resume.md` template present

**Next:** Begin platform build phase B1 — Foundation & Data Models (Pydantic schemas + AuditWriter). Start a new brainstorming session for B1 features before writing any code.
