# B5: Execution & Rollback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the four action executors (reroute_traffic, apply_qos, scale_bandwidth, isolate_segment), a mock network adapter, automatic rollback, the `/execute` and `/rollback/{intent_id}` HTTP endpoints, and replace the pipeline Stage 6 stub with live execution — completing B5 of the platform build order.

**Architecture:** `ActionExecutor` is the orchestration layer: it checks governance preconditions, calls the adapter, writes audit records, and triggers automatic rollback on failure. `MockNetworkAdapter` implements the `NetworkAdapter` protocol with deterministic simulated success rates (no real network calls). The executor and adapter are separated by a Protocol interface so future vendor adapters can be swapped in without touching executor logic. Execution records are stored in a new `execution_records` DB table so rollback can be called independently using only `intent_id`.

**Tech Stack:** FastAPI, SQLAlchemy 2 async, Alembic, Pydantic v2, structlog, pytest-asyncio, unittest.mock, Python `random` (seeded for deterministic tests)

---

## Context: AuditRecord constraints

Every `AuditRecord` with `stage=AuditStage.execute` or `stage=AuditStage.rollback` does NOT require a `reasoning_chain` (only `governance` and `decision` stages do). Always pass `duration_ms` (required, no default).

Governance preconditions (ANIF-306 §5):
- **Precondition A (auto):** `governance_result["mode"] == "auto"`
- **Precondition B (approved ticket):** `governance_result["mode"] == "manual_review"` AND a ticket with `status=approved` exists for this intent
- `isolate_segment` ALWAYS requires Precondition B — NEVER auto-executable

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `src/anif_platform/execution/__init__.py` | Create | Package marker |
| `src/anif_platform/execution/adapter.py` | Create | `NetworkAdapter` Protocol + `AdapterResponse` + `AdapterHealthStatus` |
| `src/anif_platform/execution/mock_adapter.py` | Create | `MockNetworkAdapter` — deterministic simulated success/failure |
| `src/anif_platform/execution/models.py` | Create | `ExecutionRecordRow` SQLAlchemy ORM |
| `src/anif_platform/execution/schemas.py` | Create | Pydantic request/response schemas for execute + rollback |
| `src/anif_platform/execution/executor.py` | Create | `ActionExecutor` — precondition check, execute, automatic rollback |
| `src/anif_platform/execution/router.py` | Create | `POST /execute`, `POST /rollback/{intent_id}` |
| `src/anif_platform/pipeline/router.py` | Modify | Replace Stage 6 stub with live executor call |
| `src/anif_platform/main.py` | Modify | Mount execution router + dependency overrides |
| `migrations/versions/004_add_execution_records.py` | Create | Alembic migration for `execution_records` table |
| `tests/unit/test_mock_adapter.py` | Create | Unit tests for MockNetworkAdapter |
| `tests/unit/test_action_executor.py` | Create | Unit tests for ActionExecutor |

---

## Task 1: NetworkAdapter Protocol + AdapterResponse schemas

**Files:**
- Create: `src/anif_platform/execution/__init__.py`
- Create: `src/anif_platform/execution/adapter.py`

- [ ] **Step 1: Write the failing import check**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  DATABASE_URL=postgresql+asyncpg://anif:anif_dev@localhost:5432/anif_dev \
  .venv/bin/python -c "from anif_platform.execution.adapter import NetworkAdapter" 2>&1 | head -3
```

Expected: `ModuleNotFoundError`

- [ ] **Step 2: Create `src/anif_platform/execution/__init__.py`**

```python
"""ANIF action execution module — ANIF-306."""
```

- [ ] **Step 3: Create `src/anif_platform/execution/adapter.py`**

```python
"""
NetworkAdapter Protocol and response schemas — ANIF-306 §7.

All adapters MUST implement NetworkAdapter.
The executor calls only this interface, never adapter internals.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from pydantic import BaseModel


class AdapterResponse(BaseModel):
    """Response from any adapter execute or rollback call — ANIF-306 §7.2."""

    success: bool
    adapter_status_code: int
    adapter_message: str
    applied_changes: list[str]
    rollback_reference: str | None


class AdapterHealthStatus(BaseModel):
    """Health status returned by adapter.health_check() — ANIF-306 §7.2."""

    healthy: bool
    adapter_name: str
    last_checked: datetime
    error: str | None


class NetworkAdapter(Protocol):
    """
    Abstract adapter interface — ANIF-306 §7.2.

    Every adapter MUST implement these three methods.
    The executor MUST call only this interface.
    """

    def execute(
        self,
        action_type: str,
        parameters: dict[str, Any],
        execution_id: str,
    ) -> AdapterResponse:
        """Execute an action and return the adapter response."""
        ...

    def rollback(
        self,
        action_type: str,
        rollback_reference: str | None,
        execution_id: str,
    ) -> AdapterResponse:
        """Reverse a previously applied action."""
        ...

    def health_check(self) -> AdapterHealthStatus:
        """Return the current health status of this adapter."""
        ...
```

- [ ] **Step 4: Verify import**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  DATABASE_URL=postgresql+asyncpg://anif:anif_dev@localhost:5432/anif_dev \
  .venv/bin/python -c "from anif_platform.execution.adapter import NetworkAdapter, AdapterResponse; print('OK')"
```

Expected: `OK`

- [ ] **Step 5: Lint**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  .venv/bin/ruff check --fix src/anif_platform/execution/adapter.py && \
  .venv/bin/black src/anif_platform/execution/adapter.py
```

- [ ] **Step 6: Commit**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  git add src/anif_platform/execution/ && \
  git commit -m "feat: add NetworkAdapter Protocol and adapter response schemas (ANIF-306)"
```

---

## Task 2: MockNetworkAdapter

**Files:**
- Create: `src/anif_platform/execution/mock_adapter.py`
- Create: `tests/unit/test_mock_adapter.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/unit/test_mock_adapter.py`:

```python
"""Unit tests for MockNetworkAdapter — ANIF-306 §10."""

from __future__ import annotations

import random
import uuid

import pytest

from anif_platform.execution.mock_adapter import MockNetworkAdapter

ACTION_TYPES = ["reroute_traffic", "apply_qos", "scale_bandwidth", "isolate_segment"]


def make_params(action_type: str) -> dict:
    base = {"segment_id": "seg-001"}
    extras = {
        "reroute_traffic": {"source_segment": "seg-001", "target_segment": "seg-002", "routing_protocol": "BGP"},
        "apply_qos": {"policy_name": "latency-prio", "traffic_class": "DSCP_EF", "bandwidth_guarantee_mbps": 100},
        "scale_bandwidth": {"segment_id": "seg-001", "target_bandwidth_mbps": 500, "direction": "up"},
        "isolate_segment": {"segment_id": "seg-001", "isolation_reason": "fault", "blast_radius_assessment": "low"},
    }
    return extras.get(action_type, base)


class TestMockAdapterSuccessPath:
    def test_success_response_has_required_fields(self) -> None:
        """ANIF-306 §10.2: success response MUST have all required fields."""
        adapter = MockNetworkAdapter(seed=42, force_success=True)
        exec_id = str(uuid.uuid4())
        response = adapter.execute("apply_qos", make_params("apply_qos"), exec_id)
        assert response.success is True
        assert response.adapter_status_code == 200
        assert "apply_qos" in response.adapter_message
        assert len(response.applied_changes) > 0
        assert response.rollback_reference is not None
        assert exec_id in response.rollback_reference

    def test_success_rollback_reference_contains_execution_id(self) -> None:
        adapter = MockNetworkAdapter(seed=42, force_success=True)
        exec_id = str(uuid.uuid4())
        response = adapter.execute("reroute_traffic", make_params("reroute_traffic"), exec_id)
        assert response.rollback_reference == f"mock-rollback-{exec_id}"

    def test_success_applied_changes_mentions_action_type(self) -> None:
        adapter = MockNetworkAdapter(seed=42, force_success=True)
        exec_id = str(uuid.uuid4())
        response = adapter.execute("scale_bandwidth", make_params("scale_bandwidth"), exec_id)
        assert any("scale_bandwidth" in c for c in response.applied_changes)


class TestMockAdapterFailurePath:
    def test_failure_response_has_required_fields(self) -> None:
        """ANIF-306 §10.3: failure response MUST have required fields with success=false."""
        adapter = MockNetworkAdapter(seed=42, force_failure=True)
        exec_id = str(uuid.uuid4())
        response = adapter.execute("reroute_traffic", make_params("reroute_traffic"), exec_id)
        assert response.success is False
        assert response.applied_changes == []
        assert response.rollback_reference is None

    def test_failure_status_code_is_non_200(self) -> None:
        adapter = MockNetworkAdapter(seed=42, force_failure=True)
        response = adapter.execute("apply_qos", make_params("apply_qos"), str(uuid.uuid4()))
        assert response.adapter_status_code != 200

    def test_failure_message_mentions_action_type(self) -> None:
        adapter = MockNetworkAdapter(seed=42, force_failure=True)
        response = adapter.execute("isolate_segment", make_params("isolate_segment"), str(uuid.uuid4()))
        assert "isolate_segment" in response.adapter_message


class TestMockAdapterRollback:
    def test_rollback_with_non_null_reference_succeeds(self) -> None:
        """ANIF-306 §10.4: rollback succeeds 100% if rollback_reference is non-null."""
        adapter = MockNetworkAdapter(seed=42)
        response = adapter.rollback("apply_qos", "mock-rollback-abc123", str(uuid.uuid4()))
        assert response.success is True

    def test_rollback_with_null_reference_also_succeeds(self) -> None:
        """ANIF-306 §10.4: null reference means nothing to reverse — still success."""
        adapter = MockNetworkAdapter(seed=42)
        response = adapter.rollback("reroute_traffic", None, str(uuid.uuid4()))
        assert response.success is True
        assert response.applied_changes == []


class TestMockAdapterSuccessRates:
    def test_apply_qos_has_highest_success_rate(self) -> None:
        """ANIF-306 §10.1: apply_qos has 95% success rate — highest of four."""
        total = 200
        successes = sum(
            1
            for i in range(total)
            if MockNetworkAdapter(seed=i).execute("apply_qos", make_params("apply_qos"), str(uuid.uuid4())).success
        )
        # Allow generous margin: expect at least 85% in 200 runs
        assert successes / total >= 0.85

    def test_isolate_segment_has_lowest_success_rate(self) -> None:
        """ANIF-306 §10.1: isolate_segment has 80% success rate — lowest of four."""
        total = 200
        qos_successes = sum(
            1
            for i in range(total)
            if MockNetworkAdapter(seed=i).execute("apply_qos", make_params("apply_qos"), str(uuid.uuid4())).success
        )
        iso_successes = sum(
            1
            for i in range(total)
            if MockNetworkAdapter(seed=i).execute("isolate_segment", make_params("isolate_segment"), str(uuid.uuid4())).success
        )
        assert iso_successes <= qos_successes


class TestMockAdapterHealthCheck:
    def test_health_check_returns_healthy(self) -> None:
        adapter = MockNetworkAdapter(seed=42)
        status = adapter.health_check()
        assert status.healthy is True
        assert status.adapter_name == "mock"
        assert status.error is None
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  .venv/bin/pytest tests/unit/test_mock_adapter.py --tb=line -q 2>&1 | tail -5
```

Expected: `ImportError: No module named 'anif_platform.execution.mock_adapter'`

- [ ] **Step 3: Create `src/anif_platform/execution/mock_adapter.py`**

```python
"""
MockNetworkAdapter — deterministic simulated execution — ANIF-306 §10.

Uses a seeded random number generator so behaviour is reproducible in tests.
Pass force_success=True or force_failure=True to override probability.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime
from typing import Any

from anif_platform.execution.adapter import AdapterHealthStatus, AdapterResponse

# Mock success probabilities — ANIF-306 §10.1
_SUCCESS_RATES: dict[str, float] = {
    "reroute_traffic": 0.90,
    "apply_qos": 0.95,
    "scale_bandwidth": 0.85,
    "isolate_segment": 0.80,
}

# Failure status codes — ANIF-306 §10.1
_FAILURE_CODES: dict[str, int] = {
    "reroute_traffic": 503,
    "apply_qos": 422,
    "scale_bandwidth": 503,
    "isolate_segment": 500,
}


class MockNetworkAdapter:
    """
    Simulates action execution without making real network changes — ANIF-306 §10.

    Parameters
    ----------
    seed:
        Seed for the random number generator. Use a fixed seed in tests.
    force_success:
        If True, always return a success response regardless of probability.
    force_failure:
        If True, always return a failure response regardless of probability.
    """

    def __init__(
        self,
        seed: int | None = None,
        force_success: bool = False,
        force_failure: bool = False,
    ) -> None:
        self._rng = random.Random(seed)
        self._force_success = force_success
        self._force_failure = force_failure

    def execute(
        self,
        action_type: str,
        parameters: dict[str, Any],
        execution_id: str,
    ) -> AdapterResponse:
        """Simulate executing an action — ANIF-306 §10.2 / §10.3."""
        success_rate = _SUCCESS_RATES.get(action_type, 0.90)

        if self._force_success:
            success = True
        elif self._force_failure:
            success = False
        else:
            success = self._rng.random() < success_rate

        if success:
            segment_id = parameters.get("segment_id") or parameters.get("source_segment", "unknown")
            return AdapterResponse(
                success=True,
                adapter_status_code=200,
                adapter_message=f"Mock action applied: {action_type}",
                applied_changes=[f"Simulated change: {action_type} on segment {segment_id}"],
                rollback_reference=f"mock-rollback-{execution_id}",
            )

        return AdapterResponse(
            success=False,
            adapter_status_code=_FAILURE_CODES.get(action_type, 503),
            adapter_message=f"Mock adapter simulated failure for action: {action_type}",
            applied_changes=[],
            rollback_reference=None,
        )

    def rollback(
        self,
        action_type: str,
        rollback_reference: str | None,
        execution_id: str,
    ) -> AdapterResponse:
        """
        Simulate rollback — ANIF-306 §10.4.

        Succeeds 100% of the time. If rollback_reference is None,
        no changes were applied so there is nothing to reverse.
        """
        if rollback_reference is None:
            return AdapterResponse(
                success=True,
                adapter_status_code=200,
                adapter_message="No changes to reverse; original action did not apply.",
                applied_changes=[],
                rollback_reference=None,
            )

        return AdapterResponse(
            success=True,
            adapter_status_code=200,
            adapter_message=f"Mock rollback applied for: {action_type}",
            applied_changes=[f"Reversed: {action_type} (ref={rollback_reference})"],
            rollback_reference=None,
        )

    def health_check(self) -> AdapterHealthStatus:
        """Return healthy status — mock adapter is always healthy."""
        return AdapterHealthStatus(
            healthy=True,
            adapter_name="mock",
            last_checked=datetime.now(UTC),
            error=None,
        )
```

- [ ] **Step 4: Run tests**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  .venv/bin/pytest tests/unit/test_mock_adapter.py -v --tb=short 2>&1 | tail -20
```

Expected: all tests pass.

- [ ] **Step 5: Lint**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  .venv/bin/ruff check --fix src/anif_platform/execution/mock_adapter.py && \
  .venv/bin/black src/anif_platform/execution/mock_adapter.py
```

- [ ] **Step 6: Commit**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  git add src/anif_platform/execution/mock_adapter.py tests/unit/test_mock_adapter.py && \
  git commit -m "feat: implement MockNetworkAdapter with deterministic success rates (ANIF-306)"
```

---

## Task 3: ExecutionRecord SQLAlchemy model + Pydantic schemas

**Files:**
- Create: `src/anif_platform/execution/models.py`
- Create: `src/anif_platform/execution/schemas.py`

- [ ] **Step 1: Write the failing import check**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  DATABASE_URL=postgresql+asyncpg://anif:anif_dev@localhost:5432/anif_dev \
  .venv/bin/python -c "from anif_platform.execution.models import ExecutionRecordRow" 2>&1 | head -3
```

Expected: `ImportError`

- [ ] **Step 2: Create `src/anif_platform/execution/models.py`**

```python
"""ExecutionRecord SQLAlchemy ORM model — ANIF-306 §9."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from anif_platform.database import Base


class ExecutionRecordRow(Base):
    """
    Persisted execution record — ANIF-306 §9.

    Written before rollback is called so rollback() can be invoked
    independently using only intent_id (ANIF-306 §6.2).
    Append-only; never updated after creation (ANIF-306 §13).
    """

    __tablename__ = "execution_records"

    execution_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    intent_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    decision_id: Mapped[str] = mapped_column(String, nullable=False)
    action_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)  # success | failed | partial
    adapter_name: Mapped[str] = mapped_column(String, nullable=False, default="mock")
    adapter_status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    adapter_message: Mapped[str] = mapped_column(Text, nullable=False)
    applied_changes: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON list
    rollback_reference: Mapped[str | None] = mapped_column(String, nullable=True)
    rollback_available: Mapped[bool] = mapped_column(
        # SQLAlchemy Boolean stored as String for simplicity
        String, nullable=False, default="false"
    )
    rollback_status: Mapped[str | None] = mapped_column(String, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    parameters_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # JSON
```

- [ ] **Step 3: Create `src/anif_platform/execution/schemas.py`**

```python
"""Pydantic schemas for execution and rollback — ANIF-306 §9."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AdapterResponseSchema(BaseModel):
    """Embedded adapter response in execution result — ANIF-306 §9."""

    success: bool
    adapter_status_code: int
    adapter_message: str
    applied_changes: list[str]
    rollback_reference: str | None


class ExecuteRequest(BaseModel):
    """Request body for POST /execute — ANIF-306 §9."""

    intent_id: uuid.UUID
    decision_id: str
    action_type: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    governance_result: dict[str, Any]
    # ticket_id is required when governance_result.mode == manual_review
    ticket_id: str | None = None
    dry_run: bool = False


class ExecuteResponse(BaseModel):
    """Response from POST /execute — ANIF-306 §9."""

    execution_id: str
    intent_id: uuid.UUID
    decision_id: str
    action_type: str
    status: str  # success | failed | partial
    adapter_response: AdapterResponseSchema
    duration_ms: int
    rollback_available: bool
    rollback_status: str | None
    executed_at: datetime
    completed_at: datetime


class RollbackResponse(BaseModel):
    """Response from POST /rollback/{intent_id} — ANIF-306 §6.2."""

    intent_id: uuid.UUID
    execution_id: str
    action_type: str
    rollback_status: str  # success | failed
    adapter_response: AdapterResponseSchema
    duration_ms: int
    rolled_back_at: datetime
    audit_record_id: str
```

- [ ] **Step 4: Verify imports**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  DATABASE_URL=postgresql+asyncpg://anif:anif_dev@localhost:5432/anif_dev \
  .venv/bin/python -c "
from anif_platform.execution.models import ExecutionRecordRow
from anif_platform.execution.schemas import ExecuteRequest, ExecuteResponse, RollbackResponse
print('OK')
"
```

Expected: `OK`

- [ ] **Step 5: Lint**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  .venv/bin/ruff check --fix src/anif_platform/execution/models.py src/anif_platform/execution/schemas.py && \
  .venv/bin/black src/anif_platform/execution/models.py src/anif_platform/execution/schemas.py
```

- [ ] **Step 6: Commit**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  git add src/anif_platform/execution/ && \
  git commit -m "feat: add ExecutionRecord model and execution Pydantic schemas (ANIF-306)"
```

---

## Task 4: Alembic migration 004 — execution_records table

**Files:**
- Create: `migrations/versions/004_add_execution_records.py`

- [ ] **Step 1: Check the existing migration chain**

```bash
ls /home/dan/Desktop/github/auto_networking/.worktrees/scaffold/migrations/versions/
```

The previous migration is `003_add_approval_tickets.py` with `revision = "003"`.

- [ ] **Step 2: Check env.py imports**

```bash
cat /home/dan/Desktop/github/auto_networking/.worktrees/scaffold/migrations/env.py | head -30
```

`env.py` should already import `Base` and set `target_metadata = Base.metadata`. If `anif_platform.execution.models` is not imported there, add it.

- [ ] **Step 3: Create `migrations/versions/004_add_execution_records.py`**

```python
"""add_execution_records

Revision ID: 004
Revises: 003
Create Date: 2026-04-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "execution_records",
        sa.Column("execution_id", sa.String(), nullable=False),
        sa.Column("intent_id", sa.Uuid(), nullable=False),
        sa.Column("decision_id", sa.String(), nullable=False),
        sa.Column("action_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("adapter_name", sa.String(), nullable=False),
        sa.Column("adapter_status_code", sa.Integer(), nullable=False),
        sa.Column("adapter_message", sa.Text(), nullable=False),
        sa.Column("applied_changes", sa.Text(), nullable=False),
        sa.Column("rollback_reference", sa.String(), nullable=True),
        sa.Column("rollback_available", sa.String(), nullable=False),
        sa.Column("rollback_status", sa.String(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("parameters_json", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("execution_id"),
    )
    op.create_index("ix_execution_records_intent_id", "execution_records", ["intent_id"])
    op.create_index("ix_execution_records_status", "execution_records", ["status"])


def downgrade() -> None:
    op.drop_index("ix_execution_records_status", table_name="execution_records")
    op.drop_index("ix_execution_records_intent_id", table_name="execution_records")
    op.drop_table("execution_records")
```

- [ ] **Step 4: Verify the migration**

Read the file and confirm: `upgrade()` creates the table, `downgrade()` drops indexes before the table, `down_revision = "003"`.

- [ ] **Step 5: Add the model import to env.py if missing**

```bash
grep "execution.models" /home/dan/Desktop/github/auto_networking/.worktrees/scaffold/migrations/env.py
```

If nothing is returned, add this line after the other model imports in `env.py`:

```python
import anif_platform.execution.models  # noqa: F401 — registers ExecutionRecordRow with Base.metadata
```

- [ ] **Step 6: Commit**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  git add migrations/ && \
  git commit -m "feat: add Alembic migration 004 for execution_records (ANIF-306)"
```

---

## Task 5: ActionExecutor

**Files:**
- Create: `src/anif_platform/execution/executor.py`
- Create: `tests/unit/test_action_executor.py`

The executor is the heart of B5. It:
1. Verifies governance preconditions (ANIF-306 §5)
2. Calls the adapter
3. Writes audit records (EXECUTION_START, EXECUTION_SUCCESS/FAILED, ROLLBACK_*)
4. Persists the execution record to DB
5. Triggers automatic rollback on failure

- [ ] **Step 1: Write the failing tests**

Create `tests/unit/test_action_executor.py`:

```python
"""Unit tests for ActionExecutor — ANIF-306 §5, §6, §8."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from anif_platform.execution.adapter import AdapterResponse
from anif_platform.execution.executor import ActionExecutor, PreconditionError
from anif_platform.execution.mock_adapter import MockNetworkAdapter


def make_gov_auto() -> dict:
    return {"mode": "auto", "triggered_rule": "none", "rationale": "auto"}


def make_gov_manual_approved() -> dict:
    return {"mode": "manual_review", "triggered_rule": "R-02", "rationale": "review"}


def make_decision(action_type: str = "apply_qos") -> dict:
    return {
        "decision_id": str(uuid.uuid4()),
        "recommended_action": {"action_type": action_type, "parameters": {}, "risk_level": "low"},
        "rollback_plan": {"action_type": action_type, "description": "Rollback", "estimated_duration_ms": 2000},
    }


def make_params(action_type: str = "apply_qos") -> dict:
    params = {
        "reroute_traffic": {"source_segment": "s1", "target_segment": "s2", "routing_protocol": "BGP"},
        "apply_qos": {"policy_name": "prio", "traffic_class": "DSCP_EF", "bandwidth_guarantee_mbps": 100},
        "scale_bandwidth": {"segment_id": "seg-1", "target_bandwidth_mbps": 200, "direction": "up"},
        "isolate_segment": {"segment_id": "seg-1", "isolation_reason": "fault", "blast_radius_assessment": "low"},
    }
    return params.get(action_type, {})


def make_executor(
    force_success: bool = True,
    force_failure: bool = False,
) -> tuple[ActionExecutor, AsyncMock, AsyncMock]:
    adapter = MockNetworkAdapter(seed=42, force_success=force_success, force_failure=force_failure)
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    writer = AsyncMock()
    executor = ActionExecutor(adapter=adapter, session=session, writer=writer)
    return executor, session, writer


class TestGovernancePreconditions:
    @pytest.mark.asyncio
    async def test_auto_mode_permits_non_isolate_actions(self) -> None:
        """ANIF-306 §5: auto mode satisfies Precondition A for non-isolate actions."""
        executor, _, _ = make_executor()
        result = await executor.execute(
            intent_id=uuid.uuid4(),
            decision=make_decision("apply_qos"),
            parameters=make_params("apply_qos"),
            governance_result=make_gov_auto(),
            ticket_id=None,
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_isolate_segment_blocked_in_auto_mode(self) -> None:
        """ANIF-306 §5: isolate_segment MUST NOT execute under auto mode (Precondition A only)."""
        executor, _, _ = make_executor()
        with pytest.raises(PreconditionError, match="isolate_segment"):
            await executor.execute(
                intent_id=uuid.uuid4(),
                decision=make_decision("isolate_segment"),
                parameters=make_params("isolate_segment"),
                governance_result=make_gov_auto(),
                ticket_id=None,
            )

    @pytest.mark.asyncio
    async def test_isolate_segment_permitted_with_approved_ticket(self) -> None:
        """ANIF-306 §5: isolate_segment executes when Precondition B (approved ticket) is met."""
        executor, session, _ = make_executor()
        from anif_platform.human_loop.models import ApprovalTicketRow, TicketStatus
        ticket = ApprovalTicketRow()
        ticket.ticket_id = "t-001"
        ticket.status = TicketStatus.approved
        ticket.intent_id = uuid.uuid4()
        ticket.requested_by = "jsmith"
        ticket.decision_summary = "test"
        ticket.risk_score = 80
        ticket.required_approver_role = "senior_engineer"
        ticket.created_at = datetime.now(UTC)
        ticket.expires_at = datetime.now(UTC)
        session.get = AsyncMock(return_value=ticket)

        result = await executor.execute(
            intent_id=uuid.uuid4(),
            decision=make_decision("isolate_segment"),
            parameters=make_params("isolate_segment"),
            governance_result=make_gov_manual_approved(),
            ticket_id="t-001",
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_manual_review_without_ticket_id_raises(self) -> None:
        """ANIF-306 §5: manual_review mode requires ticket_id."""
        executor, _, _ = make_executor()
        with pytest.raises(PreconditionError, match="ticket_id"):
            await executor.execute(
                intent_id=uuid.uuid4(),
                decision=make_decision("apply_qos"),
                parameters=make_params("apply_qos"),
                governance_result=make_gov_manual_approved(),
                ticket_id=None,
            )

    @pytest.mark.asyncio
    async def test_manual_review_with_pending_ticket_raises(self) -> None:
        """ANIF-306 §5: Precondition B requires status=approved, not pending."""
        executor, session, _ = make_executor()
        from anif_platform.human_loop.models import ApprovalTicketRow, TicketStatus
        ticket = ApprovalTicketRow()
        ticket.ticket_id = "t-002"
        ticket.status = TicketStatus.pending
        ticket.intent_id = uuid.uuid4()
        ticket.requested_by = "jsmith"
        ticket.decision_summary = "test"
        ticket.risk_score = 80
        ticket.required_approver_role = "senior_engineer"
        ticket.created_at = datetime.now(UTC)
        ticket.expires_at = datetime.now(UTC)
        session.get = AsyncMock(return_value=ticket)

        with pytest.raises(PreconditionError, match="approved"):
            await executor.execute(
                intent_id=uuid.uuid4(),
                decision=make_decision("apply_qos"),
                parameters=make_params("apply_qos"),
                governance_result=make_gov_manual_approved(),
                ticket_id="t-002",
            )

    @pytest.mark.asyncio
    async def test_precondition_failure_writes_audit_record(self) -> None:
        """ANIF-306 §11: PRECONDITION_FAILED event MUST be written to audit."""
        executor, _, writer = make_executor()
        with pytest.raises(PreconditionError):
            await executor.execute(
                intent_id=uuid.uuid4(),
                decision=make_decision("isolate_segment"),
                parameters=make_params("isolate_segment"),
                governance_result=make_gov_auto(),
                ticket_id=None,
            )
        writer.write.assert_called_once()


class TestExecuteSuccess:
    @pytest.mark.asyncio
    async def test_success_returns_required_fields(self) -> None:
        """ANIF-306 §9: execution response MUST include all required fields."""
        executor, _, _ = make_executor(force_success=True)
        intent_id = uuid.uuid4()
        result = await executor.execute(
            intent_id=intent_id,
            decision=make_decision("apply_qos"),
            parameters=make_params("apply_qos"),
            governance_result=make_gov_auto(),
            ticket_id=None,
        )
        assert result["execution_id"]
        assert result["intent_id"] == intent_id
        assert result["decision_id"]
        assert result["action_type"] == "apply_qos"
        assert result["status"] == "success"
        assert result["adapter_response"]["success"] is True
        assert isinstance(result["duration_ms"], int)
        assert result["rollback_available"] is True
        assert result["rollback_status"] is None
        assert result["executed_at"]
        assert result["completed_at"]

    @pytest.mark.asyncio
    async def test_success_writes_two_audit_records(self) -> None:
        """ANIF-306 §11: EXECUTION_START and EXECUTION_SUCCESS MUST be written."""
        executor, _, writer = make_executor(force_success=True)
        await executor.execute(
            intent_id=uuid.uuid4(),
            decision=make_decision("apply_qos"),
            parameters=make_params("apply_qos"),
            governance_result=make_gov_auto(),
            ticket_id=None,
        )
        assert writer.write.call_count == 2

    @pytest.mark.asyncio
    async def test_success_persists_execution_record(self) -> None:
        """Execution record MUST be persisted to DB."""
        executor, session, _ = make_executor(force_success=True)
        await executor.execute(
            intent_id=uuid.uuid4(),
            decision=make_decision("apply_qos"),
            parameters=make_params("apply_qos"),
            governance_result=make_gov_auto(),
            ticket_id=None,
        )
        session.add.assert_called_once()


class TestExecuteFailureAndRollback:
    @pytest.mark.asyncio
    async def test_failure_triggers_automatic_rollback(self) -> None:
        """ANIF-306 §8.1: automatic rollback MUST be attempted on every failure."""
        executor, _, writer = make_executor(force_failure=True)
        result = await executor.execute(
            intent_id=uuid.uuid4(),
            decision=make_decision("apply_qos"),
            parameters=make_params("apply_qos"),
            governance_result=make_gov_auto(),
            ticket_id=None,
        )
        assert result["status"] == "failed"
        # 3 audit records: EXECUTION_START, EXECUTION_FAILED, ROLLBACK_START/SUCCESS
        assert writer.write.call_count >= 3

    @pytest.mark.asyncio
    async def test_failure_response_has_rollback_status(self) -> None:
        """ANIF-306 §9: rollback_status MUST be set after automatic rollback."""
        executor, _, _ = make_executor(force_failure=True)
        result = await executor.execute(
            intent_id=uuid.uuid4(),
            decision=make_decision("scale_bandwidth"),
            parameters=make_params("scale_bandwidth"),
            governance_result=make_gov_auto(),
            ticket_id=None,
        )
        assert result["rollback_status"] in ("success", "failed")

    @pytest.mark.asyncio
    async def test_failure_rollback_available_is_false(self) -> None:
        """ANIF-306 §9: rollback_available=false when adapter returned null rollback_reference."""
        executor, _, _ = make_executor(force_failure=True)
        result = await executor.execute(
            intent_id=uuid.uuid4(),
            decision=make_decision("apply_qos"),
            parameters=make_params("apply_qos"),
            governance_result=make_gov_auto(),
            ticket_id=None,
        )
        assert result["rollback_available"] is False


class TestManualRollback:
    @pytest.mark.asyncio
    async def test_rollback_by_intent_id(self) -> None:
        """ANIF-306 §6.2: rollback MUST be callable using only intent_id."""
        executor, session, writer = make_executor(force_success=True)
        from anif_platform.execution.models import ExecutionRecordRow
        record = ExecutionRecordRow()
        record.execution_id = str(uuid.uuid4())
        record.intent_id = uuid.uuid4()
        record.decision_id = str(uuid.uuid4())
        record.action_type = "apply_qos"
        record.status = "success"
        record.adapter_name = "mock"
        record.adapter_status_code = 200
        record.adapter_message = "ok"
        record.applied_changes = "[]"
        record.rollback_reference = "mock-rollback-abc"
        record.rollback_available = "true"
        record.rollback_status = None
        record.duration_ms = 100
        record.executed_at = datetime.now(UTC)
        record.completed_at = datetime.now(UTC)
        record.parameters_json = "{}"

        from sqlalchemy import Result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = record
        session.execute = AsyncMock(return_value=mock_result)
        session.flush = AsyncMock()

        result = await executor.rollback(intent_id=record.intent_id)
        assert result["rollback_status"] == "success"
        assert result["intent_id"] == record.intent_id

    @pytest.mark.asyncio
    async def test_rollback_not_found_raises(self) -> None:
        """Rollback with unknown intent_id MUST raise a clear error."""
        executor, session, _ = make_executor()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(Exception, match="No execution record"):
            await executor.rollback(intent_id=uuid.uuid4())
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  DATABASE_URL=postgresql+asyncpg://anif:anif_dev@localhost:5432/anif_dev \
  .venv/bin/pytest tests/unit/test_action_executor.py --tb=line -q 2>&1 | tail -5
```

Expected: `ImportError: No module named 'anif_platform.execution.executor'`

- [ ] **Step 3: Create `src/anif_platform/execution/executor.py`**

```python
"""
ActionExecutor — orchestrates execution and automatic rollback — ANIF-306 §6.

Checks governance preconditions (§5), calls the adapter (§7), writes audit
records (§11), persists execution records (§9), and triggers automatic
rollback on failure (§8.1).
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.audit.writer import AuditWriter
from anif_platform.execution.adapter import NetworkAdapter
from anif_platform.execution.models import ExecutionRecordRow
from anif_platform.human_loop.models import ApprovalTicketRow, TicketStatus
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage

log = structlog.get_logger(__name__)

# isolate_segment MUST NEVER auto-execute — ANIF-306 §5
_ALWAYS_REQUIRES_TICKET = frozenset({"isolate_segment"})


class PreconditionError(Exception):
    """Raised when governance preconditions are not satisfied — ANIF-306 §5."""

    def __init__(self, message: str, http_status: int = 403) -> None:
        super().__init__(message)
        self.http_status = http_status


class ActionExecutor:
    """
    Orchestrates action execution with precondition checks and automatic rollback.

    Inject adapter, session, and writer via constructor.
    Call execute() for new actions; rollback() for manual rollback by intent_id.
    """

    def __init__(
        self,
        adapter: NetworkAdapter,
        session: AsyncSession,
        writer: AuditWriter,
    ) -> None:
        self._adapter = adapter
        self._session = session
        self._writer = writer

    async def execute(
        self,
        intent_id: uuid.UUID,
        decision: dict[str, Any],
        parameters: dict[str, Any],
        governance_result: dict[str, Any],
        ticket_id: str | None,
    ) -> dict[str, Any]:
        """
        Execute an action after verifying governance preconditions — ANIF-306 §6.1.

        Writes EXECUTION_START before calling the adapter.
        Writes EXECUTION_SUCCESS or EXECUTION_FAILED after the adapter responds.
        Triggers automatic rollback on failure (§8.1).
        """
        decision_id = decision.get("decision_id", "")
        action_type = decision.get("recommended_action", {}).get("action_type", "apply_qos")
        execution_id = str(uuid.uuid4())

        # ── Precondition check ────────────────────────────────────────────
        await self._check_preconditions(
            intent_id=intent_id,
            action_type=action_type,
            governance_result=governance_result,
            ticket_id=ticket_id,
            execution_id=execution_id,
            decision_id=decision_id,
        )

        # ── EXECUTION_START audit ─────────────────────────────────────────
        executed_at = datetime.now(UTC)
        await self._writer.write(AuditRecord(
            intent_id=intent_id,
            stage=AuditStage.execute,
            input_summary={
                "execution_id": execution_id,
                "action_type": action_type,
                "event": "EXECUTION_START",
            },
            output_summary={},
            outcome=AuditOutcome.success,
            duration_ms=0,
            action_type=action_type,
        ))

        # ── Call adapter ──────────────────────────────────────────────────
        start = time.monotonic()
        adapter_response = self._adapter.execute(action_type, parameters, execution_id)
        duration_ms = int((time.monotonic() - start) * 1000)
        completed_at = datetime.now(UTC)

        rollback_available = adapter_response.success and adapter_response.rollback_reference is not None
        rollback_status: str | None = None

        if adapter_response.success:
            exec_status = "success"
            outcome = AuditOutcome.success
            event = "EXECUTION_SUCCESS"
        else:
            exec_status = "failed"
            outcome = AuditOutcome.failure
            event = "EXECUTION_FAILED"

        # ── Persist execution record ──────────────────────────────────────
        record = ExecutionRecordRow(
            execution_id=execution_id,
            intent_id=intent_id,
            decision_id=decision_id,
            action_type=action_type,
            status=exec_status,
            adapter_name="mock",
            adapter_status_code=adapter_response.adapter_status_code,
            adapter_message=adapter_response.adapter_message,
            applied_changes=json.dumps(adapter_response.applied_changes),
            rollback_reference=adapter_response.rollback_reference,
            rollback_available=str(rollback_available).lower(),
            rollback_status=None,
            duration_ms=duration_ms,
            executed_at=executed_at,
            completed_at=completed_at,
            parameters_json=json.dumps(parameters),
        )
        self._session.add(record)
        await self._session.flush()

        # ── EXECUTION_SUCCESS / EXECUTION_FAILED audit ────────────────────
        await self._writer.write(AuditRecord(
            intent_id=intent_id,
            stage=AuditStage.execute,
            input_summary={"execution_id": execution_id, "action_type": action_type, "event": event},
            output_summary={
                "status": exec_status,
                "adapter_status_code": adapter_response.adapter_status_code,
                "rollback_available": rollback_available,
            },
            outcome=outcome,
            duration_ms=duration_ms,
            action_type=action_type,
            rollback_available=rollback_available,
        ))

        log.info(
            "execution_completed",
            execution_id=execution_id,
            intent_id=str(intent_id),
            action_type=action_type,
            status=exec_status,
        )

        # ── Automatic rollback on failure (§8.1) ─────────────────────────
        if not adapter_response.success:
            rollback_status = await self._auto_rollback(
                intent_id=intent_id,
                action_type=action_type,
                rollback_reference=adapter_response.rollback_reference,
                execution_id=execution_id,
            )
            record.rollback_status = rollback_status
            await self._session.flush()

        return {
            "execution_id": execution_id,
            "intent_id": intent_id,
            "decision_id": decision_id,
            "action_type": action_type,
            "status": exec_status,
            "adapter_response": {
                "success": adapter_response.success,
                "adapter_status_code": adapter_response.adapter_status_code,
                "adapter_message": adapter_response.adapter_message,
                "applied_changes": adapter_response.applied_changes,
                "rollback_reference": adapter_response.rollback_reference,
            },
            "duration_ms": duration_ms,
            "rollback_available": rollback_available,
            "rollback_status": rollback_status,
            "executed_at": executed_at.isoformat(),
            "completed_at": completed_at.isoformat(),
        }

    async def rollback(self, intent_id: uuid.UUID) -> dict[str, Any]:
        """
        Manually roll back the most recent execution for an intent — ANIF-306 §6.2.

        Callable using only intent_id; retrieves rollback parameters from the
        persisted execution record.
        """
        result = await self._session.execute(
            select(ExecutionRecordRow)
            .where(ExecutionRecordRow.intent_id == intent_id)
            .order_by(ExecutionRecordRow.executed_at.desc())
            .limit(1)
        )
        record = result.scalar_one_or_none()
        if record is None:
            raise ValueError(f"No execution record found for intent_id={intent_id}")

        rollback_status = await self._auto_rollback(
            intent_id=intent_id,
            action_type=record.action_type,
            rollback_reference=record.rollback_reference,
            execution_id=record.execution_id,
        )

        audit_record = AuditRecord(
            intent_id=intent_id,
            stage=AuditStage.rollback,
            input_summary={"execution_id": record.execution_id, "action_type": record.action_type},
            output_summary={"rollback_status": rollback_status},
            outcome=AuditOutcome.success if rollback_status == "success" else AuditOutcome.failure,
            duration_ms=0,
            original_execute_record_id=uuid.UUID(record.execution_id) if len(record.execution_id) == 36 else None,
        )
        await self._writer.write(audit_record)

        return {
            "intent_id": intent_id,
            "execution_id": record.execution_id,
            "action_type": record.action_type,
            "rollback_status": rollback_status,
            "rolled_back_at": datetime.now(UTC).isoformat(),
            "audit_record_id": str(audit_record.record_id),
        }

    # ── Private helpers ───────────────────────────────────────────────────

    async def _check_preconditions(
        self,
        intent_id: uuid.UUID,
        action_type: str,
        governance_result: dict[str, Any],
        ticket_id: str | None,
        execution_id: str,
        decision_id: str,
    ) -> None:
        """Check ANIF-306 §5 preconditions; raise PreconditionError and write audit if unmet."""
        mode = governance_result.get("mode", "block")

        # isolate_segment always requires an approved ticket
        if action_type in _ALWAYS_REQUIRES_TICKET and mode == "auto":
            await self._write_precondition_failed(
                intent_id=intent_id,
                action_type=action_type,
                reason=(
                    f"isolate_segment MUST NOT execute under auto mode (ANIF-306 §5). "
                    f"An approved governance ticket is required."
                ),
            )
            raise PreconditionError(
                f"isolate_segment requires an approved governance ticket; auto mode is prohibited (ANIF-306 §5).",
                http_status=403,
            )

        if mode == "manual_review":
            if not ticket_id:
                await self._write_precondition_failed(
                    intent_id=intent_id,
                    action_type=action_type,
                    reason="manual_review mode requires a ticket_id but none was provided.",
                )
                raise PreconditionError(
                    "Governance mode is manual_review but ticket_id was not provided.",
                    http_status=403,
                )

            ticket = await self._session.get(ApprovalTicketRow, ticket_id)
            if ticket is None or ticket.status != TicketStatus.approved:
                status = ticket.status if ticket else "not_found"
                await self._write_precondition_failed(
                    intent_id=intent_id,
                    action_type=action_type,
                    reason=f"Ticket {ticket_id} must be approved (current status: {status}).",
                )
                raise PreconditionError(
                    f"Ticket {ticket_id} is not approved (status: {status}). "
                    f"Execution requires an approved ticket (ANIF-306 §5 Precondition B).",
                    http_status=403,
                )

    async def _write_precondition_failed(
        self,
        intent_id: uuid.UUID,
        action_type: str,
        reason: str,
    ) -> None:
        await self._writer.write(AuditRecord(
            intent_id=intent_id,
            stage=AuditStage.execute,
            input_summary={"action_type": action_type, "event": "PRECONDITION_FAILED"},
            output_summary={"reason": reason},
            outcome=AuditOutcome.blocked,
            duration_ms=0,
            action_type=action_type,
        ))

    async def _auto_rollback(
        self,
        intent_id: uuid.UUID,
        action_type: str,
        rollback_reference: str | None,
        execution_id: str,
    ) -> str:
        """Attempt automatic rollback — ANIF-306 §8.1. Returns 'success' or 'failed'."""
        rollback_id = str(uuid.uuid4())

        await self._writer.write(AuditRecord(
            intent_id=intent_id,
            stage=AuditStage.rollback,
            input_summary={
                "execution_id": execution_id,
                "action_type": action_type,
                "event": "ROLLBACK_START",
                "rollback_reference": rollback_reference,
            },
            output_summary={},
            outcome=AuditOutcome.success,
            duration_ms=0,
        ))

        rb_response = self._adapter.rollback(action_type, rollback_reference, rollback_id)

        if rb_response.success:
            rollback_status = "success"
            outcome = AuditOutcome.success
            event = "ROLLBACK_SUCCESS"
        else:
            rollback_status = "failed"
            outcome = AuditOutcome.failure
            event = "ROLLBACK_FAILED"
            log.error(
                "rollback_failed_human_escalation_required",
                intent_id=str(intent_id),
                action_type=action_type,
                execution_id=execution_id,
            )

        await self._writer.write(AuditRecord(
            intent_id=intent_id,
            stage=AuditStage.rollback,
            input_summary={"execution_id": execution_id, "action_type": action_type, "event": event},
            output_summary={
                "rollback_status": rollback_status,
                "adapter_status_code": rb_response.adapter_status_code,
            },
            outcome=outcome,
            duration_ms=0,
        ))

        return rollback_status
```

- [ ] **Step 4: Run tests**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  DATABASE_URL=postgresql+asyncpg://anif:anif_dev@localhost:5432/anif_dev \
  .venv/bin/pytest tests/unit/test_action_executor.py -v --tb=short 2>&1 | tail -30
```

Expected: all tests pass.

- [ ] **Step 5: Lint**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  .venv/bin/ruff check --fix src/anif_platform/execution/executor.py && \
  .venv/bin/black src/anif_platform/execution/executor.py
```

- [ ] **Step 6: Commit**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  git add src/anif_platform/execution/executor.py tests/unit/test_action_executor.py && \
  git commit -m "feat: implement ActionExecutor with precondition checks and automatic rollback (ANIF-306)"
```

---

## Task 6: Execution Router (`POST /execute`, `POST /rollback/{intent_id}`)

**Files:**
- Create: `src/anif_platform/execution/router.py`

- [ ] **Step 1: Create `src/anif_platform/execution/router.py`**

```python
"""
Execution router — ANIF-306.

POST /execute                    — execute an approved action
POST /rollback/{intent_id}       — manual rollback
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from anif_platform.auth import get_api_key
from anif_platform.audit.writer import AuditWriter
from anif_platform.execution.executor import ActionExecutor, PreconditionError
from anif_platform.execution.schemas import ExecuteRequest, ExecuteResponse, RollbackResponse

log = structlog.get_logger(__name__)
router = APIRouter(tags=["execution"])


def get_action_executor() -> ActionExecutor:
    raise NotImplementedError("Override via dependency injection")


@router.post("/execute", response_model=dict[str, Any])
async def execute_action(
    request: ExecuteRequest,
    executor: ActionExecutor = Depends(get_action_executor),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """
    Execute an approved action — ANIF-306 §6.1.

    Returns 403 if governance preconditions are not met.
    Returns 422 if action_type is not in the permitted set.
    """
    if request.dry_run:
        return {
            "execution_id": str(uuid.uuid4()),
            "intent_id": request.intent_id,
            "decision_id": request.decision_id,
            "action_type": request.action_type,
            "status": "dry_run",
            "adapter_response": None,
            "duration_ms": 0,
            "rollback_available": False,
            "rollback_status": None,
            "executed_at": None,
            "completed_at": None,
        }

    try:
        result = await executor.execute(
            intent_id=request.intent_id,
            decision={
                "decision_id": request.decision_id,
                "recommended_action": {
                    "action_type": request.action_type,
                    "parameters": request.parameters,
                    "risk_level": "medium",
                },
            },
            parameters=request.parameters,
            governance_result=request.governance_result,
            ticket_id=request.ticket_id,
        )
    except PreconditionError as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc

    return result


@router.post("/rollback/{intent_id}", response_model=dict[str, Any])
async def rollback_action(
    intent_id: uuid.UUID,
    executor: ActionExecutor = Depends(get_action_executor),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """
    Roll back the most recent execution for an intent — ANIF-306 §6.2.

    Callable using only intent_id.
    """
    try:
        result = await executor.rollback(intent_id=intent_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return result
```

- [ ] **Step 2: Verify import**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  DATABASE_URL=postgresql+asyncpg://anif:anif_dev@localhost:5432/anif_dev \
  .venv/bin/python -c "from anif_platform.execution.router import router; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Lint**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  .venv/bin/ruff check --fix src/anif_platform/execution/router.py && \
  .venv/bin/black src/anif_platform/execution/router.py
```

- [ ] **Step 4: Commit**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  git add src/anif_platform/execution/router.py && \
  git commit -m "feat: add execution router POST /execute and POST /rollback/{intent_id} (ANIF-306)"
```

---

## Task 7: Wire execution into main.py + pipeline Stage 6

**Files:**
- Modify: `src/anif_platform/main.py`
- Modify: `src/anif_platform/pipeline/router.py`

- [ ] **Step 1: Read `src/anif_platform/main.py` in full before editing**

This file already has `_get_session_writer`, `_get_session_approval_queue`, and the lifespan. You will add new imports and dependency factories.

- [ ] **Step 2: Add imports to `main.py`**

Add after the existing human_loop/governance imports:

```python
from anif_platform.execution.router import get_action_executor as exec_get_executor
from anif_platform.execution.router import router as execution_router
from anif_platform.execution.executor import ActionExecutor
from anif_platform.execution.mock_adapter import MockNetworkAdapter
```

- [ ] **Step 3: Add executor dependency factory to `main.py`**

Add after `_get_session_approval_queue`:

```python
async def _get_session_executor(request: Request) -> AsyncGenerator[ActionExecutor, None]:
    async with async_session_factory() as session:
        writer = AuditWriter(session)
        adapter = MockNetworkAdapter()
        yield ActionExecutor(adapter=adapter, session=session, writer=writer)
```

- [ ] **Step 4: Add dependency override and mount router in `main.py`**

In the `dependency_overrides` block, add:
```python
app.dependency_overrides[exec_get_executor] = _get_session_executor
```

In the `include_router` block, add:
```python
app.include_router(execution_router)
```

- [ ] **Step 5: Read `src/anif_platform/pipeline/router.py` and replace Stage 6 stub**

Find this block:
```python
# ── Stage 6: Execute (STUB — implemented in B5) ──────────────────────
pipeline_result["execute"] = {
    "status": "not_yet_implemented",
    "stage": "execute",
    "message": "ActionExecutor will be implemented in B5",
}
```

Add `get_action_executor` import and parameter to `pipeline/router.py`:

```python
from anif_platform.execution.executor import ActionExecutor, PreconditionError
from anif_platform.execution.router import get_action_executor
```

Add `executor: ActionExecutor = Depends(get_action_executor)` to the `orchestrate` function signature.

Replace the Stage 6 stub with:

```python
# ── Stage 6: Execute (ANIF-306) ──────────────────────────────────────
if not request.dry_run:
    try:
        _exec_result = await executor.execute(
            intent_id=intent_id,
            decision=decision_result,
            parameters=decision_result.get("recommended_action", {}).get("parameters", {}),
            governance_result=_gov_result,
            ticket_id=None,  # auto mode: no ticket needed
        )
    except PreconditionError as exc:
        return {
            "status": "precondition_failed",
            "stage": "execute",
            "intent_id": str(intent_id),
            "error": str(exc),
        }
    pipeline_result["execute"] = _exec_result
else:
    pipeline_result["execute"] = {"status": "dry_run", "stage": "execute"}
```

Also add `get_action_executor` to the `dependency_overrides` in `main.py`:
```python
from anif_platform.pipeline.router import get_action_executor as pipeline_get_executor
# ...
app.dependency_overrides[pipeline_get_executor] = _get_session_executor
```

- [ ] **Step 6: Verify the app imports cleanly**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  DATABASE_URL=postgresql+asyncpg://anif:anif_dev@localhost:5432/anif_dev \
  .venv/bin/python -c "from anif_platform.main import app; print('OK')"
```

Expected: `OK`

- [ ] **Step 7: Run full unit test suite**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  DATABASE_URL=postgresql+asyncpg://anif:anif_dev@localhost:5432/anif_dev \
  .venv/bin/pytest tests/unit/ \
    --ignore=tests/unit/test_audit_writer.py \
    --ignore=tests/unit/test_intent_validator.py \
    --tb=short -q 2>&1 | tail -5
```

Expected: all tests pass (at least 280+ with the new B5 tests).

- [ ] **Step 8: Lint both files**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  .venv/bin/ruff check --fix src/anif_platform/main.py src/anif_platform/pipeline/router.py && \
  .venv/bin/black src/anif_platform/main.py src/anif_platform/pipeline/router.py
```

- [ ] **Step 9: Commit**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold && \
  git add src/anif_platform/main.py src/anif_platform/pipeline/router.py && \
  git commit -m "feat: integrate ActionExecutor into pipeline orchestrator and main.py (ANIF-306)"
```

---

## Self-Review: Spec Coverage Check

### ANIF-306 Requirements

| Requirement | Task |
|---|---|
| Four action types with correct characteristics (§4) | Task 2 (success rates), Task 5 (preconditions) |
| Governance Precondition A: auto mode permits non-isolate | Task 5 |
| Governance Precondition B: manual_review requires approved ticket | Task 5 |
| `isolate_segment` ALWAYS requires approved ticket | Task 5 |
| `PRECONDITION_FAILED` audit event written on failure | Task 5 |
| Abstract adapter interface (Protocol) | Task 1 |
| `execute()` + `rollback()` + `health_check()` on adapter | Task 1 |
| Mock adapter with per-action-type success rates | Task 2 |
| Mock rollback succeeds 100% | Task 2 |
| Execution record persisted to DB | Task 3, Task 5 |
| Alembic migration for execution_records | Task 4 |
| `rollback()` callable by intent_id alone | Task 5 |
| EXECUTION_START audit before adapter call | Task 5 |
| EXECUTION_SUCCESS / EXECUTION_FAILED audit after | Task 5 |
| Automatic rollback on failure (§8.1) | Task 5 |
| ROLLBACK_START / ROLLBACK_SUCCESS / ROLLBACK_FAILED audit | Task 5 |
| ROLLBACK_FAILED triggers log escalation alert | Task 5 |
| Execution response schema (all 10 fields) | Task 3, Task 5 |
| `POST /execute` endpoint | Task 6 |
| `POST /rollback/{intent_id}` endpoint | Task 6 |
| Pipeline Stage 6 stub replaced with live executor | Task 7 |

### Gaps / Out of Scope for B5

- **Adapter selection by segment/platform** (§7.3): hardcoded `MockNetworkAdapter`. Real adapter routing deferred to B6.
- **Partial success status** (§8.2): mock adapter returns binary success/failure only; partial path untested.
- **Timeout handling** (§8.3): no timeout configured on mock adapter calls. Add in B6 with real adapters.
- **`GET /execute/{execution_id}`**: retrieval endpoint for execution records not specified in core flow; defer.
- **Two-person authorisation for isolate_segment** (§13): operational consideration, deferred to B6.
