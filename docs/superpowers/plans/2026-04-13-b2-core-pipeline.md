# B2: Core Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Intent Engine, Policy Engine, and Orchestrator — the full pipeline skeleton from Git-sourced intent through to a response, with stubs for stages not yet built (risk, decision, governance, execute).

**Architecture:** Git is the source of truth for intent files. The platform detects new intents via configurable webhook and/or polling, assigns a UUID `intent_id`, stores metadata in the `intents` table, and runs them through validation → policy evaluation → (stubbed) risk → decision → governance → execute. All four built-in policies are loaded from YAML files in `policies/`; custom policies drop in by adding more YAML files. A simple API key protects all endpoints until B6 builds full X.509 auth.

**Tech Stack:** Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2 async, PyYAML, httpx (for Git fetching), asyncio background tasks, pytest-asyncio.

**Spec sources:**
- `ANIF-301` — intent authoring standard, validation rules VAL-001–VAL-007
- `ANIF-302` — policy engine, condition grammar, 8 operators, built-in policies
- `ANIF-303` — conflict detection and resolution, precedence hierarchy

**Working directory:** `/home/dan/Desktop/github/auto_networking/.worktrees/scaffold/`

**Design decisions recorded from planning:**
- Orchestrator: end-to-end skeleton with `{"status": "not_yet_implemented"}` stubs for risk/decision/governance/execute
- Policy engine: extensible from YAML files — drop in any policy file without code changes
- Intent flow: intent YAML committed to Git → platform detects → validates → registers with UUID
- Git detection: both webhook and polling, controlled by `GIT_WATCHER_MODE=webhook|polling|both`
- Auth: API key from `ANIF_API_KEY` env var, checked on all endpoints

---

## File Map

```
src/anif_platform/
├── auth/
│   ├── __init__.py           MODIFY — re-export get_api_key
│   └── middleware.py         CREATE — API key dependency
├── intent/
│   ├── __init__.py           MODIFY — re-export IntentValidator, IntentRegistry
│   ├── models.py             CREATE — SQLAlchemy IntentRow
│   ├── schemas.py            CREATE — ValidatedIntent, ValidationResult, GitIntentRef
│   ├── validator.py          CREATE — IntentValidator (VAL-001–VAL-007)
│   ├── registry.py           CREATE — IntentRegistry (DB read/write)
│   ├── git_watcher.py        CREATE — GitWatcher (polling + webhook detection)
│   └── router.py             CREATE — POST /validate-intent, GET /intent/{id}, POST /webhooks/git
├── policy/
│   ├── __init__.py           MODIFY — re-export PolicyEngine
│   ├── condition.py          CREATE — ConditionEvaluator (all 8 operators)
│   ├── loader.py             CREATE — PolicyLoader (YAML files from policies/ dir)
│   ├── engine.py             CREATE — PolicyEngine (evaluation algorithm)
│   ├── conflict.py           CREATE — ConflictDetector + ConflictResolver (ANIF-303)
│   └── router.py             CREATE — POST /evaluate-policy
├── pipeline/
│   ├── __init__.py           MODIFY
│   └── router.py             CREATE — POST /orchestrate (end-to-end with stubs)
└── main.py                   MODIFY — add routers + git watcher lifespan

policies/                     CREATE dir
├── zero_trust.yml            CREATE — built-in policy
├── no_public_ingress.yml     CREATE — built-in policy
├── pci_compliant.yml         CREATE — built-in policy
└── data_residency.yml        CREATE — built-in policy

migrations/versions/
└── 002_create_intents.py     CREATE — intents table

tests/unit/
├── test_intent_validator.py  CREATE
├── test_condition_evaluator.py CREATE
├── test_policy_engine.py     CREATE
└── test_conflict_resolver.py CREATE
tests/integration/
├── test_intent_endpoints.py  CREATE
└── test_policy_endpoints.py  CREATE
```

---

## Environment Variables (add to `.env.example`)

```bash
ANIF_API_KEY=changeme-dev-key          # Required — all endpoints check this
GIT_WATCHER_MODE=polling               # webhook | polling | both
GIT_WATCHER_POLL_INTERVAL=60           # seconds between polls (polling mode)
GIT_REPO_URL=https://github.com/org/intents
GIT_INTENTS_PATH=intents/              # path within repo where .yml intent files live
GIT_ACCESS_TOKEN=ghp_xxxxx             # personal access token for private repos
DATA_RESIDENCY_APPROVED_REGIONS=EU,US,APAC  # comma-separated approved regions
```

---

## Task 1: API Key Middleware

**Files:**
- Create: `src/anif_platform/auth/middleware.py`
- Modify: `src/anif_platform/auth/__init__.py`

- [ ] **Step 1: Create `src/anif_platform/auth/middleware.py`**

  ```python
  """Simple API key authentication — placeholder until B6 X.509 auth.

  All endpoints depend on `get_api_key`. In B6 this dependency is replaced
  with the full X.509/JWT middleware without changing the endpoint signatures.
  """

  from __future__ import annotations

  import os

  from fastapi import Depends, HTTPException, Security, status
  from fastapi.security import APIKeyHeader

  _API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


  async def get_api_key(api_key: str | None = Security(_API_KEY_HEADER)) -> str:
      """
      Validate the X-API-Key header against ANIF_API_KEY env var.

      Raises HTTP 401 if the key is missing or incorrect.
      Replace this dependency in B6 with X.509/JWT auth.
      """
      expected = os.environ.get("ANIF_API_KEY", "")
      if not expected:
          raise HTTPException(
              status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="ANIF_API_KEY environment variable is not set",
          )
      if api_key != expected:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Invalid or missing API key",
          )
      return api_key
  ```

- [ ] **Step 2: Update `src/anif_platform/auth/__init__.py`**

  ```python
  """ANIF auth module."""

  from anif_platform.auth.middleware import get_api_key

  __all__ = ["get_api_key"]
  ```

- [ ] **Step 3: Verify import**

  ```bash
  .venv/bin/python -c "from anif_platform.auth import get_api_key; print('OK')"
  ```

- [ ] **Step 4: Commit**

  ```bash
  git add src/anif_platform/auth/middleware.py src/anif_platform/auth/__init__.py
  git commit -m "feat: add API key auth middleware (placeholder for B6 X.509)"
  ```

---

## Task 2: Intents Database Migration

**Files:**
- Create: `migrations/versions/002_create_intents.py`

### Schema design
The `intents` table stores metadata. The full intent YAML lives in Git. The platform stores enough to reconstruct what was validated and where to fetch the original.

- [ ] **Step 1: Create `migrations/versions/002_create_intents.py`**

  ```python
  """create intents table

  Revision ID: 002
  Revises: 001
  Create Date: 2026-04-13
  """

  from __future__ import annotations

  import sqlalchemy as sa
  from alembic import op
  from sqlalchemy.dialects.postgresql import JSONB, UUID

  revision = "002"
  down_revision = "001"
  branch_labels = None
  depends_on = None


  def upgrade() -> None:
      op.create_table(
          "intents",
          sa.Column("intent_id", UUID(as_uuid=True), nullable=False),
          sa.Column("change_number", sa.Integer, nullable=False, autoincrement=True),
          sa.Column("version", sa.String(64), nullable=False, server_default="0.1.0"),
          sa.Column("service", sa.String(256), nullable=False),
          sa.Column("status", sa.String(32), nullable=False, server_default="validated"),
          # Git provenance
          sa.Column("git_repo_url", sa.Text, nullable=True),
          sa.Column("git_path", sa.Text, nullable=True),
          sa.Column("git_commit_sha", sa.String(40), nullable=True),
          # Fully resolved intent with defaults applied (ANIF-301 §6)
          sa.Column("resolved_intent", JSONB, nullable=False),
          # Validation metadata
          sa.Column("warnings", JSONB, nullable=False, server_default="[]"),
          sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
          sa.PrimaryKeyConstraint("intent_id"),
          sa.UniqueConstraint("change_number", name="uq_intents_change_number"),
      )
      op.create_index("ix_intents_service", "intents", ["service"])
      op.create_index("ix_intents_status", "intents", ["status"])
      op.create_index("ix_intents_created_at", "intents", ["created_at"])
      op.create_index("ix_intents_git_commit_sha", "intents", ["git_commit_sha"])


  def downgrade() -> None:
      op.drop_index("ix_intents_git_commit_sha", table_name="intents")
      op.drop_index("ix_intents_created_at", table_name="intents")
      op.drop_index("ix_intents_status", table_name="intents")
      op.drop_index("ix_intents_service", table_name="intents")
      op.drop_table("intents")
  ```

- [ ] **Step 2: Apply migration**

  ```bash
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif_test .venv/bin/alembic upgrade head
  DATABASE_URL=postgresql://anif:anif_dev@localhost:5432/anif .venv/bin/alembic upgrade head
  ```

  Expected: `Running upgrade 001 -> 002, create intents table`

- [ ] **Step 3: Commit**

  ```bash
  git add migrations/versions/002_create_intents.py
  git commit -m "feat: add intents table migration (ANIF-301)"
  ```

---

## Task 3: Intent Schemas + SQLAlchemy Model

**Files:**
- Create: `src/anif_platform/intent/schemas.py`
- Create: `src/anif_platform/intent/models.py`

- [ ] **Step 1: Create `src/anif_platform/intent/schemas.py`**

  ```python
  """Pydantic schemas for the Intent Engine — ANIF-301."""

  from __future__ import annotations

  from datetime import datetime
  from typing import Any, Optional
  from uuid import UUID

  from pydantic import BaseModel

  from anif_platform.schemas.intent import Intent


  class GitIntentRef(BaseModel):
      """Provenance of an intent sourced from Git."""

      repo_url: str
      path: str
      commit_sha: str


  class ValidationResult(BaseModel):
      """
      Result of validating an intent document — ANIF-301 §8.

      On success: intent_id is assigned, validated_intent has defaults applied.
      On failure: intent_id is None, errors is non-empty.
      """

      intent_id: Optional[UUID] = None
      status: str  # "validated" | "validation_failed"
      errors: list[str] = []
      warnings: list[str] = []
      validated_intent: Optional[dict[str, Any]] = None


  class ValidatedIntent(BaseModel):
      """A registered, validated intent with its assigned UUID and Git provenance."""

      intent_id: UUID
      change_number: int
      version: str
      service: str
      status: str
      git_ref: Optional[GitIntentRef] = None
      resolved_intent: dict[str, Any]
      warnings: list[str]
      created_at: datetime
  ```

- [ ] **Step 2: Create `src/anif_platform/intent/models.py`**

  ```python
  """SQLAlchemy ORM model for intents — ANIF-301."""

  from __future__ import annotations

  from datetime import datetime
  from typing import Any
  from uuid import UUID

  from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
  from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
  from sqlalchemy.orm import Mapped, mapped_column

  from anif_platform.database import Base


  class IntentRow(Base):
      """Registered, validated intent record."""

      __tablename__ = "intents"

      intent_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
      change_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
      version: Mapped[str] = mapped_column(String(64), nullable=False, default="0.1.0")
      service: Mapped[str] = mapped_column(String(256), nullable=False)
      status: Mapped[str] = mapped_column(String(32), nullable=False, default="validated")
      git_repo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
      git_path: Mapped[str | None] = mapped_column(Text, nullable=True)
      git_commit_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)
      resolved_intent: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
      warnings: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
      created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

      __table_args__ = (UniqueConstraint("change_number", name="uq_intents_change_number"),)
  ```

- [ ] **Step 3: Commit**

  ```bash
  git add src/anif_platform/intent/schemas.py src/anif_platform/intent/models.py
  git commit -m "feat: add intent Pydantic schemas and SQLAlchemy model (ANIF-301)"
  ```

---

## Task 4: IntentValidator

**Spec:** ANIF-301 §5, §6, §7 (VAL-001–VAL-007)
**Files:**
- Create: `src/anif_platform/intent/validator.py`
- Create: `tests/unit/test_intent_validator.py`

### MUSTs
- VAL-001 warning: latency_ms < 10 (non-blocking)
- VAL-002 error: availability_percent outside 90–100
- VAL-003 error: prod environment without high/critical priority
- VAL-004 error: pci_compliant policy without encryption=true
- VAL-005 error: availability_percent >= 99.99 with < 2 allowed_zones
- VAL-006 error: region not in EU/US/APAC (covered by Pydantic, but must return correct message)
- VAL-007 error: unrecognised policy name
- All rules MUST be evaluated — MUST NOT short-circuit on first error (ANIF-301 §10.4)
- Optional fields MUST have defaults applied before further processing (ANIF-301 §6)
- `environment` defaults to `dev`, `priority` defaults to `medium`, `policies` defaults to `[]`

- [ ] **Step 1: Write the failing tests**

  Create `tests/unit/test_intent_validator.py`:

  ```python
  """Tests for IntentValidator — ANIF-301 §7 (VAL-001–VAL-007)."""

  import pytest

  from anif_platform.intent.validator import IntentValidator
  from anif_platform.schemas.intent import (
      Constraints,
      Environment,
      Intent,
      Objectives,
      PolicyName,
      Priority,
      Region,
  )


  def make_valid_prod_intent(**kwargs) -> Intent:
      defaults = dict(
          service="payments",
          environment=Environment.prod,
          objectives=Objectives(availability_percent=99.5, latency_ms=50),
          constraints=Constraints(region=Region.EU, encryption=True, allowed_zones=["eu-a"]),
          priority=Priority.high,
      )
      defaults.update(kwargs)
      return Intent(**defaults)


  class TestDefaultsApplied:
      def test_environment_defaults_to_dev(self) -> None:
          intent = Intent(
              service="svc",
              objectives=Objectives(latency_ms=50),
              constraints=Constraints(region=Region.EU),
          )
          validator = IntentValidator()
          result = validator.validate(intent)
          assert result.validated_intent["environment"] == "dev"

      def test_priority_defaults_to_medium(self) -> None:
          intent = Intent(
              service="svc",
              objectives=Objectives(latency_ms=50),
              constraints=Constraints(region=Region.EU),
          )
          validator = IntentValidator()
          result = validator.validate(intent)
          assert result.validated_intent["priority"] == "medium"

      def test_policies_defaults_to_empty_list(self) -> None:
          intent = Intent(
              service="svc",
              objectives=Objectives(latency_ms=50),
              constraints=Constraints(region=Region.EU),
          )
          validator = IntentValidator()
          result = validator.validate(intent)
          assert result.validated_intent["policies"] == []


  class TestVAL001LatencyWarning:
      def test_latency_below_10_produces_warning(self) -> None:
          intent = make_valid_prod_intent(
              objectives=Objectives(latency_ms=5, availability_percent=99.5)
          )
          validator = IntentValidator()
          result = validator.validate(intent)
          assert result.intent_id is not None  # warning does not block
          assert any("latency_ms" in w and "10 ms" in w for w in result.warnings)

      def test_latency_at_10_no_warning(self) -> None:
          intent = make_valid_prod_intent(
              objectives=Objectives(latency_ms=10, availability_percent=99.5)
          )
          result = IntentValidator().validate(intent)
          assert not any("latency_ms" in w for w in result.warnings)


  class TestVAL003ProdPriority:
      def test_prod_without_high_priority_fails(self) -> None:
          intent = make_valid_prod_intent(priority=Priority.low)
          result = IntentValidator().validate(intent)
          assert result.intent_id is None
          assert any("priority" in e and "prod" in e for e in result.errors)

      def test_prod_with_medium_priority_fails(self) -> None:
          intent = make_valid_prod_intent(priority=Priority.medium)
          result = IntentValidator().validate(intent)
          assert result.intent_id is None

      def test_prod_with_high_priority_passes(self) -> None:
          result = IntentValidator().validate(make_valid_prod_intent(priority=Priority.high))
          assert result.intent_id is not None

      def test_prod_with_critical_priority_passes(self) -> None:
          result = IntentValidator().validate(make_valid_prod_intent(priority=Priority.critical))
          assert result.intent_id is not None

      def test_staging_with_low_priority_passes(self) -> None:
          intent = Intent(
              service="svc",
              environment=Environment.staging,
              objectives=Objectives(latency_ms=50),
              constraints=Constraints(region=Region.EU, encryption=True),
              priority=Priority.low,
          )
          result = IntentValidator().validate(intent)
          assert result.intent_id is not None


  class TestVAL004PCIEncryption:
      def test_pci_without_encryption_fails(self) -> None:
          intent = make_valid_prod_intent(
              constraints=Constraints(region=Region.EU, encryption=False, allowed_zones=["eu-a"]),
              policies=[PolicyName.pci_compliant],
          )
          result = IntentValidator().validate(intent)
          assert result.intent_id is None
          assert any("encryption" in e and "pci_compliant" in e for e in result.errors)

      def test_pci_with_encryption_passes(self) -> None:
          intent = make_valid_prod_intent(
              constraints=Constraints(region=Region.EU, encryption=True, allowed_zones=["eu-a"]),
              policies=[PolicyName.pci_compliant],
          )
          result = IntentValidator().validate(intent)
          assert result.intent_id is not None


  class TestVAL005HighAvailabilityZones:
      def test_99_99_availability_requires_2_zones(self) -> None:
          intent = make_valid_prod_intent(
              objectives=Objectives(availability_percent=99.99),
              constraints=Constraints(
                  region=Region.EU, encryption=True, allowed_zones=["eu-a"]
              ),
          )
          result = IntentValidator().validate(intent)
          assert result.intent_id is None
          assert any("allowed_zones" in e and "2" in e for e in result.errors)

      def test_99_99_availability_with_2_zones_passes(self) -> None:
          intent = make_valid_prod_intent(
              objectives=Objectives(availability_percent=99.99),
              constraints=Constraints(
                  region=Region.EU, encryption=True, allowed_zones=["eu-a", "eu-b"]
              ),
          )
          result = IntentValidator().validate(intent)
          assert result.intent_id is not None

      def test_99_9_availability_with_1_zone_passes(self) -> None:
          intent = make_valid_prod_intent(
              objectives=Objectives(availability_percent=99.9),
              constraints=Constraints(
                  region=Region.EU, encryption=True, allowed_zones=["eu-a"]
              ),
          )
          result = IntentValidator().validate(intent)
          assert result.intent_id is not None


  class TestMultipleErrors:
      def test_all_errors_returned_without_short_circuit(self) -> None:
          """ANIF-301 §10.4: MUST NOT short-circuit on first error."""
          intent = Intent(
              service="billing",
              environment=Environment.prod,
              objectives=Objectives(availability_percent=99.99),
              constraints=Constraints(
                  region=Region.EU,
                  encryption=False,
                  allowed_zones=["eu-a"],
              ),
              policies=[PolicyName.pci_compliant],
              priority=Priority.medium,
          )
          result = IntentValidator().validate(intent)
          assert result.intent_id is None
          # Should have: VAL-003 (prod+medium), VAL-004 (pci+no-encryption), VAL-005 (99.99+1zone)
          assert len(result.errors) >= 3

      def test_intent_id_not_assigned_when_any_blocking_error(self) -> None:
          """ANIF-301 §10.5: intent_id MUST NOT be assigned when any blocking rule violated."""
          intent = make_valid_prod_intent(priority=Priority.low)
          result = IntentValidator().validate(intent)
          assert result.intent_id is None
          assert result.status == "validation_failed"

      def test_status_is_validated_on_success(self) -> None:
          result = IntentValidator().validate(make_valid_prod_intent())
          assert result.status == "validated"
          assert result.intent_id is not None
  ```

- [ ] **Step 2: Verify tests fail**

  ```bash
  .venv/bin/pytest tests/unit/test_intent_validator.py -v 2>&1 | head -10
  ```

  Expected: `ModuleNotFoundError`

- [ ] **Step 3: Create `src/anif_platform/intent/validator.py`**

  ```python
  """IntentValidator — ANIF-301 §7, VAL-001 through VAL-007."""

  from __future__ import annotations

  from uuid import uuid4

  from anif_platform.intent.schemas import ValidationResult
  from anif_platform.schemas.intent import Environment, Intent, PolicyName, Priority


  class IntentValidator:
      """
      Validates an intent document against all ANIF-301 rules.

      All rules are evaluated — validation MUST NOT short-circuit on the first
      error (ANIF-301 §10.4). Multiple errors MAY be returned in a single result.
      """

      def validate(self, intent: Intent) -> ValidationResult:
          """
          Validate an intent and apply defaults.

          Returns ValidationResult with:
          - intent_id set and status="validated" if no blocking errors
          - intent_id=None and status="validation_failed" if any blocking error
          """
          errors: list[str] = []
          warnings: list[str] = []

          # Apply defaults before validation (ANIF-301 §6)
          resolved = intent.model_dump(mode="json")
          if resolved.get("environment") is None:
              resolved["environment"] = Environment.dev.value
          if resolved.get("priority") is None:
              resolved["priority"] = Priority.medium.value
          if resolved.get("policies") is None:
              resolved["policies"] = []

          environment = resolved["environment"]
          priority = resolved["priority"]
          policies = resolved["policies"]
          objectives = resolved.get("objectives") or {}
          constraints = resolved.get("constraints") or {}

          # VAL-001 — latency warning (non-blocking)
          latency = objectives.get("latency_ms")
          if latency is not None and latency < 10:
              warnings.append(
                  "objectives.latency_ms: value below 10 ms is unlikely to be achievable "
                  "in most environments; proceeding with intent submission"
              )

          # VAL-003 — prod requires high or critical priority (blocking)
          if environment == Environment.prod.value:
              if priority not in (Priority.high.value, Priority.critical.value):
                  errors.append(
                      f"priority: production environment requires priority to be "
                      f"'high' or 'critical'; received '{priority}'"
                  )

          # VAL-004 — pci_compliant requires encryption=true (blocking)
          if PolicyName.pci_compliant.value in policies:
              encryption = constraints.get("encryption")
              if encryption is not True:
                  errors.append(
                      "constraints.encryption: pci_compliant policy requires encryption to be true"
                  )

          # VAL-005 — availability >= 99.99 requires >= 2 allowed_zones (blocking)
          availability = objectives.get("availability_percent")
          if availability is not None and availability >= 99.99:
              allowed_zones = constraints.get("allowed_zones") or []
              n = len(allowed_zones)
              if n < 2:
                  errors.append(
                      f"constraints.allowed_zones: availability_percent >= 99.99 requires "
                      f"at least 2 allowed zones; {n} provided"
                  )

          if errors:
              return ValidationResult(
                  status="validation_failed",
                  errors=errors,
                  warnings=warnings,
              )

          return ValidationResult(
              intent_id=uuid4(),
              status="validated",
              warnings=warnings,
              validated_intent=resolved,
          )
  ```

- [ ] **Step 4: Verify tests pass**

  ```bash
  .venv/bin/pytest tests/unit/test_intent_validator.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/anif_platform/intent/validator.py tests/unit/test_intent_validator.py
  git commit -m "feat: implement IntentValidator with VAL-001–VAL-007 (ANIF-301)"
  ```

---

## Task 5: IntentRegistry

**Files:**
- Create: `src/anif_platform/intent/registry.py`

- [ ] **Step 1: Create `src/anif_platform/intent/registry.py`**

  ```python
  """IntentRegistry — persists and retrieves validated intents."""

  from __future__ import annotations

  from datetime import UTC, datetime
  from typing import Optional
  from uuid import UUID

  from sqlalchemy import func, select
  from sqlalchemy.ext.asyncio import AsyncSession

  from anif_platform.intent.models import IntentRow
  from anif_platform.intent.schemas import GitIntentRef, ValidatedIntent, ValidationResult


  class IntentRegistry:
      """Stores and retrieves validated intent records."""

      def __init__(self, session: AsyncSession) -> None:
          self._session = session

      async def register(
          self,
          result: ValidationResult,
          git_ref: Optional[GitIntentRef] = None,
      ) -> ValidatedIntent:
          """
          Persist a validated intent.

          result.intent_id MUST be set (call only after successful validation).
          Returns the registered ValidatedIntent.
          """
          assert result.intent_id is not None
          assert result.validated_intent is not None

          change_number = await self._next_change_number()

          row = IntentRow(
              intent_id=result.intent_id,
              change_number=change_number,
              version="0.1.0",
              service=result.validated_intent["service"],
              status="validated",
              git_repo_url=git_ref.repo_url if git_ref else None,
              git_path=git_ref.path if git_ref else None,
              git_commit_sha=git_ref.commit_sha if git_ref else None,
              resolved_intent=result.validated_intent,
              warnings=result.warnings,
              created_at=datetime.now(UTC),
          )
          self._session.add(row)
          await self._session.flush()

          return self._row_to_schema(row, git_ref)

      async def get(self, intent_id: UUID) -> Optional[ValidatedIntent]:
          """Return a registered intent by ID, or None if not found."""
          result = await self._session.execute(
              select(IntentRow).where(IntentRow.intent_id == intent_id)
          )
          row = result.scalar_one_or_none()
          if row is None:
              return None
          git_ref = None
          if row.git_repo_url:
              git_ref = GitIntentRef(
                  repo_url=row.git_repo_url,
                  path=row.git_path or "",
                  commit_sha=row.git_commit_sha or "",
              )
          return self._row_to_schema(row, git_ref)

      async def _next_change_number(self) -> int:
          result = await self._session.execute(select(func.max(IntentRow.change_number)))
          current_max = result.scalar_one_or_none()
          return (current_max or 0) + 1

      @staticmethod
      def _row_to_schema(
          row: IntentRow, git_ref: Optional[GitIntentRef]
      ) -> ValidatedIntent:
          return ValidatedIntent(
              intent_id=row.intent_id,
              change_number=row.change_number,
              version=row.version,
              service=row.service,
              status=row.status,
              git_ref=git_ref,
              resolved_intent=row.resolved_intent,
              warnings=row.warnings,
              created_at=row.created_at,
          )
  ```

- [ ] **Step 2: Commit**

  ```bash
  git add src/anif_platform/intent/registry.py
  git commit -m "feat: add IntentRegistry for persisting validated intents (ANIF-301)"
  ```

---

## Task 6: Built-In Policy YAML Files

**Spec:** ANIF-302 §7
**Files:** `policies/zero_trust.yml`, `policies/no_public_ingress.yml`, `policies/pci_compliant.yml`, `policies/data_residency.yml`

These are the four built-in policies. Custom policies drop in alongside them.

- [ ] **Step 1: Create `policies/zero_trust.yml`**

  ```yaml
  name: zero_trust
  category: security
  version: "1.0.0"
  rules:
    - condition: "constraints.encryption:equals:false"
      action: deny
      reason: "Zero trust requires encryption to be explicitly enabled"
    - condition: "constraints.region:not_in_list:[EU,US,APAC]"
      action: deny
      reason: "Zero trust requires a valid region to be declared"
  ```

- [ ] **Step 2: Create `policies/no_public_ingress.yml`**

  ```yaml
  name: no_public_ingress
  category: security
  version: "1.0.0"
  rules:
    - condition: "constraints.allowed_zones:equals:[]"
      action: deny
      reason: "Public ingress is prohibited; at least one allowed zone must be specified"
  ```

- [ ] **Step 3: Create `policies/pci_compliant.yml`**

  ```yaml
  name: pci_compliant
  category: compliance
  version: "1.0.0"
  rules:
    - condition: "constraints.encryption:equals:false"
      action: deny
      reason: "PCI compliance requires encryption to be true"
    - condition: "constraints.encryption:not_equals:true"
      action: deny
      reason: "PCI compliance requires encryption to be explicitly set to true"
  ```

- [ ] **Step 4: Create `policies/data_residency.yml`**

  ```yaml
  name: data_residency
  category: compliance
  version: "1.0.0"
  rules:
    - condition: "constraints.region:not_in_list:[EU,US,APAC]"
      action: deny
      reason: "Data residency policy: region is not in the approved region list"
  ```

  Note: The approved region list defaults to `EU,US,APAC`. Override via `DATA_RESIDENCY_APPROVED_REGIONS` env var. The PolicyLoader rewrites this at load time.

- [ ] **Step 5: Commit**

  ```bash
  git add policies/
  git commit -m "feat: add four built-in policy YAML files (ANIF-302 §7)"
  ```

---

## Task 7: ConditionEvaluator

**Spec:** ANIF-302 §6
**Files:**
- Create: `src/anif_platform/policy/condition.py`
- Create: `tests/unit/test_condition_evaluator.py`

### MUSTs
- All 8 operators MUST be implemented (ANIF-302 §6.2)
- Missing field behaviour MUST be correct per ANIF-302 §6.3
- Type coercion MUST NOT be performed for `equals`/`not_equals` (ANIF-302 §6.2)

- [ ] **Step 1: Write the failing tests**

  Create `tests/unit/test_condition_evaluator.py`:

  ```python
  """Tests for ConditionEvaluator — ANIF-302 §6."""

  import pytest

  from anif_platform.policy.condition import ConditionEvaluator, ConditionParseError


  class TestEquals:
      def test_string_equals_match(self) -> None:
          assert ConditionEvaluator.evaluate(
              "environment:equals:prod", {"environment": "prod"}
          ) is True

      def test_string_equals_no_match(self) -> None:
          assert ConditionEvaluator.evaluate(
              "environment:equals:prod", {"environment": "staging"}
          ) is False

      def test_boolean_equals_false(self) -> None:
          assert ConditionEvaluator.evaluate(
              "constraints.encryption:equals:false",
              {"constraints": {"encryption": False}},
          ) is True

      def test_boolean_equals_true(self) -> None:
          assert ConditionEvaluator.evaluate(
              "constraints.encryption:equals:true",
              {"constraints": {"encryption": True}},
          ) is True

      def test_no_type_coercion(self) -> None:
          """ANIF-302 §6.2: type coercion MUST NOT be performed."""
          # string "false" != boolean False
          assert ConditionEvaluator.evaluate(
              "constraints.encryption:equals:false",
              {"constraints": {"encryption": "false"}},
          ) is False

      def test_number_equals(self) -> None:
          assert ConditionEvaluator.evaluate(
              "objectives.latency_ms:equals:50",
              {"objectives": {"latency_ms": 50}},
          ) is True


  class TestNotEquals:
      def test_not_equals_match(self) -> None:
          assert ConditionEvaluator.evaluate(
              "environment:not_equals:prod", {"environment": "staging"}
          ) is True

      def test_not_equals_no_match(self) -> None:
          assert ConditionEvaluator.evaluate(
              "environment:not_equals:prod", {"environment": "prod"}
          ) is False


  class TestGreaterThan:
      def test_greater_than_match(self) -> None:
          assert ConditionEvaluator.evaluate(
              "objectives.availability_percent:greater_than:99.98",
              {"objectives": {"availability_percent": 99.99}},
          ) is True

      def test_greater_than_equal_is_false(self) -> None:
          assert ConditionEvaluator.evaluate(
              "objectives.latency_ms:greater_than:50",
              {"objectives": {"latency_ms": 50}},
          ) is False


  class TestLessThan:
      def test_less_than_match(self) -> None:
          assert ConditionEvaluator.evaluate(
              "objectives.latency_ms:less_than:10",
              {"objectives": {"latency_ms": 5}},
          ) is True

      def test_less_than_equal_is_false(self) -> None:
          assert ConditionEvaluator.evaluate(
              "objectives.latency_ms:less_than:10",
              {"objectives": {"latency_ms": 10}},
          ) is False


  class TestContains:
      def test_array_contains_value(self) -> None:
          assert ConditionEvaluator.evaluate(
              "policies:contains:pci_compliant",
              {"policies": ["zero_trust", "pci_compliant"]},
          ) is True

      def test_array_does_not_contain(self) -> None:
          assert ConditionEvaluator.evaluate(
              "policies:contains:pci_compliant",
              {"policies": ["zero_trust"]},
          ) is False

      def test_string_contains_substring(self) -> None:
          assert ConditionEvaluator.evaluate(
              "service:contains:payments",
              {"service": "payments-gateway"},
          ) is True


  class TestNotContains:
      def test_array_not_contains(self) -> None:
          assert ConditionEvaluator.evaluate(
              "policies:not_contains:pci_compliant",
              {"policies": ["zero_trust"]},
          ) is True


  class TestInList:
      def test_value_in_list(self) -> None:
          assert ConditionEvaluator.evaluate(
              "constraints.region:in_list:[EU,US,APAC]",
              {"constraints": {"region": "EU"}},
          ) is True

      def test_value_not_in_list(self) -> None:
          assert ConditionEvaluator.evaluate(
              "constraints.region:in_list:[EU,US]",
              {"constraints": {"region": "APAC"}},
          ) is False


  class TestNotInList:
      def test_value_not_in_list(self) -> None:
          assert ConditionEvaluator.evaluate(
              "constraints.region:not_in_list:[EU,US,APAC]",
              {"constraints": {"region": "INVALID"}},
          ) is True

      def test_value_in_list_returns_false(self) -> None:
          assert ConditionEvaluator.evaluate(
              "constraints.region:not_in_list:[EU,US,APAC]",
              {"constraints": {"region": "EU"}},
          ) is False


  class TestMissingFieldBehaviour:
      """ANIF-302 §6.3: missing field behaviour."""

      def test_equals_missing_field_is_false(self) -> None:
          assert ConditionEvaluator.evaluate("constraints.encryption:equals:false", {}) is False

      def test_not_equals_missing_field_is_true(self) -> None:
          assert ConditionEvaluator.evaluate("constraints.encryption:not_equals:true", {}) is True

      def test_contains_missing_array_is_false(self) -> None:
          assert ConditionEvaluator.evaluate("constraints.allowed_zones:contains:eu-a", {}) is False

      def test_not_contains_missing_array_is_true(self) -> None:
          assert ConditionEvaluator.evaluate(
              "constraints.allowed_zones:not_contains:eu-a", {}
          ) is True

      def test_greater_than_missing_field_is_false(self) -> None:
          assert ConditionEvaluator.evaluate("objectives.latency_ms:greater_than:10", {}) is False

      def test_less_than_missing_field_is_false(self) -> None:
          assert ConditionEvaluator.evaluate("objectives.latency_ms:less_than:10", {}) is False

      def test_in_list_missing_field_is_false(self) -> None:
          assert ConditionEvaluator.evaluate("constraints.region:in_list:[EU,US]", {}) is False

      def test_not_in_list_missing_field_is_true(self) -> None:
          assert ConditionEvaluator.evaluate(
              "constraints.region:not_in_list:[EU,US]", {}
          ) is True


  class TestParseErrors:
      def test_malformed_expression_raises(self) -> None:
          with pytest.raises(ConditionParseError):
              ConditionEvaluator.evaluate("not_a_valid_condition", {})

      def test_unknown_operator_raises(self) -> None:
          with pytest.raises(ConditionParseError):
              ConditionEvaluator.evaluate("field:unknown_op:value", {})
  ```

- [ ] **Step 2: Verify tests fail**

  ```bash
  .venv/bin/pytest tests/unit/test_condition_evaluator.py -v 2>&1 | head -10
  ```

- [ ] **Step 3: Create `src/anif_platform/policy/condition.py`**

  ```python
  """Policy condition evaluator — ANIF-302 §6."""

  from __future__ import annotations

  from typing import Any


  class ConditionParseError(Exception):
      """Raised when a condition expression cannot be parsed."""


  def _get_field(path: str, intent: dict[str, Any]) -> Any:
      """Resolve a dot-separated field path in an intent dict. Returns None if missing."""
      parts = path.split(".")
      value: Any = intent
      for part in parts:
          if not isinstance(value, dict) or part not in value:
              return None
          value = value[part]
      return value


  def _field_missing(path: str, intent: dict[str, Any]) -> bool:
      """Return True if the field path is not present in the intent."""
      parts = path.split(".")
      value: Any = intent
      for part in parts:
          if not isinstance(value, dict) or part not in value:
              return True
          value = value[part]
      return False


  def _coerce_value(raw: str, field_value: Any) -> Any:
      """
      Parse the condition literal to match the type of the field value.

      Type coercion is NOT applied for equals/not_equals (ANIF-302 §6.2).
      This function is used for numeric comparisons only.
      """
      try:
          return float(raw)
      except ValueError:
          return raw


  def _parse_list_literal(raw: str) -> list[str]:
      """Parse [EU,US,APAC] → ['EU', 'US', 'APAC']."""
      raw = raw.strip()
      if raw.startswith("[") and raw.endswith("]"):
          inner = raw[1:-1]
          if not inner:
              return []
          return [v.strip() for v in inner.split(",")]
      return [v.strip() for v in raw.split(",")]


  def _parse_bool_or_string(raw: str) -> Any:
      """Parse 'true'/'false' to bool, otherwise return as string."""
      if raw.lower() == "true":
          return True
      if raw.lower() == "false":
          return False
      return raw


  class ConditionEvaluator:
      """
      Evaluates ANIF policy condition expressions — ANIF-302 §6.

      Condition syntax: field_path:operator:value
      All 8 operators are supported. Missing field behaviour per ANIF-302 §6.3.
      """

      _VALID_OPERATORS = {
          "equals", "not_equals", "greater_than", "less_than",
          "contains", "not_contains", "in_list", "not_in_list",
      }

      @classmethod
      def evaluate(cls, condition: str, intent: dict[str, Any]) -> bool:
          """
          Evaluate a condition expression against an intent dict.

          Returns True if the condition matches, False otherwise.
          Raises ConditionParseError if the expression is malformed.
          """
          parts = condition.split(":", 2)
          if len(parts) != 3:
              raise ConditionParseError(
                  f"Invalid condition expression '{condition}': "
                  "expected 'field_path:operator:value'"
              )
          field_path, operator, raw_value = parts

          if operator not in cls._VALID_OPERATORS:
              raise ConditionParseError(
                  f"Unknown operator '{operator}' in condition '{condition}'"
              )

          missing = _field_missing(field_path, intent)
          field_value = _get_field(field_path, intent)

          # Missing field behaviour — ANIF-302 §6.3
          if missing:
              if operator in ("equals", "in_list", "contains", "greater_than", "less_than"):
                  return False
              if operator in ("not_equals", "not_in_list", "not_contains"):
                  return True
              return False

          if operator == "equals":
              return field_value == _parse_bool_or_string(raw_value)

          if operator == "not_equals":
              return field_value != _parse_bool_or_string(raw_value)

          if operator == "greater_than":
              try:
                  return float(field_value) > float(raw_value)
              except (TypeError, ValueError):
                  return False

          if operator == "less_than":
              try:
                  return float(field_value) < float(raw_value)
              except (TypeError, ValueError):
                  return False

          if operator == "contains":
              if isinstance(field_value, list):
                  return raw_value in field_value
              if isinstance(field_value, str):
                  return raw_value in field_value
              return False

          if operator == "not_contains":
              if isinstance(field_value, list):
                  return raw_value not in field_value
              if isinstance(field_value, str):
                  return raw_value not in field_value
              return True

          if operator == "in_list":
              allowed = _parse_list_literal(raw_value)
              return str(field_value) in allowed

          if operator == "not_in_list":
              allowed = _parse_list_literal(raw_value)
              return str(field_value) not in allowed

          return False  # unreachable
  ```

- [ ] **Step 4: Verify tests pass**

  ```bash
  .venv/bin/pytest tests/unit/test_condition_evaluator.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/anif_platform/policy/condition.py tests/unit/test_condition_evaluator.py
  git commit -m "feat: implement ConditionEvaluator with all 8 operators (ANIF-302 §6)"
  ```

---

## Task 8: PolicyLoader

**Spec:** ANIF-302 §5, §7
**Files:**
- Create: `src/anif_platform/policy/loader.py`

The loader reads every `.yml` file from `policies/` at startup. The `data_residency` policy has its region list rewritten from the `DATA_RESIDENCY_APPROVED_REGIONS` env var.

- [ ] **Step 1: Create `src/anif_platform/policy/loader.py`**

  ```python
  """PolicyLoader — loads policy YAML files from the policies/ directory."""

  from __future__ import annotations

  import os
  from pathlib import Path
  from typing import Any

  import yaml

  from anif_platform.schemas.policy import Policy, PolicyRule, RuleAction


  class PolicyLoadError(Exception):
      """Raised when a policy file cannot be loaded or is invalid."""


  class PolicyLoader:
      """
      Loads policy definitions from YAML files.

      All .yml files in the policies directory are loaded at startup.
      Drop in new .yml files to add policies — no code changes required.
      The data_residency policy has its approved region list rewritten
      from DATA_RESIDENCY_APPROVED_REGIONS env var before evaluation.
      """

      def __init__(self, policies_dir: str | Path | None = None) -> None:
          if policies_dir is None:
              # Default to policies/ at project root
              self._dir = Path(__file__).parent.parent.parent.parent / "policies"
          else:
              self._dir = Path(policies_dir)

      def load_all(self) -> dict[str, dict[str, Any]]:
          """
          Load all policy YAML files from the policies directory.

          Returns a dict mapping policy name → raw policy dict.
          Raises PolicyLoadError if any file is invalid.
          """
          if not self._dir.exists():
              raise PolicyLoadError(f"Policies directory not found: {self._dir}")

          policies: dict[str, dict[str, Any]] = {}
          for path in sorted(self._dir.glob("*.yml")):
              policy = self._load_file(path)
              name = policy.get("name")
              if not name:
                  raise PolicyLoadError(f"Policy file {path} is missing 'name' field")
              policies[name] = policy

          return self._apply_env_overrides(policies)

      def _load_file(self, path: Path) -> dict[str, Any]:
          try:
              with open(path) as f:
                  data = yaml.safe_load(f)
              if not isinstance(data, dict):
                  raise PolicyLoadError(f"Policy file {path} must be a YAML object")
              # Validate against Policy schema (ANIF-302 §5 / ANIF-600 §5.3)
              self._validate_policy_schema(data, path)
              return data
          except yaml.YAMLError as exc:
              raise PolicyLoadError(f"Failed to parse {path}: {exc}") from exc

      @staticmethod
      def _validate_policy_schema(data: dict[str, Any], path: Path) -> None:
          """Policies that fail schema validation MUST be rejected — ANIF-600 §5.3."""
          if "name" not in data:
              raise PolicyLoadError(f"{path}: missing required field 'name'")
          if "rules" not in data or not isinstance(data["rules"], list) or len(data["rules"]) == 0:
              raise PolicyLoadError(f"{path}: 'rules' must be a non-empty list")
          valid_actions = {a.value for a in RuleAction}
          for i, rule in enumerate(data["rules"]):
              if "condition" not in rule:
                  raise PolicyLoadError(f"{path}: rule {i} missing 'condition'")
              if "action" not in rule:
                  raise PolicyLoadError(f"{path}: rule {i} missing 'action'")
              if rule["action"] not in valid_actions:
                  raise PolicyLoadError(
                      f"{path}: rule {i} has invalid action '{rule['action']}'"
                  )

      @staticmethod
      def _apply_env_overrides(policies: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
          """
          Apply environment variable overrides to parameterised policies.

          data_residency: rewrites the approved region list from
          DATA_RESIDENCY_APPROVED_REGIONS env var (comma-separated).
          """
          approved = os.environ.get("DATA_RESIDENCY_APPROVED_REGIONS", "EU,US,APAC")
          region_list = "[" + ",".join(r.strip() for r in approved.split(",")) + "]"

          if "data_residency" in policies:
              for rule in policies["data_residency"]["rules"]:
                  if "{approved_regions}" in rule.get("condition", ""):
                      rule["condition"] = rule["condition"].replace(
                          "{approved_regions}", approved
                      )
                  if "not_in_list:" in rule.get("condition", ""):
                      # Rewrite the list literal with current approved regions
                      parts = rule["condition"].split(":", 2)
                      if len(parts) == 3:
                          rule["condition"] = f"{parts[0]}:{parts[1]}:{region_list}"

          return policies
  ```

- [ ] **Step 2: Verify loader works against the policy files**

  ```bash
  cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold
  .venv/bin/python -c "
  from anif_platform.policy.loader import PolicyLoader
  p = PolicyLoader()
  policies = p.load_all()
  print('Loaded:', list(policies.keys()))
  "
  ```

  Expected: `Loaded: ['data_residency', 'no_public_ingress', 'pci_compliant', 'zero_trust']`

- [ ] **Step 3: Commit**

  ```bash
  git add src/anif_platform/policy/loader.py
  git commit -m "feat: add PolicyLoader for YAML-driven extensible policy loading (ANIF-302 §5)"
  ```

---

## Task 9: PolicyEngine + ConflictResolver

**Spec:** ANIF-302 §8, §9 · ANIF-303
**Files:**
- Create: `src/anif_platform/policy/conflict.py`
- Create: `src/anif_platform/policy/engine.py`
- Create: `tests/unit/test_policy_engine.py`
- Create: `tests/unit/test_conflict_resolver.py`

### MUSTs
- Engine MUST be 100% deterministic (ANIF-302 §4)
- All 4 built-in policies MUST be active for every evaluation (ANIF-302 §11.2)
- First matching rule determines policy decision; no match = allow (ANIF-302 §8)
- Overall result: any deny → fail; no deny but warn → warn; all allow → pass (ANIF-302 §8)
- Conflict detection MUST be exhaustive — all n*(n-1)/2 pairs checked (ANIF-303 §4.3)
- Precedence hierarchy: compliance > security > availability > performance (ANIF-303 §5)
- Equal-precedence conflicts MUST produce manual_review mode (ANIF-303 §6.2)
- `warn` MUST NOT be upgraded to `deny` by conflict resolution (ANIF-303 §10.9)
- Dry-run mode MUST NOT write audit records (ANIF-302 §10)

- [ ] **Step 1: Write the failing tests**

  Create `tests/unit/test_policy_engine.py`:

  ```python
  """Tests for PolicyEngine — ANIF-302."""

  import pytest

  from anif_platform.policy.engine import PolicyEngine
  from anif_platform.policy.loader import PolicyLoader


  def make_engine(policies_dir: str) -> PolicyEngine:
      loader = PolicyLoader(policies_dir)
      return PolicyEngine(loader)


  @pytest.fixture
  def engine(tmp_path) -> PolicyEngine:
      """Engine loaded with the real built-in policies."""
      import shutil
      from pathlib import Path
      src = Path(__file__).parent.parent.parent / "policies"
      dst = tmp_path / "policies"
      shutil.copytree(src, dst)
      return PolicyEngine(PolicyLoader(dst))


  class TestOverallResult:
      def test_pass_when_all_policies_allow(self, engine: PolicyEngine) -> None:
          intent = {
              "service": "payments",
              "environment": "prod",
              "objectives": {"latency_ms": 50, "availability_percent": 99.5},
              "constraints": {
                  "region": "EU",
                  "encryption": True,
                  "allowed_zones": ["eu-a", "eu-b"],
              },
              "policies": [],
              "priority": "high",
          }
          result = engine.evaluate(intent_id="test-id", resolved_intent=intent)
          assert result["overall_result"] == "pass"

      def test_fail_when_any_policy_denies(self, engine: PolicyEngine) -> None:
          intent = {
              "service": "payments",
              "environment": "prod",
              "objectives": {"latency_ms": 50},
              "constraints": {"region": "EU", "encryption": False},
              "policies": [],
              "priority": "high",
          }
          result = engine.evaluate(intent_id="test-id", resolved_intent=intent)
          assert result["overall_result"] == "fail"

      def test_evaluation_id_is_always_set(self, engine: PolicyEngine) -> None:
          intent = {
              "service": "svc",
              "constraints": {"region": "EU", "encryption": True, "allowed_zones": ["eu-a"]},
              "objectives": {"latency_ms": 50},
              "policies": [],
          }
          result = engine.evaluate(intent_id="test-id", resolved_intent=intent)
          assert result["evaluation_id"] is not None

      def test_deterministic_same_inputs_same_outputs(self, engine: PolicyEngine) -> None:
          """ANIF-302 §4: identical inputs MUST produce identical outputs."""
          intent = {
              "service": "svc",
              "constraints": {"region": "EU", "encryption": True, "allowed_zones": ["eu-a"]},
              "objectives": {"latency_ms": 50},
              "policies": [],
          }
          r1 = engine.evaluate(intent_id="test-id", resolved_intent=intent)
          r2 = engine.evaluate(intent_id="test-id", resolved_intent=intent)
          assert r1["overall_result"] == r2["overall_result"]
          assert len(r1["policy_results"]) == len(r2["policy_results"])

      def test_dry_run_flag_is_returned(self, engine: PolicyEngine) -> None:
          """ANIF-302 §10: dry_run response must include dry_run: true."""
          intent = {
              "service": "svc",
              "constraints": {"region": "EU", "encryption": True, "allowed_zones": ["eu-a"]},
              "objectives": {"latency_ms": 50},
              "policies": [],
          }
          result = engine.evaluate(intent_id="test-id", resolved_intent=intent, dry_run=True)
          assert result["dry_run"] is True

      def test_all_four_builtin_policies_always_evaluated(self, engine: PolicyEngine) -> None:
          """ANIF-302 §11.2: all 4 built-in policies active for every evaluation."""
          intent = {
              "service": "svc",
              "constraints": {"region": "EU", "encryption": True, "allowed_zones": ["eu-a"]},
              "objectives": {"latency_ms": 50},
              "policies": [],
          }
          result = engine.evaluate(intent_id="test-id", resolved_intent=intent)
          evaluated_names = {r["policy_name"] for r in result["policy_results"]}
          assert "zero_trust" in evaluated_names
          assert "no_public_ingress" in evaluated_names
          assert "pci_compliant" in evaluated_names
          assert "data_residency" in evaluated_names
  ```

  Create `tests/unit/test_conflict_resolver.py`:

  ```python
  """Tests for ConflictDetector and ConflictResolver — ANIF-303."""

  from anif_platform.policy.conflict import ConflictResolver


  class TestPrecedenceHierarchy:
      def test_compliance_beats_performance(self) -> None:
          policy_results = [
              {"policy_name": "pci_compliant", "category": "compliance", "decision": "deny",
               "triggered_rule": "constraints.encryption:equals:false", "reason": "needs encryption"},
              {"policy_name": "perf_opt", "category": "performance", "decision": "allow",
               "triggered_rule": "no rule matched", "reason": ""},
          ]
          resolver = ConflictResolver()
          conflicts, resolved = resolver.resolve(policy_results)
          assert len(conflicts) == 1
          assert conflicts[0]["winner"] == "pci_compliant"
          assert conflicts[0]["resolution_type"] == "precedence_hierarchy"

      def test_compliance_beats_security(self) -> None:
          policy_results = [
              {"policy_name": "data_residency", "category": "compliance", "decision": "deny",
               "triggered_rule": "constraints.region:not_in_list:[EU]", "reason": "region"},
              {"policy_name": "no_public_ingress", "category": "security", "decision": "allow",
               "triggered_rule": "no rule matched", "reason": ""},
          ]
          resolver = ConflictResolver()
          conflicts, _ = resolver.resolve(policy_results)
          assert conflicts[0]["winner"] == "data_residency"

      def test_equal_precedence_conflict_is_escalated(self) -> None:
          """ANIF-303 §6.2: equal-precedence conflict MUST escalate."""
          policy_results = [
              {"policy_name": "policy_a", "category": "security", "decision": "deny",
               "triggered_rule": "x:equals:y", "reason": ""},
              {"policy_name": "policy_b", "category": "security", "decision": "allow",
               "triggered_rule": "no rule matched", "reason": ""},
          ]
          resolver = ConflictResolver()
          conflicts, _ = resolver.resolve(policy_results)
          assert conflicts[0]["resolution_type"] == "escalated"
          assert conflicts[0]["winner"] is None

      def test_warn_not_upgraded_to_deny(self) -> None:
          """ANIF-303 §10.9: warn MUST NOT be upgraded to deny."""
          policy_results = [
              {"policy_name": "pol_a", "category": "compliance", "decision": "warn",
               "triggered_rule": "x:equals:y", "reason": ""},
              {"policy_name": "pol_b", "category": "performance", "decision": "allow",
               "triggered_rule": "no rule matched", "reason": ""},
          ]
          resolver = ConflictResolver()
          conflicts, resolved = resolver.resolve(policy_results)
          final_decisions = {r["policy_name"]: r["final_decision"] for r in resolved}
          assert final_decisions["pol_a"] != "deny"

      def test_no_conflict_when_decisions_agree(self) -> None:
          policy_results = [
              {"policy_name": "pol_a", "category": "compliance", "decision": "allow",
               "triggered_rule": "no rule matched", "reason": ""},
              {"policy_name": "pol_b", "category": "security", "decision": "allow",
               "triggered_rule": "no rule matched", "reason": ""},
          ]
          resolver = ConflictResolver()
          conflicts, _ = resolver.resolve(policy_results)
          assert conflicts == []

      def test_all_pairs_checked(self) -> None:
          """ANIF-303 §4.3: all n*(n-1)/2 pairs MUST be checked."""
          policy_results = [
              {"policy_name": f"pol_{i}", "category": "security",
               "decision": "deny" if i == 0 else "allow",
               "triggered_rule": "x:equals:y", "reason": ""}
              for i in range(4)
          ]
          resolver = ConflictResolver()
          conflicts, _ = resolver.resolve(policy_results)
          # pol_0 (deny) conflicts with pol_1, pol_2, pol_3 (allow) — 3 conflicts
          assert len(conflicts) == 3
  ```

- [ ] **Step 2: Verify tests fail**

  ```bash
  .venv/bin/pytest tests/unit/test_policy_engine.py tests/unit/test_conflict_resolver.py -v 2>&1 | head -15
  ```

- [ ] **Step 3: Create `src/anif_platform/policy/conflict.py`**

  ```python
  """ConflictDetector and ConflictResolver — ANIF-303."""

  from __future__ import annotations

  from typing import Any
  from uuid import uuid4

  # Precedence hierarchy — normative, MUST NOT be configurable (ANIF-303 §5)
  _PRECEDENCE: dict[str, int] = {
      "compliance": 1,
      "security": 2,
      "availability": 3,
      "performance": 4,
  }


  def _decisions_conflict(d_a: str, d_b: str) -> bool:
      """Two decisions conflict if they are not equal and at least one is deny or one is warn."""
      if d_a == d_b:
          return False
      # deny vs allow or warn
      if "deny" in (d_a, d_b):
          return True
      # warn vs allow
      if set((d_a, d_b)) == {"warn", "allow"}:
          return True
      return False


  class ConflictResolver:
      """
      Detects and resolves policy conflicts — ANIF-303.

      Detection is exhaustive: all n*(n-1)/2 pairs are checked.
      Resolution applies the precedence hierarchy.
      Equal-precedence conflicts are escalated.
      """

      def resolve(
          self, policy_results: list[dict[str, Any]]
      ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
          """
          Detect conflicts and produce the resolved policy set.

          Returns:
              (conflicts, resolved_policy_set)
              conflicts: list of conflict records
              resolved_policy_set: one entry per policy with final_decision
          """
          conflicts: list[dict[str, Any]] = []
          # Track overridden policies (loser in a resolved conflict)
          overridden: set[str] = set()

          n = len(policy_results)
          for i in range(n):
              for j in range(i + 1, n):
                  a = policy_results[i]
                  b = policy_results[j]
                  if not _decisions_conflict(a["decision"], b["decision"]):
                      continue

                  cat_a = a.get("category", "performance")
                  cat_b = b.get("category", "performance")
                  rank_a = _PRECEDENCE.get(cat_a, 99)
                  rank_b = _PRECEDENCE.get(cat_b, 99)

                  if rank_a == rank_b:
                      # Equal-precedence — escalate (ANIF-303 §6.2)
                      conflict: dict[str, Any] = {
                          "conflict_id": str(uuid4()),
                          "policies": [a["policy_name"], b["policy_name"]],
                          "constraint": a.get("triggered_rule", ""),
                          "decision_a": a["decision"],
                          "decision_b": b["decision"],
                          "winner": None,
                          "loser": None,
                          "resolution_rationale": (
                              f"Both policies are category '{cat_a}'; "
                              "equal-precedence conflict cannot be resolved by hierarchy"
                          ),
                          "resolution_type": "escalated",
                          "escalation_ticket_id": str(uuid4()),
                      }
                  else:
                      # Higher precedence wins (lower rank number = higher precedence)
                      if rank_a < rank_b:
                          winner, loser = a, b
                      else:
                          winner, loser = b, a

                      # warn is NEVER upgraded to deny (ANIF-303 §6.3)
                      winning_decision = winner["decision"]
                      if winning_decision == "deny" and loser["decision"] == "warn":
                          winning_decision = "warn"

                      overridden.add(loser["policy_name"])
                      conflict = {
                          "conflict_id": str(uuid4()),
                          "policies": [a["policy_name"], b["policy_name"]],
                          "constraint": a.get("triggered_rule", ""),
                          "decision_a": a["decision"],
                          "decision_b": b["decision"],
                          "winner": winner["policy_name"],
                          "loser": loser["policy_name"],
                          "resolution_rationale": (
                              f"{winner['policy_name']} ({winner.get('category', '?')}, "
                              f"rank {_PRECEDENCE.get(winner.get('category', ''), 99)}) "
                              f"overrides {loser['policy_name']} "
                              f"({loser.get('category', '?')}, "
                              f"rank {_PRECEDENCE.get(loser.get('category', ''), 99)}) "
                              "per precedence hierarchy"
                          ),
                          "resolution_type": "precedence_hierarchy",
                      }

                  conflicts.append(conflict)

          # Build resolved policy set — one entry per policy, excluding overridden losers
          resolved: list[dict[str, Any]] = []
          for pr in policy_results:
              name = pr["policy_name"]
              if name in overridden:
                  continue
              resolved.append({"policy_name": name, "final_decision": pr["decision"]})

          return conflicts, resolved
  ```

- [ ] **Step 4: Create `src/anif_platform/policy/engine.py`**

  ```python
  """PolicyEngine — 100% deterministic policy evaluation — ANIF-302."""

  from __future__ import annotations

  import os
  from datetime import UTC, datetime
  from typing import Any
  from uuid import uuid4

  from anif_platform.policy.condition import ConditionEvaluator
  from anif_platform.policy.conflict import ConflictResolver
  from anif_platform.policy.loader import PolicyLoader

  # Built-in policies that MUST always be active (ANIF-302 §11.2)
  _BUILTIN_POLICY_NAMES = {"zero_trust", "no_public_ingress", "pci_compliant", "data_residency"}

  # Additional zero_trust logic not expressible in grammar v0.1 (ANIF-302 §7.1)
  _ZERO_TRUST_REQUIRED_FIELDS = [
      "constraints.encryption",
      "constraints.region",
      "constraints.allowed_zones",
  ]


  class PolicyEngine:
      """
      Evaluates all active policies against an intent — ANIF-302.

      Evaluation is 100% deterministic: same inputs always produce same outputs.
      All four built-in policies are always included.
      Custom policies load from the policies/ directory.
      """

      def __init__(self, loader: PolicyLoader) -> None:
          self._policies = loader.load_all()
          self._resolver = ConflictResolver()

      def evaluate(
          self,
          intent_id: str,
          resolved_intent: dict[str, Any],
          dry_run: bool = False,
      ) -> dict[str, Any]:
          """
          Evaluate all active policies against a resolved intent.

          Returns the full evaluation result conforming to ANIF-302 §9.
          dry_run=True: no audit records written, evaluation_id is ephemeral.
          """
          # Active policy set = all loaded policies (built-ins + custom)
          policy_results: list[dict[str, Any]] = []

          for name, policy in sorted(self._policies.items()):
              result = self._evaluate_single(name, policy, resolved_intent)
              policy_results.append(result)

          # Additional zero_trust logic — ANIF-302 §7.1
          if "zero_trust" in self._policies:
              zt_result = self._evaluate_zero_trust_extra(resolved_intent, policy_results)
              if zt_result is not None:
                  # Replace the existing zero_trust result
                  policy_results = [
                      zt_result if r["policy_name"] == "zero_trust" else r
                      for r in policy_results
                  ]

          # Additional no_public_ingress logic — ANIF-302 §7.2
          if "no_public_ingress" in self._policies:
              npi_result = self._evaluate_no_public_ingress_extra(resolved_intent, policy_results)
              if npi_result is not None:
                  policy_results = [
                      npi_result if r["policy_name"] == "no_public_ingress" else r
                      for r in policy_results
                  ]

          # Conflict detection and resolution — ANIF-303
          conflicts, resolved_set = self._resolver.resolve(policy_results)

          # Determine overall_result
          decisions = [r["decision"] for r in policy_results]
          if "deny" in decisions:
              overall_result = "fail"
          elif "warn" in decisions:
              overall_result = "warn"
          else:
              overall_result = "pass"

          return {
              "intent_id": intent_id,
              "evaluation_id": str(uuid4()),
              "overall_result": overall_result,
              "policy_results": policy_results,
              "conflicts": conflicts,
              "resolved_policy_set": resolved_set,
              "evaluated_at": datetime.now(UTC).isoformat(),
              "dry_run": dry_run,
          }

      def _evaluate_single(
          self, name: str, policy: dict[str, Any], intent: dict[str, Any]
      ) -> dict[str, Any]:
          """Evaluate one policy: first matching rule wins; no match = allow."""
          category = policy.get("category", "performance")
          for rule in policy.get("rules", []):
              condition = rule.get("condition", "")
              action = rule.get("action", "allow")
              reason = rule.get("reason", "")
              try:
                  if ConditionEvaluator.evaluate(condition, intent):
                      return {
                          "policy_name": name,
                          "category": category,
                          "decision": action,
                          "triggered_rule": condition,
                          "reason": reason,
                      }
              except Exception:
                  # Malformed condition treated as non-matching (safe default)
                  continue

          return {
              "policy_name": name,
              "category": category,
              "decision": "allow",
              "triggered_rule": "no rule matched",
              "reason": f"All rules evaluated; no condition matched for {name}",
          }

      @staticmethod
      def _evaluate_zero_trust_extra(
          intent: dict[str, Any], current_results: list[dict[str, Any]]
      ) -> dict[str, Any] | None:
          """
          Additional zero_trust logic not expressible in grammar v0.1 — ANIF-302 §7.1.
          If allowed_zones is absent, produce deny.
          """
          constraints = intent.get("constraints") or {}
          if "allowed_zones" not in constraints:
              return {
                  "policy_name": "zero_trust",
                  "category": "security",
                  "decision": "deny",
                  "triggered_rule": "constraints.allowed_zones:absent",
                  "reason": "zero_trust: allowed_zones must be explicitly declared",
              }
          return None

      @staticmethod
      def _evaluate_no_public_ingress_extra(
          intent: dict[str, Any], current_results: list[dict[str, Any]]
      ) -> dict[str, Any] | None:
          """
          Additional no_public_ingress logic — ANIF-302 §7.2.
          If allowed_zones is entirely absent, produce deny.
          """
          constraints = intent.get("constraints") or {}
          if "allowed_zones" not in constraints:
              return {
                  "policy_name": "no_public_ingress",
                  "category": "security",
                  "decision": "deny",
                  "triggered_rule": "constraints.allowed_zones:absent",
                  "reason": "Public ingress is prohibited; at least one allowed zone must be specified",
              }
          return None
  ```

- [ ] **Step 5: Verify tests pass**

  ```bash
  .venv/bin/pytest tests/unit/test_policy_engine.py tests/unit/test_conflict_resolver.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 6: Commit**

  ```bash
  git add src/anif_platform/policy/conflict.py src/anif_platform/policy/engine.py \
    tests/unit/test_policy_engine.py tests/unit/test_conflict_resolver.py
  git commit -m "feat: implement PolicyEngine and ConflictResolver (ANIF-302, ANIF-303)"
  ```

---

## Task 10: Intent + Policy FastAPI Routers

**Files:**
- Create: `src/anif_platform/intent/router.py`
- Create: `src/anif_platform/policy/router.py`
- Modify: `src/anif_platform/intent/__init__.py`
- Modify: `src/anif_platform/policy/__init__.py`

- [ ] **Step 1: Create `src/anif_platform/intent/router.py`**

  ```python
  """FastAPI router for Intent Engine endpoints — ANIF-301."""

  from __future__ import annotations

  import uuid
  from typing import Any

  from fastapi import APIRouter, Depends, HTTPException, status
  from pydantic import BaseModel

  from anif_platform.auth import get_api_key
  from anif_platform.audit.writer import AuditWriter
  from anif_platform.intent.registry import IntentRegistry
  from anif_platform.intent.schemas import GitIntentRef, ValidatedIntent, ValidationResult
  from anif_platform.intent.validator import IntentValidator
  from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage
  from anif_platform.schemas.intent import Intent

  router = APIRouter(prefix="/intent", tags=["intent"])


  def get_intent_registry() -> IntentRegistry:
      raise NotImplementedError("Provide IntentRegistry via dependency injection")


  def get_audit_writer() -> AuditWriter:
      raise NotImplementedError("Provide AuditWriter via dependency injection")


  class ValidateIntentRequest(BaseModel):
      intent: dict[str, Any]
      git_ref: GitIntentRef | None = None


  @router.post("/validate-intent", response_model=ValidationResult)
  async def validate_intent(
      request: ValidateIntentRequest,
      registry: IntentRegistry = Depends(get_intent_registry),
      writer: AuditWriter = Depends(get_audit_writer),
      _: str = Depends(get_api_key),
  ) -> ValidationResult:
      """
      Validate an intent document and assign an intent_id if valid.

      Applies defaults, runs VAL-001–VAL-007, writes audit record,
      registers in the intents table if valid.
      — ANIF-301 §8
      """
      import time
      start = time.monotonic()

      try:
          intent_obj = Intent(**request.intent)
      except Exception as exc:
          return ValidationResult(
              status="validation_failed",
              errors=[str(exc)],
          )

      validator = IntentValidator()
      result = validator.validate(intent_obj)

      duration_ms = int((time.monotonic() - start) * 1000)
      outcome = AuditOutcome.success if result.intent_id else AuditOutcome.blocked

      # Write audit record before returning — ANIF-107 §4.3
      record = AuditRecord(
          intent_id=result.intent_id or uuid.uuid4(),
          stage=AuditStage.validate,
          input_summary={"service": request.intent.get("service"), "environment": request.intent.get("environment")},
          output_summary={"status": result.status, "error_count": len(result.errors)},
          outcome=outcome,
          duration_ms=duration_ms,
      )
      await writer.write(record)

      if result.intent_id:
          await registry.register(result, request.git_ref)

      return result


  @router.get("/intent/{intent_id}", response_model=ValidatedIntent)
  async def get_intent(
      intent_id: uuid.UUID,
      registry: IntentRegistry = Depends(get_intent_registry),
      _: str = Depends(get_api_key),
  ) -> ValidatedIntent:
      """Return a registered intent by ID."""
      intent = await registry.get(intent_id)
      if intent is None:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intent not found")
      return intent
  ```

- [ ] **Step 2: Create `src/anif_platform/policy/router.py`**

  ```python
  """FastAPI router for Policy Engine endpoints — ANIF-302."""

  from __future__ import annotations

  import time
  import uuid
  from typing import Any

  from fastapi import APIRouter, Depends
  from pydantic import BaseModel

  from anif_platform.auth import get_api_key
  from anif_platform.audit.writer import AuditWriter
  from anif_platform.intent.registry import IntentRegistry
  from anif_platform.policy.engine import PolicyEngine
  from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage

  router = APIRouter(tags=["policy"])


  def get_policy_engine() -> PolicyEngine:
      raise NotImplementedError("Provide PolicyEngine via dependency injection")


  def get_intent_registry() -> IntentRegistry:
      raise NotImplementedError("Provide IntentRegistry via dependency injection")


  def get_audit_writer() -> AuditWriter:
      raise NotImplementedError("Provide AuditWriter via dependency injection")


  class EvaluatePolicyRequest(BaseModel):
      intent_id: uuid.UUID
      dry_run: bool = False


  @router.post("/evaluate-policy", response_model=dict[str, Any])
  async def evaluate_policy(
      request: EvaluatePolicyRequest,
      engine: PolicyEngine = Depends(get_policy_engine),
      registry: IntentRegistry = Depends(get_intent_registry),
      writer: AuditWriter = Depends(get_audit_writer),
      _: str = Depends(get_api_key),
  ) -> dict[str, Any]:
      """
      Evaluate all active policies against a validated intent.

      Writes audit record unless dry_run=True (ANIF-302 §10).
      — ANIF-302 §9
      """
      start = time.monotonic()

      intent = await registry.get(request.intent_id)
      if intent is None:
          return {
              "error": f"Intent {request.intent_id} not found",
              "intent_id": str(request.intent_id),
          }

      result = engine.evaluate(
          intent_id=str(request.intent_id),
          resolved_intent=intent.resolved_intent,
          dry_run=request.dry_run,
      )

      duration_ms = int((time.monotonic() - start) * 1000)
      outcome = AuditOutcome.failure if result["overall_result"] == "fail" else AuditOutcome.success

      # Dry-run MUST NOT write audit records (ANIF-302 §10)
      if not request.dry_run:
          record = AuditRecord(
              intent_id=request.intent_id,
              stage=AuditStage.policy,
              input_summary={"intent_id": str(request.intent_id)},
              output_summary={
                  "overall_result": result["overall_result"],
                  "policy_count": len(result["policy_results"]),
                  "conflict_count": len(result["conflicts"]),
              },
              outcome=outcome,
              duration_ms=duration_ms,
              policies_evaluated=[r["policy_name"] for r in result["policy_results"]],
              policies_violated=[
                  r["policy_name"] for r in result["policy_results"] if r["decision"] == "deny"
              ],
          )
          await writer.write(record)

      return result
  ```

- [ ] **Step 3: Update `src/anif_platform/intent/__init__.py`**

  ```python
  """ANIF intent module."""

  from anif_platform.intent.registry import IntentRegistry
  from anif_platform.intent.validator import IntentValidator

  __all__ = ["IntentRegistry", "IntentValidator"]
  ```

- [ ] **Step 4: Update `src/anif_platform/policy/__init__.py`**

  ```python
  """ANIF policy module."""

  from anif_platform.policy.engine import PolicyEngine
  from anif_platform.policy.loader import PolicyLoader

  __all__ = ["PolicyEngine", "PolicyLoader"]
  ```

- [ ] **Step 5: Commit**

  ```bash
  git add src/anif_platform/intent/router.py src/anif_platform/policy/router.py \
    src/anif_platform/intent/__init__.py src/anif_platform/policy/__init__.py
  git commit -m "feat: add intent and policy FastAPI routers (ANIF-301, ANIF-302)"
  ```

---

## Task 11: GitWatcher (Polling + Webhook)

**Files:**
- Create: `src/anif_platform/intent/git_watcher.py`

The watcher detects new intent YAML files committed to a Git repo. Controlled by `GIT_WATCHER_MODE`.

- [ ] **Step 1: Create `src/anif_platform/intent/git_watcher.py`**

  ```python
  """
  GitWatcher — detects new intents committed to Git.

  Supports polling and webhook modes. Controlled by:
    GIT_WATCHER_MODE=polling|webhook|both
    GIT_WATCHER_POLL_INTERVAL=60  (seconds)
    GIT_REPO_URL=https://github.com/org/intents
    GIT_INTENTS_PATH=intents/
    GIT_ACCESS_TOKEN=ghp_xxxxx
  """

  from __future__ import annotations

  import asyncio
  import logging
  import os
  from typing import Any

  import httpx
  import yaml

  from anif_platform.intent.registry import IntentRegistry
  from anif_platform.intent.schemas import GitIntentRef
  from anif_platform.intent.validator import IntentValidator
  from anif_platform.schemas.intent import Intent

  log = logging.getLogger(__name__)


  class GitWatcher:
      """
      Watches a Git repository for new intent YAML files.

      On detection: fetches file, validates, registers in DB.
      """

      def __init__(self, registry: IntentRegistry) -> None:
          self._registry = registry
          self._validator = IntentValidator()
          self._last_commit: str | None = None
          self._repo_url = os.environ.get("GIT_REPO_URL", "")
          self._intents_path = os.environ.get("GIT_INTENTS_PATH", "intents/")
          self._token = os.environ.get("GIT_ACCESS_TOKEN", "")
          self._poll_interval = int(os.environ.get("GIT_WATCHER_POLL_INTERVAL", "60"))
          self._mode = os.environ.get("GIT_WATCHER_MODE", "polling")

      async def start(self) -> None:
          """Start the watcher. Runs polling loop if mode includes polling."""
          if self._mode in ("polling", "both"):
              asyncio.create_task(self._poll_loop())

      async def _poll_loop(self) -> None:
          """Poll the Git repo for new commits on an interval."""
          while True:
              try:
                  await self._check_for_new_intents()
              except Exception as exc:
                  log.error("git_watcher_poll_error", error=str(exc))
              await asyncio.sleep(self._poll_interval)

      async def _check_for_new_intents(self) -> None:
          """Fetch latest commit SHA and process any new intent files."""
          if not self._repo_url:
              return

          latest_sha = await self._get_latest_commit_sha()
          if latest_sha == self._last_commit:
              return

          files = await self._list_intent_files(latest_sha)
          for file_path in files:
              await self._process_intent_file(file_path, latest_sha)

          self._last_commit = latest_sha

      async def _get_latest_commit_sha(self) -> str:
          """Fetch the latest commit SHA from the Git API (GitHub format)."""
          # Converts https://github.com/org/repo → api.github.com/repos/org/repo/commits
          api_url = self._repo_url.replace(
              "https://github.com/", "https://api.github.com/repos/"
          ) + "/commits"
          headers = {"Accept": "application/vnd.github+json"}
          if self._token:
              headers["Authorization"] = f"Bearer {self._token}"
          async with httpx.AsyncClient() as client:
              resp = await client.get(api_url, headers=headers, params={"per_page": 1})
              resp.raise_for_status()
              data = resp.json()
              return data[0]["sha"]

      async def _list_intent_files(self, commit_sha: str) -> list[str]:
          """List all .yml files in the intents path at the given commit."""
          api_url = self._repo_url.replace(
              "https://github.com/", "https://api.github.com/repos/"
          ) + f"/contents/{self._intents_path}"
          headers = {"Accept": "application/vnd.github+json"}
          if self._token:
              headers["Authorization"] = f"Bearer {self._token}"
          async with httpx.AsyncClient() as client:
              resp = await client.get(api_url, headers=headers, params={"ref": commit_sha})
              if resp.status_code == 404:
                  return []
              resp.raise_for_status()
              return [
                  f["path"] for f in resp.json()
                  if f["name"].endswith(".yml") or f["name"].endswith(".yaml")
              ]

      async def _process_intent_file(self, file_path: str, commit_sha: str) -> None:
          """Fetch, parse, validate, and register one intent file."""
          raw_url = self._repo_url.replace(
              "https://github.com/", "https://raw.githubusercontent.com/"
          ) + f"/{commit_sha}/{file_path}"
          headers = {}
          if self._token:
              headers["Authorization"] = f"Bearer {self._token}"
          async with httpx.AsyncClient() as client:
              resp = await client.get(raw_url, headers=headers)
              resp.raise_for_status()
              raw_yaml = resp.text

          try:
              data = yaml.safe_load(raw_yaml)
              intent = Intent(**data)
          except Exception as exc:
              log.warning("git_watcher_parse_error", file=file_path, error=str(exc))
              return

          result = self._validator.validate(intent)
          if not result.intent_id:
              log.warning(
                  "git_watcher_validation_failed",
                  file=file_path,
                  errors=result.errors,
              )
              return

          git_ref = GitIntentRef(
              repo_url=self._repo_url,
              path=file_path,
              commit_sha=commit_sha,
          )
          await self._registry.register(result, git_ref)
          log.info(
              "git_watcher_intent_registered",
              intent_id=str(result.intent_id),
              file=file_path,
              commit_sha=commit_sha,
          )

      async def handle_webhook(self, payload: dict[str, Any]) -> None:
          """
          Process a push webhook payload (GitHub/GitLab format).

          Called from POST /webhooks/git endpoint when GIT_WATCHER_MODE
          includes 'webhook'.
          """
          # GitHub push event: payload["after"] = new commit SHA
          commit_sha = payload.get("after") or payload.get("checkout_sha", "")
          if not commit_sha or commit_sha == "0000000000000000000000000000000000000000":
              return  # Branch deletion — nothing to process

          files = await self._list_intent_files(commit_sha)
          for file_path in files:
              await self._process_intent_file(file_path, commit_sha)
  ```

- [ ] **Step 2: Commit**

  ```bash
  git add src/anif_platform/intent/git_watcher.py
  git commit -m "feat: add GitWatcher with polling and webhook support (configurable per environment)"
  ```

---

## Task 12: Orchestrator (End-to-End Pipeline with Stubs)

**Files:**
- Create: `src/anif_platform/pipeline/router.py`
- Modify: `src/anif_platform/pipeline/__init__.py`

The orchestrator chains all pipeline stages. Stages not yet built return a stub response. This gives a working end-to-end skeleton from day one.

- [ ] **Step 1: Create `src/anif_platform/pipeline/router.py`**

  ```python
  """
  Orchestrator — full pipeline skeleton with stubs for unbuilt stages.

  POST /orchestrate chains:
    validate → policy → [risk stub] → [decision stub] → [governance stub] → [execute stub]

  Stub stages return {"status": "not_yet_implemented", "stage": "<name>"}
  and are replaced when B3–B5 are built.
  """

  from __future__ import annotations

  import time
  import uuid
  from typing import Any

  from fastapi import APIRouter, Depends
  from pydantic import BaseModel

  from anif_platform.auth import get_api_key
  from anif_platform.audit.writer import AuditWriter
  from anif_platform.intent.registry import IntentRegistry
  from anif_platform.intent.schemas import GitIntentRef
  from anif_platform.intent.validator import IntentValidator
  from anif_platform.policy.engine import PolicyEngine
  from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage, ReasoningStep
  from anif_platform.schemas.intent import Intent

  router = APIRouter(tags=["pipeline"])


  def get_policy_engine() -> PolicyEngine:
      raise NotImplementedError("Provide PolicyEngine via dependency injection")


  def get_intent_registry() -> IntentRegistry:
      raise NotImplementedError("Provide IntentRegistry via dependency injection")


  def get_audit_writer() -> AuditWriter:
      raise NotImplementedError("Provide AuditWriter via dependency injection")


  class OrchestrateRequest(BaseModel):
      intent: dict[str, Any]
      git_ref: GitIntentRef | None = None
      dry_run: bool = False


  @router.post("/orchestrate", response_model=dict[str, Any])
  async def orchestrate(
      request: OrchestrateRequest,
      engine: PolicyEngine = Depends(get_policy_engine),
      registry: IntentRegistry = Depends(get_intent_registry),
      writer: AuditWriter = Depends(get_audit_writer),
      _: str = Depends(get_api_key),
  ) -> dict[str, Any]:
      """
      Run the full ANIF pipeline for an intent.

      Stages not yet built (risk, decision, governance, execute) return stubs.
      Governance checks are enforced even in stub form — the pipeline will not
      proceed past governance without a clearance record (ANIF-300 §5).
      """
      pipeline_result: dict[str, Any] = {}

      # ── Stage 1: Validate ────────────────────────────────────────────────
      start = time.monotonic()
      try:
          intent_obj = Intent(**request.intent)
      except Exception as exc:
          return {"status": "failed", "stage": "validate", "error": str(exc)}

      validator = IntentValidator()
      validation = validator.validate(intent_obj)

      intent_id = validation.intent_id or uuid.uuid4()
      duration_ms = int((time.monotonic() - start) * 1000)

      record = AuditRecord(
          intent_id=intent_id,
          stage=AuditStage.validate,
          input_summary={"service": request.intent.get("service")},
          output_summary={"status": validation.status},
          outcome=AuditOutcome.success if validation.intent_id else AuditOutcome.blocked,
          duration_ms=duration_ms,
      )
      await writer.write(record)

      if not validation.intent_id:
          return {
              "status": "failed",
              "stage": "validate",
              "errors": validation.errors,
              "warnings": validation.warnings,
          }

      await registry.register(validation, request.git_ref)
      pipeline_result["validate"] = {"status": "pass", "intent_id": str(intent_id)}

      # ── Stage 2: Policy Evaluation ───────────────────────────────────────
      start = time.monotonic()
      policy_result = engine.evaluate(
          intent_id=str(intent_id),
          resolved_intent=validation.validated_intent,  # type: ignore[arg-type]
          dry_run=request.dry_run,
      )
      duration_ms = int((time.monotonic() - start) * 1000)

      if not request.dry_run:
          policy_outcome = (
              AuditOutcome.failure
              if policy_result["overall_result"] == "fail"
              else AuditOutcome.success
          )
          await writer.write(AuditRecord(
              intent_id=intent_id,
              stage=AuditStage.policy,
              input_summary={"intent_id": str(intent_id)},
              output_summary={"overall_result": policy_result["overall_result"]},
              outcome=policy_outcome,
              duration_ms=duration_ms,
              policies_evaluated=[r["policy_name"] for r in policy_result["policy_results"]],
              policies_violated=[
                  r["policy_name"] for r in policy_result["policy_results"]
                  if r["decision"] == "deny"
              ],
          ))

      if policy_result["overall_result"] == "fail":
          return {
              "status": "failed",
              "stage": "policy",
              "intent_id": str(intent_id),
              "policy_result": policy_result,
          }

      pipeline_result["policy"] = policy_result

      # ── Stage 3: Risk Scoring (STUB — implemented in B3) ─────────────────
      pipeline_result["risk"] = {
          "status": "not_yet_implemented",
          "stage": "risk",
          "message": "RiskScorer will be implemented in B3",
      }

      # ── Stage 4: Decision Engine (STUB — implemented in B3) ──────────────
      pipeline_result["decision"] = {
          "status": "not_yet_implemented",
          "stage": "decision",
          "message": "DecisionEngine will be implemented in B3",
      }

      # ── Stage 5: Governance Gate (STUB — implemented in B4) ──────────────
      pipeline_result["governance"] = {
          "status": "not_yet_implemented",
          "stage": "governance",
          "message": "GovernanceGate will be implemented in B4",
      }

      # ── Stage 6: Execute (STUB — implemented in B5) ──────────────────────
      pipeline_result["execute"] = {
          "status": "not_yet_implemented",
          "stage": "execute",
          "message": "ActionExecutor will be implemented in B5",
      }

      return {
          "status": "pipeline_complete",
          "intent_id": str(intent_id),
          "stages": pipeline_result,
          "dry_run": request.dry_run,
      }
  ```

- [ ] **Step 2: Update `src/anif_platform/pipeline/__init__.py`**

  ```python
  """ANIF pipeline module."""
  ```

- [ ] **Step 3: Commit**

  ```bash
  git add src/anif_platform/pipeline/router.py src/anif_platform/pipeline/__init__.py
  git commit -m "feat: add orchestrator with end-to-end pipeline skeleton and stubs (ANIF-300 §5)"
  ```

---

## Task 13: Wire Everything into main.py

**Files:**
- Modify: `src/anif_platform/main.py`

All routers, dependency overrides, and the GitWatcher lifespan go here.

- [ ] **Step 1: Replace `src/anif_platform/main.py`**

  ```python
  """FastAPI application — ANIF Platform."""

  from __future__ import annotations

  import os
  from collections.abc import AsyncGenerator
  from contextlib import asynccontextmanager
  from typing import Any

  import structlog
  from fastapi import APIRouter, Depends, FastAPI, Request

  from anif_platform.audit.query import AuditQueryService
  from anif_platform.audit.router import get_audit_query_service
  from anif_platform.audit.router import router as audit_router
  from anif_platform.audit.writer import AuditWriter
  from anif_platform.auth import get_api_key
  from anif_platform.database import async_session_factory, engine
  from anif_platform.intent.git_watcher import GitWatcher
  from anif_platform.intent.registry import IntentRegistry
  from anif_platform.intent.router import get_audit_writer as intent_get_writer
  from anif_platform.intent.router import get_intent_registry as intent_get_registry
  from anif_platform.intent.router import router as intent_router
  from anif_platform.pipeline.router import get_audit_writer as pipeline_get_writer
  from anif_platform.pipeline.router import get_intent_registry as pipeline_get_registry
  from anif_platform.pipeline.router import get_policy_engine as pipeline_get_engine
  from anif_platform.pipeline.router import router as pipeline_router
  from anif_platform.policy.engine import PolicyEngine
  from anif_platform.policy.loader import PolicyLoader
  from anif_platform.policy.router import get_audit_writer as policy_get_writer
  from anif_platform.policy.router import get_intent_registry as policy_get_registry
  from anif_platform.policy.router import get_policy_engine as policy_get_engine
  from anif_platform.policy.router import router as policy_router

  log = structlog.get_logger(__name__)

  # Module-level singletons are acceptable here as this is the app entry point.
  # All other modules use dependency injection.
  _policy_engine: PolicyEngine | None = None


  def _get_policy_engine() -> PolicyEngine:
      global _policy_engine
      if _policy_engine is None:
          policies_dir = os.environ.get("POLICIES_DIR", "policies")
          _policy_engine = PolicyEngine(PolicyLoader(policies_dir))
      return _policy_engine


  @asynccontextmanager
  async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
      log.info("anif_platform_starting")

      # Start GitWatcher if configured
      mode = os.environ.get("GIT_WATCHER_MODE", "")
      if mode:
          async with async_session_factory() as session:
              registry = IntentRegistry(session)
              watcher = GitWatcher(registry)
              await watcher.start()
              log.info("git_watcher_started", mode=mode)

      yield

      await engine.dispose()
      log.info("anif_platform_stopped")


  app = FastAPI(
      title="ANIF Platform",
      description="Autonomous Networking & Infrastructure Framework",
      version="0.1.0",
      lifespan=lifespan,
  )


  # ── Per-request dependency factories ─────────────────────────────────────

  async def _get_session_writer(request: Request) -> AuditWriter:
      async with async_session_factory() as session:
          yield AuditWriter(session)  # type: ignore[misc]


  async def _get_session_registry(request: Request) -> IntentRegistry:
      async with async_session_factory() as session:
          yield IntentRegistry(session)  # type: ignore[misc]


  async def _get_session_query(request: Request) -> AuditQueryService:
      async with async_session_factory() as session:
          yield AuditQueryService(session)  # type: ignore[misc]


  # ── Dependency overrides ──────────────────────────────────────────────────

  app.dependency_overrides[get_audit_query_service] = _get_session_query
  app.dependency_overrides[intent_get_writer] = _get_session_writer
  app.dependency_overrides[intent_get_registry] = _get_session_registry
  app.dependency_overrides[policy_get_writer] = _get_session_writer
  app.dependency_overrides[policy_get_registry] = _get_session_registry
  app.dependency_overrides[policy_get_engine] = _get_policy_engine
  app.dependency_overrides[pipeline_get_writer] = _get_session_writer
  app.dependency_overrides[pipeline_get_registry] = _get_session_registry
  app.dependency_overrides[pipeline_get_engine] = _get_policy_engine


  # ── Webhook endpoint (when GIT_WATCHER_MODE includes webhook) ────────────

  webhook_router = APIRouter(tags=["webhooks"])


  @webhook_router.post("/webhooks/git")
  async def git_webhook(
      request: Request,
      _: str = Depends(get_api_key),
  ) -> dict[str, Any]:
      """Receive Git push webhooks and trigger intent detection."""
      payload = await request.json()
      async with async_session_factory() as session:
          registry = IntentRegistry(session)
          watcher = GitWatcher(registry)
          await watcher.handle_webhook(payload)
      return {"status": "accepted"}


  # ── Mount routers ─────────────────────────────────────────────────────────

  app.include_router(audit_router)
  app.include_router(intent_router)
  app.include_router(policy_router)
  app.include_router(pipeline_router)
  app.include_router(webhook_router)
  ```

- [ ] **Step 2: Verify app starts**

  ```bash
  .venv/bin/python -c "from anif_platform.main import app; print('OK', len(app.routes), 'routes')"
  ```

  Expected: `OK` with route count printed.

- [ ] **Step 3: Commit**

  ```bash
  git add src/anif_platform/main.py
  git commit -m "feat: wire all B2 routers into FastAPI app with dependency injection and GitWatcher lifespan"
  ```

---

## Task 14: Integration Tests

**Files:**
- Create: `tests/integration/test_intent_endpoints.py`
- Create: `tests/integration/test_policy_endpoints.py`
- Modify: `tests/conftest.py` — add policy_engine and intent_registry fixtures

- [ ] **Step 1: Update `tests/conftest.py` — add B2 fixtures**

  Add these fixtures to the existing `tests/conftest.py`:

  ```python
  # Add to existing conftest.py

  import shutil
  from pathlib import Path

  import pytest_asyncio


  @pytest_asyncio.fixture
  async def intent_registry(db_session):
      from anif_platform.intent.registry import IntentRegistry
      return IntentRegistry(db_session)


  @pytest_asyncio.fixture
  def policy_engine(tmp_path):
      src = Path(__file__).parent.parent / "policies"
      dst = tmp_path / "policies"
      shutil.copytree(src, dst)
      from anif_platform.policy.engine import PolicyEngine
      from anif_platform.policy.loader import PolicyLoader
      return PolicyEngine(PolicyLoader(dst))


  @pytest_asyncio.fixture
  async def auth_client(db_session, policy_engine) -> AsyncGenerator[AsyncClient, None]:
      """Authenticated test client with real DB session."""
      import os
      os.environ["ANIF_API_KEY"] = "test-key"

      from anif_platform.main import app
      from anif_platform.audit.query import AuditQueryService
      from anif_platform.audit.writer import AuditWriter
      from anif_platform.intent.registry import IntentRegistry
      from anif_platform.audit.router import get_audit_query_service
      from anif_platform.intent.router import get_audit_writer as iaw
      from anif_platform.intent.router import get_intent_registry as iir
      from anif_platform.policy.router import get_audit_writer as paw
      from anif_platform.policy.router import get_intent_registry as pir
      from anif_platform.policy.router import get_policy_engine as ppe
      from anif_platform.pipeline.router import get_audit_writer as oaw
      from anif_platform.pipeline.router import get_intent_registry as oir
      from anif_platform.pipeline.router import get_policy_engine as ope

      app.dependency_overrides[get_audit_query_service] = lambda: AuditQueryService(db_session)
      app.dependency_overrides[iaw] = lambda: AuditWriter(db_session)
      app.dependency_overrides[iir] = lambda: IntentRegistry(db_session)
      app.dependency_overrides[paw] = lambda: AuditWriter(db_session)
      app.dependency_overrides[pir] = lambda: IntentRegistry(db_session)
      app.dependency_overrides[ppe] = lambda: policy_engine
      app.dependency_overrides[oaw] = lambda: AuditWriter(db_session)
      app.dependency_overrides[oir] = lambda: IntentRegistry(db_session)
      app.dependency_overrides[ope] = lambda: policy_engine

      async with AsyncClient(
          transport=ASGITransport(app=app), base_url="http://test",
          headers={"X-API-Key": "test-key"},
      ) as c:
          yield c

      app.dependency_overrides.clear()
  ```

- [ ] **Step 2: Create `tests/integration/test_intent_endpoints.py`**

  ```python
  """Integration tests for Intent Engine endpoints — ANIF-301."""

  import pytest
  from httpx import AsyncClient


  VALID_PROD_INTENT = {
      "service": "payments-gateway",
      "environment": "prod",
      "objectives": {"latency_ms": 45, "availability_percent": 99.5},
      "constraints": {"region": "EU", "encryption": True, "allowed_zones": ["eu-a", "eu-b"]},
      "policies": ["pci_compliant"],
      "priority": "critical",
  }


  @pytest.mark.asyncio
  class TestValidateIntent:
      async def test_valid_intent_returns_intent_id(self, auth_client: AsyncClient) -> None:
          resp = await auth_client.post(
              "/intent/validate-intent", json={"intent": VALID_PROD_INTENT}
          )
          assert resp.status_code == 200
          body = resp.json()
          assert body["status"] == "validated"
          assert body["intent_id"] is not None

      async def test_invalid_intent_returns_errors(self, auth_client: AsyncClient) -> None:
          bad_intent = {
              "service": "svc",
              "environment": "prod",
              "objectives": {"latency_ms": 50},
              "constraints": {"region": "EU"},
              "priority": "low",
          }
          resp = await auth_client.post(
              "/intent/validate-intent", json={"intent": bad_intent}
          )
          assert resp.status_code == 200
          body = resp.json()
          assert body["status"] == "validation_failed"
          assert len(body["errors"]) > 0
          assert body["intent_id"] is None

      async def test_requires_api_key(self, client: AsyncClient) -> None:
          resp = await client.post(
              "/intent/validate-intent", json={"intent": VALID_PROD_INTENT}
          )
          assert resp.status_code == 401

      async def test_get_intent_after_validation(self, auth_client: AsyncClient) -> None:
          resp = await auth_client.post(
              "/intent/validate-intent", json={"intent": VALID_PROD_INTENT}
          )
          intent_id = resp.json()["intent_id"]

          get_resp = await auth_client.get(f"/intent/intent/{intent_id}")
          assert get_resp.status_code == 200
          assert get_resp.json()["intent_id"] == intent_id

      async def test_get_unknown_intent_returns_404(self, auth_client: AsyncClient) -> None:
          import uuid
          resp = await auth_client.get(f"/intent/intent/{uuid.uuid4()}")
          assert resp.status_code == 404
  ```

- [ ] **Step 3: Create `tests/integration/test_policy_endpoints.py`**

  ```python
  """Integration tests for Policy Engine endpoints — ANIF-302."""

  import pytest
  from httpx import AsyncClient


  VALID_INTENT = {
      "service": "payments",
      "environment": "prod",
      "objectives": {"latency_ms": 50, "availability_percent": 99.5},
      "constraints": {"region": "EU", "encryption": True, "allowed_zones": ["eu-a"]},
      "policies": [],
      "priority": "high",
  }


  @pytest.mark.asyncio
  class TestEvaluatePolicy:
      async def test_evaluate_policy_for_valid_intent(self, auth_client: AsyncClient) -> None:
          # First register an intent
          resp = await auth_client.post(
              "/intent/validate-intent", json={"intent": VALID_INTENT}
          )
          intent_id = resp.json()["intent_id"]

          # Then evaluate policy
          resp = await auth_client.post(
              "/evaluate-policy", json={"intent_id": intent_id}
          )
          assert resp.status_code == 200
          body = resp.json()
          assert body["overall_result"] in ("pass", "warn", "fail")
          assert body["evaluation_id"] is not None
          assert len(body["policy_results"]) >= 4  # all 4 built-ins

      async def test_dry_run_does_not_write_audit(self, auth_client: AsyncClient) -> None:
          """ANIF-302 §10: dry_run MUST NOT write audit records."""
          import uuid
          resp = await auth_client.post(
              "/intent/validate-intent", json={"intent": VALID_INTENT}
          )
          intent_id = resp.json()["intent_id"]

          # dry_run evaluation
          resp = await auth_client.post(
              "/evaluate-policy", json={"intent_id": intent_id, "dry_run": True}
          )
          assert resp.status_code == 200
          assert resp.json()["dry_run"] is True

          # Check no policy-stage audit record was written
          audit_resp = await auth_client.get(f"/audit/{intent_id}")
          stages = [r["stage"] for r in audit_resp.json()]
          assert "policy" not in stages

      async def test_orchestrate_returns_pipeline_result(self, auth_client: AsyncClient) -> None:
          resp = await auth_client.post(
              "/orchestrate", json={"intent": VALID_INTENT}
          )
          assert resp.status_code == 200
          body = resp.json()
          assert body["status"] == "pipeline_complete"
          assert "intent_id" in body
          assert body["stages"]["validate"]["status"] == "pass"
          assert body["stages"]["risk"]["status"] == "not_yet_implemented"
  ```

- [ ] **Step 4: Run all tests**

  ```bash
  .venv/bin/pytest -v
  ```

  Expected: all tests PASS.

- [ ] **Step 5: Run linting**

  ```bash
  .venv/bin/ruff check src/ tests/ --fix
  .venv/bin/black src/ tests/
  ```

- [ ] **Step 6: Commit**

  ```bash
  git add tests/integration/test_intent_endpoints.py tests/integration/test_policy_endpoints.py \
    tests/conftest.py
  git commit -m "feat: add B2 integration tests for intent and policy endpoints"
  ```

---

## Self-Review

### Spec coverage

| Requirement | Source | Task |
|---|---|---|
| VAL-001 latency warning | ANIF-301 §7.1 | 4 |
| VAL-002 availability range error | ANIF-301 §7.2 | Pydantic (B1) |
| VAL-003 prod requires high/critical priority | ANIF-301 §7.3 | 4 |
| VAL-004 pci_compliant requires encryption | ANIF-301 §7.4 | 4 |
| VAL-005 availability 99.99 requires 2 zones | ANIF-301 §7.5 | 4 |
| VAL-006 region enumeration | ANIF-301 §7.6 | Pydantic (B1) |
| VAL-007 policy name enumeration | ANIF-301 §7.7 | Pydantic (B1) |
| All validation rules evaluated, no short-circuit | ANIF-301 §10.4 | 4 |
| Defaults applied (environment=dev, priority=medium, policies=[]) | ANIF-301 §6 | 4 |
| Engine 100% deterministic | ANIF-302 §4 | 9 |
| All 4 built-in policies always active | ANIF-302 §11.2 | 6, 9 |
| Extensible — custom policies load from YAML | Design decision | 8 |
| Condition grammar all 8 operators | ANIF-302 §6.2 | 7 |
| Missing field behaviour per §6.3 | ANIF-302 §6.3 | 7 |
| dry_run MUST NOT write audit records | ANIF-302 §10 | 10 |
| Conflict detection exhaustive (all pairs) | ANIF-303 §4.3 | 9 |
| Precedence hierarchy compliance>security>availability>performance | ANIF-303 §5 | 9 |
| Equal-precedence → manual_review escalation | ANIF-303 §6.2 | 9 |
| warn MUST NOT be upgraded to deny | ANIF-303 §10.9 | 9 |
| All conflict resolutions written to audit | ANIF-303 §9 | 10 (policy router) |
| intent_id assigned by framework, not author | ANIF-300 §4.4 | B1 Task 1 |
| Git is source of truth, webhook + polling detection | Design decision | 11 |
| API key auth on all endpoints | Design decision | 1 |
| End-to-end pipeline skeleton with stubs | Design decision | 12 |
| Audit write before each stage returns | ANIF-107 §4.3 | 10, 12 |
