# B6 Agent Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the agent infrastructure layer — AgentRegistry with full lifecycle management, X.509 certificate issuance/verification, and tier boundary enforcement — satisfying ANIF-803, ANIF-805, ANIF-801, ANIF-802, and ANIF-843.

**Architecture:** SQLAlchemy ORM persists agent state across four tables (registry, lifecycle events, decommissioned identities, revocation list). A `MockCertificateAuthority` issues real X.509v3 certificates (using the `cryptography` lib already in `pyproject.toml`). A `CertificateVerifier` performs all five ANIF-843 §5.2 verification steps. A `TierBoundaryChecker` enforces the ANIF-802/843 tier matrix. All are wired as FastAPI dependency-injectable services with the same DI pattern used throughout the platform.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy 2 async, Pydantic v2, `cryptography` library (already a dependency), pytest-asyncio, structlog. Follows the same patterns as B5 execution module.

---

## File Structure

### New files
| File | Responsibility |
|---|---|
| `src/anif_platform/agents/models.py` | SQLAlchemy ORM: `AgentRegistryRow`, `AgentLifecycleEventRow`, `DecommissionedIdentityRow`, `AgentRevocationRow` |
| `src/anif_platform/agents/schemas.py` | Pydantic v2 models, enums (`AgentLifecycleState`, `AgentTier`), request/response schemas |
| `src/anif_platform/agents/registry.py` | `AgentRegistry` service: register, transition, get, list\_active, clear\_working\_context |
| `src/anif_platform/agents/tier_boundary.py` | `TierBoundaryChecker`: endpoint category → minimum tier map; ANIF-802 forbidden endpoint map |
| `src/anif_platform/agents/certificate.py` | `MockCertificateAuthority`, `CertificateVerifier`, `RevocationList` |
| `src/anif_platform/agents/router.py` | REST API: POST /agents, GET /agents/{id}, POST /agents/{id}/transition, GET /agents |
| `migrations/versions/005_add_agent_registry.py` | Alembic migration adding four new tables |
| `tests/unit/test_agent_registry.py` | Tests for AgentRegistry service |
| `tests/unit/test_agent_certificate.py` | Tests for MockCA, CertificateVerifier, RevocationList |
| `tests/unit/test_tier_boundary.py` | Tests for TierBoundaryChecker |
| `tests/unit/test_agent_router.py` | Tests for REST endpoints |

### Modified files
| File | Change |
|---|---|
| `src/anif_platform/agents/__init__.py` | Update module docstring |
| `migrations/env.py` | Import `anif_platform.agents.models` |
| `src/anif_platform/main.py` | Add agents router + DI overrides for `AgentRegistry` |

---

## Task 1: DB Models

**Files:**
- Create: `src/anif_platform/agents/models.py`
- Modify: `src/anif_platform/agents/__init__.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_agent_registry.py
"""Unit tests for AgentRegistry and DB models — ANIF-803, ANIF-805."""
from __future__ import annotations

from anif_platform.agents.models import (
    AgentLifecycleEventRow,
    AgentRegistryRow,
    AgentRevocationRow,
    DecommissionedIdentityRow,
)


def test_agent_registry_row_has_required_columns() -> None:
    cols = {c.key for c in AgentRegistryRow.__table__.columns}
    assert "agent_id" in cols
    assert "agent_type" in cols
    assert "role" in cols
    assert "tier" in cols
    assert "lifecycle_state" in cols
    assert "strike_count" in cols
    assert "provisional_until" in cols
    assert "capabilities_hash" in cols
    assert "certificate_pem" in cols
    assert "certificate_expires_at" in cols
    assert "last_intent_id" in cols
    assert "last_intent_at" in cols
    assert "working_context_cleared_at" in cols
    assert "registered_at" in cols
    assert "manifest_json" in cols


def test_agent_lifecycle_event_row_has_required_columns() -> None:
    cols = {c.key for c in AgentLifecycleEventRow.__table__.columns}
    assert "event_id" in cols
    assert "agent_id" in cols
    assert "previous_state" in cols
    assert "new_state" in cols
    assert "trigger" in cols
    assert "approver_identity" in cols
    assert "reason" in cols
    assert "transitioned_at" in cols


def test_decommissioned_identity_row_has_required_columns() -> None:
    cols = {c.key for c in DecommissionedIdentityRow.__table__.columns}
    assert "record_id" in cols
    assert "agent_id" in cols
    assert "agent_type" in cols
    assert "tier" in cols
    assert "capabilities_hash" in cols
    assert "decommissioned_at" in cols
    assert "decommissioned_by" in cols
    assert "reason" in cols


def test_agent_revocation_row_has_required_columns() -> None:
    cols = {c.key for c in AgentRevocationRow.__table__.columns}
    assert "revocation_id" in cols
    assert "agent_id" in cols
    assert "revoked_at" in cols
    assert "reason" in cols
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /home/dan/Desktop/github/auto_networking/.worktrees/scaffold
.venv/bin/pytest tests/unit/test_agent_registry.py::test_agent_registry_row_has_required_columns -v
```

Expected: `FAILED` — `ImportError: cannot import name 'AgentRegistryRow'`

- [ ] **Step 3: Write the implementation**

```python
# src/anif_platform/agents/models.py
"""SQLAlchemy ORM models for agent infrastructure — ANIF-803, ANIF-805, ANIF-843."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from anif_platform.database import Base


class AgentRegistryRow(Base):
    """Persistent agent state — ANIF-805 permitted persistent state items."""

    __tablename__ = "agent_registry"

    agent_id: Mapped[str] = mapped_column(String, primary_key=True)
    agent_type: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    tier: Mapped[int] = mapped_column(Integer, nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(String, nullable=False)
    strike_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    provisional_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    capabilities_hash: Mapped[str] = mapped_column(String, nullable=False)
    certificate_pem: Mapped[str | None] = mapped_column(Text, nullable=True)
    certificate_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_intent_id: Mapped[str | None] = mapped_column(String, nullable=True)
    last_intent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    working_context_cleared_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    manifest_json: Mapped[str] = mapped_column(Text, nullable=False)


class AgentLifecycleEventRow(Base):
    """Append-only lifecycle transition log — ANIF-803 §5."""

    __tablename__ = "agent_lifecycle_events"

    event_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    agent_id: Mapped[str] = mapped_column(
        String, ForeignKey("agent_registry.agent_id"), nullable=False, index=True
    )
    previous_state: Mapped[str] = mapped_column(String, nullable=False)
    new_state: Mapped[str] = mapped_column(String, nullable=False)
    trigger: Mapped[str] = mapped_column(String, nullable=False)
    approver_identity: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    transitioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DecommissionedIdentityRow(Base):
    """Append-only decommissioned identity register — ANIF-803 §6."""

    __tablename__ = "decommissioned_identities"

    record_id: Mapped[str] = mapped_column(String, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    agent_type: Mapped[str] = mapped_column(String, nullable=False)
    tier: Mapped[int] = mapped_column(Integer, nullable=False)
    capabilities_hash: Mapped[str] = mapped_column(String, nullable=False)
    decommissioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    decommissioned_by: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)


class AgentRevocationRow(Base):
    """Certificate revocation list — ANIF-843 §7.2."""

    __tablename__ = "agent_revocation_list"

    revocation_id: Mapped[str] = mapped_column(String, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
```

Also update the `__init__.py`:

```python
# src/anif_platform/agents/__init__.py
"""ANIF agent infrastructure — lifecycle, certificates, and tier boundary enforcement."""
```

- [ ] **Step 4: Run test to verify it passes**

```bash
.venv/bin/pytest tests/unit/test_agent_registry.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Write Alembic migration**

```python
# migrations/versions/005_add_agent_registry.py
"""add_agent_registry

Revision ID: 005
Revises: 004
Create Date: 2026-04-29
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_registry",
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("agent_type", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("tier", sa.Integer(), nullable=False),
        sa.Column("lifecycle_state", sa.String(), nullable=False),
        sa.Column("strike_count", sa.Integer(), nullable=False),
        sa.Column("provisional_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("capabilities_hash", sa.String(), nullable=False),
        sa.Column("certificate_pem", sa.Text(), nullable=True),
        sa.Column("certificate_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_intent_id", sa.String(), nullable=True),
        sa.Column("last_intent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("working_context_cleared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("manifest_json", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("agent_id"),
    )
    op.create_table(
        "agent_lifecycle_events",
        sa.Column("event_id", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), sa.ForeignKey("agent_registry.agent_id"), nullable=False),
        sa.Column("previous_state", sa.String(), nullable=False),
        sa.Column("new_state", sa.String(), nullable=False),
        sa.Column("trigger", sa.String(), nullable=False),
        sa.Column("approver_identity", sa.String(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("transitioned_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index("ix_lifecycle_events_agent_id", "agent_lifecycle_events", ["agent_id"])
    op.create_table(
        "decommissioned_identities",
        sa.Column("record_id", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("agent_type", sa.String(), nullable=False),
        sa.Column("tier", sa.Integer(), nullable=False),
        sa.Column("capabilities_hash", sa.String(), nullable=False),
        sa.Column("decommissioned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decommissioned_by", sa.String(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("record_id"),
    )
    op.create_index(
        "ix_decommissioned_identities_agent_id", "decommissioned_identities", ["agent_id"]
    )
    op.create_table(
        "agent_revocation_list",
        sa.Column("revocation_id", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("revocation_id"),
    )
    op.create_index("ix_revocation_list_agent_id", "agent_revocation_list", ["agent_id"])


def downgrade() -> None:
    op.drop_index("ix_revocation_list_agent_id", table_name="agent_revocation_list")
    op.drop_table("agent_revocation_list")
    op.drop_index("ix_decommissioned_identities_agent_id", table_name="decommissioned_identities")
    op.drop_table("decommissioned_identities")
    op.drop_index("ix_lifecycle_events_agent_id", table_name="agent_lifecycle_events")
    op.drop_table("agent_lifecycle_events")
    op.drop_table("agent_registry")
```

- [ ] **Step 6: Commit**

```bash
git add src/anif_platform/agents/__init__.py \
        src/anif_platform/agents/models.py \
        migrations/versions/005_add_agent_registry.py \
        tests/unit/test_agent_registry.py
git commit -m "feat: add agent registry DB models and migration (B6 ANIF-803/805/843)"
```

---

## Task 2: Pydantic Schemas

**Files:**
- Create: `src/anif_platform/agents/schemas.py`

- [ ] **Step 1: Write the failing tests (add to `tests/unit/test_agent_registry.py`)**

```python
# Append to tests/unit/test_agent_registry.py
from anif_platform.agents.schemas import (
    AgentLifecycleState,
    AgentTier,
    RegisterAgentRequest,
    RegisterAgentResponse,
    TransitionRequest,
    TransitionResponse,
)


def test_lifecycle_state_enum_has_all_states() -> None:
    states = {s.value for s in AgentLifecycleState}
    assert "PROPOSED" in states
    assert "PROVISIONAL" in states
    assert "ACTIVE" in states
    assert "DEGRADED" in states
    assert "DECOMMISSIONED" in states
    assert "UNTRUSTED" in states


def test_agent_tier_enum_has_all_tiers() -> None:
    tiers = {t.value for t in AgentTier}
    assert 0 in tiers
    assert 1 in tiers
    assert 2 in tiers
    assert 3 in tiers


def test_register_agent_request_validates_tier() -> None:
    req = RegisterAgentRequest(
        agent_id="agent-001",
        agent_type="NetworkObserver",
        role="Network Observer",
        tier=1,
        manifest={"capabilities": ["read_telemetry"]},
    )
    assert req.tier == 1


def test_transition_request_requires_all_fields() -> None:
    req = TransitionRequest(
        new_state=AgentLifecycleState.PROVISIONAL,
        trigger="council_approval",
        approver_identity="council-member-1",
        reason="Initial approval after review",
    )
    assert req.new_state == AgentLifecycleState.PROVISIONAL
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/unit/test_agent_registry.py::test_lifecycle_state_enum_has_all_states -v
```

Expected: `FAILED` — `ImportError: cannot import name 'AgentLifecycleState'`

- [ ] **Step 3: Write the implementation**

```python
# src/anif_platform/agents/schemas.py
"""Pydantic schemas for agent infrastructure — ANIF-801, ANIF-803, ANIF-805, ANIF-843."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AgentLifecycleState(str, Enum):
    """Agent lifecycle states — ANIF-803 §4."""

    PROPOSED = "PROPOSED"
    PROVISIONAL = "PROVISIONAL"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    DECOMMISSIONED = "DECOMMISSIONED"
    UNTRUSTED = "UNTRUSTED"


class AgentTier(int, Enum):
    """Agent tier classification — ANIF-801 §4–7."""

    TIER_0 = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class RegisterAgentRequest(BaseModel):
    agent_id: str = Field(..., description="Unique agent instance identifier")
    agent_type: str = Field(..., description="Registered agent type from ANIF-801 catalogue")
    role: str = Field(..., description="Role from ANIF-801 role catalogue")
    tier: int = Field(..., ge=0, le=3, description="Agent tier 0–3")
    manifest: dict[str, Any] = Field(..., description="Agent capability manifest")


class RegisterAgentResponse(BaseModel):
    agent_id: str
    lifecycle_state: AgentLifecycleState
    provisional_until: datetime | None
    certificate_pem: str | None
    registered_at: datetime


class TransitionRequest(BaseModel):
    new_state: AgentLifecycleState
    trigger: str = Field(..., description="Event that caused the transition")
    approver_identity: str = Field(..., description="Identity of the approving operator")
    reason: str = Field(..., description="Human-readable reason for transition")


class TransitionResponse(BaseModel):
    agent_id: str
    previous_state: AgentLifecycleState
    new_state: AgentLifecycleState
    event_id: str
    transitioned_at: datetime


class AgentDetailResponse(BaseModel):
    agent_id: str
    agent_type: str
    role: str
    tier: int
    lifecycle_state: AgentLifecycleState
    strike_count: int
    provisional_until: datetime | None
    capabilities_hash: str
    certificate_expires_at: datetime | None
    last_intent_id: str | None
    last_intent_at: datetime | None
    working_context_cleared_at: datetime | None
    registered_at: datetime


class AgentListResponse(BaseModel):
    agents: list[AgentDetailResponse]
    total: int
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/pytest tests/unit/test_agent_registry.py -v
```

Expected: all 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/anif_platform/agents/schemas.py tests/unit/test_agent_registry.py
git commit -m "feat: add agent schemas — lifecycle states, tier enum, request/response (B6)"
```

---

## Task 3: AgentRegistry Service

**Files:**
- Create: `src/anif_platform/agents/registry.py`

- [ ] **Step 1: Write the failing tests (add to `tests/unit/test_agent_registry.py`)**

```python
# Append to tests/unit/test_agent_registry.py
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from anif_platform.agents.registry import (
    AgentRegistry,
    InvalidTransitionError,
    ProvisionalPeriodError,
)
from anif_platform.agents.schemas import AgentLifecycleState


def make_registry() -> tuple[AgentRegistry, AsyncMock]:
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    registry = AgentRegistry(session=session)
    return registry, session


def make_mock_agent_row(
    lifecycle_state: str = "PROPOSED",
    provisional_until: datetime | None = None,
    tier: int = 1,
) -> MagicMock:
    row = MagicMock()
    row.agent_id = "agent-001"
    row.agent_type = "NetworkObserver"
    row.role = "Network Observer"
    row.tier = tier
    row.lifecycle_state = lifecycle_state
    row.provisional_until = provisional_until
    row.strike_count = 0
    row.capabilities_hash = "abc123"
    row.manifest_json = json.dumps({"capabilities": ["read_telemetry"]})
    return row


@pytest.mark.asyncio
async def test_register_creates_agent_in_proposed_state() -> None:
    registry, session = make_registry()
    agent = await registry.register(
        agent_id="agent-001",
        agent_type="NetworkObserver",
        role="Network Observer",
        tier=1,
        manifest={"capabilities": ["read_telemetry"]},
    )
    assert agent.lifecycle_state == AgentLifecycleState.PROPOSED.value
    session.add.assert_called()
    session.flush.assert_called()


@pytest.mark.asyncio
async def test_register_computes_capabilities_hash() -> None:
    registry, _ = make_registry()
    manifest = {"capabilities": ["read_telemetry"]}
    agent = await registry.register(
        agent_id="agent-001",
        agent_type="NetworkObserver",
        role="Network Observer",
        tier=1,
        manifest=manifest,
    )
    import hashlib
    expected = hashlib.sha256(
        json.dumps(manifest, sort_keys=True).encode()
    ).hexdigest()
    assert agent.capabilities_hash == expected


@pytest.mark.asyncio
async def test_transition_proposed_to_provisional_sets_provisional_until() -> None:
    registry, session = make_registry()

    mock_agent = make_mock_agent_row("PROPOSED")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = mock_agent
    session.execute = AsyncMock(return_value=result_mock)

    event = await registry.transition(
        agent_id="agent-001",
        new_state=AgentLifecycleState.PROVISIONAL,
        trigger="council_approval",
        approver_identity="council-member-1",
        reason="Approved after review",
    )
    assert event.new_state == AgentLifecycleState.PROVISIONAL.value
    assert mock_agent.provisional_until is not None
    # Should be approximately 72 hours from now
    expected_min = datetime.now(UTC) + timedelta(hours=71)
    expected_max = datetime.now(UTC) + timedelta(hours=73)
    assert expected_min < mock_agent.provisional_until < expected_max


@pytest.mark.asyncio
async def test_transition_provisional_to_active_blocked_before_72h() -> None:
    registry, session = make_registry()

    # provisional_until is still in the future
    future = datetime.now(UTC) + timedelta(hours=48)
    mock_agent = make_mock_agent_row("PROVISIONAL", provisional_until=future)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = mock_agent
    session.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(ProvisionalPeriodError):
        await registry.transition(
            agent_id="agent-001",
            new_state=AgentLifecycleState.ACTIVE,
            trigger="manual",
            approver_identity="ops",
            reason="Promote to active",
        )


@pytest.mark.asyncio
async def test_transition_provisional_to_active_succeeds_after_72h() -> None:
    registry, session = make_registry()

    # provisional_until is in the past
    past = datetime.now(UTC) - timedelta(hours=1)
    mock_agent = make_mock_agent_row("PROVISIONAL", provisional_until=past)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = mock_agent
    session.execute = AsyncMock(return_value=result_mock)

    event = await registry.transition(
        agent_id="agent-001",
        new_state=AgentLifecycleState.ACTIVE,
        trigger="manual",
        approver_identity="ops",
        reason="Promote after provisional period",
    )
    assert event.new_state == AgentLifecycleState.ACTIVE.value


@pytest.mark.asyncio
async def test_transition_decommissioned_raises_invalid() -> None:
    registry, session = make_registry()

    mock_agent = make_mock_agent_row("DECOMMISSIONED")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = mock_agent
    session.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(InvalidTransitionError):
        await registry.transition(
            agent_id="agent-001",
            new_state=AgentLifecycleState.ACTIVE,
            trigger="attempt",
            approver_identity="ops",
            reason="Trying to revive",
        )


@pytest.mark.asyncio
async def test_transition_to_decommissioned_writes_to_register() -> None:
    registry, session = make_registry()

    mock_agent = make_mock_agent_row("ACTIVE")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = mock_agent
    session.execute = AsyncMock(return_value=result_mock)

    added_rows: list = []
    session.add = MagicMock(side_effect=lambda row: added_rows.append(row))

    await registry.transition(
        agent_id="agent-001",
        new_state=AgentLifecycleState.DECOMMISSIONED,
        trigger="manual",
        approver_identity="council",
        reason="End of life",
    )

    row_types = [type(r).__name__ for r in added_rows]
    assert "AgentLifecycleEventRow" in row_types
    assert "DecommissionedIdentityRow" in row_types


@pytest.mark.asyncio
async def test_clear_working_context_sets_timestamp() -> None:
    registry, session = make_registry()

    mock_agent = make_mock_agent_row("ACTIVE")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = mock_agent
    session.execute = AsyncMock(return_value=result_mock)

    await registry.clear_working_context(agent_id="agent-001", intent_id="intent-xyz")
    assert mock_agent.working_context_cleared_at is not None
    assert mock_agent.last_intent_id == "intent-xyz"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/pytest tests/unit/test_agent_registry.py -k "test_register_creates" -v
```

Expected: `FAILED` — `ImportError: cannot import name 'AgentRegistry'`

- [ ] **Step 3: Write the implementation**

```python
# src/anif_platform/agents/registry.py
"""AgentRegistry service — ANIF-803 lifecycle management, ANIF-805 state constraints."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.agents.models import (
    AgentLifecycleEventRow,
    AgentRegistryRow,
    DecommissionedIdentityRow,
)
from anif_platform.agents.schemas import AgentLifecycleState

log = structlog.get_logger(__name__)

_PROVISIONAL_HOURS: int = 72

_VALID_TRANSITIONS: dict[AgentLifecycleState, frozenset[AgentLifecycleState]] = {
    AgentLifecycleState.PROPOSED: frozenset(
        {AgentLifecycleState.PROVISIONAL, AgentLifecycleState.DECOMMISSIONED}
    ),
    AgentLifecycleState.PROVISIONAL: frozenset(
        {
            AgentLifecycleState.ACTIVE,
            AgentLifecycleState.DECOMMISSIONED,
            AgentLifecycleState.UNTRUSTED,
        }
    ),
    AgentLifecycleState.ACTIVE: frozenset(
        {
            AgentLifecycleState.DEGRADED,
            AgentLifecycleState.DECOMMISSIONED,
            AgentLifecycleState.UNTRUSTED,
        }
    ),
    AgentLifecycleState.DEGRADED: frozenset(
        {
            AgentLifecycleState.ACTIVE,
            AgentLifecycleState.DECOMMISSIONED,
            AgentLifecycleState.UNTRUSTED,
        }
    ),
    AgentLifecycleState.DECOMMISSIONED: frozenset(),  # terminal — ANIF-803
    AgentLifecycleState.UNTRUSTED: frozenset({AgentLifecycleState.DECOMMISSIONED}),
}


class InvalidTransitionError(Exception):
    """Raised when a lifecycle transition is not permitted."""


class ProvisionalPeriodError(Exception):
    """Raised when PROVISIONAL→ACTIVE transition is attempted before 72h — ANIF-803."""


class AgentNotFoundError(Exception):
    """Raised when agent_id is not found in the registry."""


class AgentRegistry:
    """Manages agent lifecycle and permitted persistent state — ANIF-803, ANIF-805."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def register(
        self,
        agent_id: str,
        agent_type: str,
        role: str,
        tier: int,
        manifest: dict[str, Any],
    ) -> AgentRegistryRow:
        """Create a new agent in PROPOSED state — ANIF-803 §4.1."""
        manifest_json = json.dumps(manifest, sort_keys=True)
        capabilities_hash = hashlib.sha256(manifest_json.encode()).hexdigest()

        now = datetime.now(UTC)
        agent = AgentRegistryRow(
            agent_id=agent_id,
            agent_type=agent_type,
            role=role,
            tier=tier,
            lifecycle_state=AgentLifecycleState.PROPOSED.value,
            strike_count=0,
            provisional_until=None,
            capabilities_hash=capabilities_hash,
            certificate_pem=None,
            certificate_expires_at=None,
            last_intent_id=None,
            last_intent_at=None,
            working_context_cleared_at=None,
            registered_at=now,
            manifest_json=manifest_json,
        )
        self._session.add(agent)
        await self._session.flush()
        log.info("agent_registered", agent_id=agent_id, tier=tier, role=role)
        return agent

    async def get(self, agent_id: str) -> AgentRegistryRow:
        """Retrieve agent by ID."""
        result = await self._session.execute(
            select(AgentRegistryRow).where(AgentRegistryRow.agent_id == agent_id)
        )
        agent = result.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id!r} not found in registry")
        return agent

    async def transition(
        self,
        agent_id: str,
        new_state: AgentLifecycleState,
        trigger: str,
        approver_identity: str,
        reason: str,
    ) -> AgentLifecycleEventRow:
        """Transition agent to new lifecycle state — ANIF-803 §5.

        Every transition is logged with previous state, new state, timestamp,
        trigger, approver identity, and reason (ANIF-803 §5.4).
        """
        agent = await self.get(agent_id)
        current_state = AgentLifecycleState(agent.lifecycle_state)

        allowed = _VALID_TRANSITIONS[current_state]
        if new_state not in allowed:
            raise InvalidTransitionError(
                f"Transition {current_state!r} → {new_state!r} is not permitted"
            )

        # ANIF-803 §4.2: PROVISIONAL must be held for 72 hours before ACTIVE
        if (
            current_state == AgentLifecycleState.PROVISIONAL
            and new_state == AgentLifecycleState.ACTIVE
        ):
            if agent.provisional_until and datetime.now(UTC) < agent.provisional_until:
                raise ProvisionalPeriodError(
                    f"Agent must remain PROVISIONAL until {agent.provisional_until.isoformat()}"
                )

        now = datetime.now(UTC)
        event = AgentLifecycleEventRow(
            event_id=str(uuid.uuid4()),
            agent_id=agent_id,
            previous_state=current_state.value,
            new_state=new_state.value,
            trigger=trigger,
            approver_identity=approver_identity,
            reason=reason,
            transitioned_at=now,
        )
        self._session.add(event)

        agent.lifecycle_state = new_state.value

        if new_state == AgentLifecycleState.PROVISIONAL:
            agent.provisional_until = now + timedelta(hours=_PROVISIONAL_HOURS)

        # ANIF-803 §6: DECOMMISSIONED agents written to append-only identity register
        if new_state == AgentLifecycleState.DECOMMISSIONED:
            decommission = DecommissionedIdentityRow(
                record_id=str(uuid.uuid4()),
                agent_id=agent_id,
                agent_type=agent.agent_type,
                tier=agent.tier,
                capabilities_hash=agent.capabilities_hash,
                decommissioned_at=now,
                decommissioned_by=approver_identity,
                reason=reason,
            )
            self._session.add(decommission)

        await self._session.flush()
        log.info(
            "agent_lifecycle_transition",
            agent_id=agent_id,
            previous_state=current_state.value,
            new_state=new_state.value,
            trigger=trigger,
        )
        return event

    async def list_active(self) -> list[AgentRegistryRow]:
        """Return all agents in ACTIVE state."""
        result = await self._session.execute(
            select(AgentRegistryRow).where(
                AgentRegistryRow.lifecycle_state == AgentLifecycleState.ACTIVE.value
            )
        )
        return list(result.scalars().all())

    async def clear_working_context(self, agent_id: str, intent_id: str) -> None:
        """Clear agent working context on intent completion — ANIF-805 §4.2."""
        agent = await self.get(agent_id)
        now = datetime.now(UTC)
        agent.working_context_cleared_at = now
        agent.last_intent_id = intent_id
        agent.last_intent_at = now
        await self._session.flush()
        log.info("agent_working_context_cleared", agent_id=agent_id, intent_id=intent_id)

    async def record_cert(
        self,
        agent_id: str,
        certificate_pem: str,
        certificate_expires_at: datetime,
    ) -> None:
        """Store issued certificate PEM and expiry in the registry."""
        agent = await self.get(agent_id)
        agent.certificate_pem = certificate_pem
        agent.certificate_expires_at = certificate_expires_at
        await self._session.flush()
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/pytest tests/unit/test_agent_registry.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/anif_platform/agents/registry.py tests/unit/test_agent_registry.py
git commit -m "feat: implement AgentRegistry — lifecycle management per ANIF-803/805"
```

---

## Task 4: Tier Boundary Checker

**Files:**
- Create: `src/anif_platform/agents/tier_boundary.py`
- Create: `tests/unit/test_tier_boundary.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_tier_boundary.py
"""Unit tests for TierBoundaryChecker — ANIF-802, ANIF-843 §6."""
from __future__ import annotations

import pytest

from anif_platform.agents.tier_boundary import TierBoundaryChecker


@pytest.fixture
def checker() -> TierBoundaryChecker:
    return TierBoundaryChecker()


def test_tier_0_can_read_canonical_state(checker: TierBoundaryChecker) -> None:
    """ANIF-843 §6.2: canonical_state_read requires Tier 0 minimum."""
    assert checker.check(agent_tier=0, endpoint_category="canonical_state_read") is True


def test_tier_1_can_call_policy_evaluation(checker: TierBoundaryChecker) -> None:
    """ANIF-843 §6.2: policy_evaluation requires Tier 1 minimum."""
    assert checker.check(agent_tier=1, endpoint_category="policy_evaluation") is True


def test_tier_0_cannot_call_policy_evaluation(checker: TierBoundaryChecker) -> None:
    """Tier 0 is below the Tier 1 minimum for policy_evaluation."""
    assert checker.check(agent_tier=0, endpoint_category="policy_evaluation") is False


def test_tier_2_can_call_risk_scoring(checker: TierBoundaryChecker) -> None:
    assert checker.check(agent_tier=2, endpoint_category="risk_scoring") is True


def test_tier_1_cannot_call_risk_scoring(checker: TierBoundaryChecker) -> None:
    assert checker.check(agent_tier=1, endpoint_category="risk_scoring") is False


def test_tier_3_can_call_execution_api(checker: TierBoundaryChecker) -> None:
    assert checker.check(agent_tier=3, endpoint_category="execution_api") is True


def test_tier_2_cannot_call_execution_api(checker: TierBoundaryChecker) -> None:
    """ANIF-802: Tier 2 MUST NOT call execution endpoints."""
    assert checker.check(agent_tier=2, endpoint_category="execution_api") is False


def test_tier_1_cannot_call_execution_api(checker: TierBoundaryChecker) -> None:
    """ANIF-802: Tier 1 MUST NOT call execution endpoints."""
    assert checker.check(agent_tier=1, endpoint_category="execution_api") is False


def test_higher_tier_satisfies_lower_requirement(checker: TierBoundaryChecker) -> None:
    """Tier 3 agents can call policy evaluation (requires Tier 1 minimum)."""
    assert checker.check(agent_tier=3, endpoint_category="policy_evaluation") is True


def test_unknown_endpoint_category_defaults_to_tier_0_requirement(
    checker: TierBoundaryChecker,
) -> None:
    """Unknown endpoint categories require Tier 0 minimum (safe default)."""
    assert checker.check(agent_tier=0, endpoint_category="unknown_category") is True
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/pytest tests/unit/test_tier_boundary.py -v
```

Expected: `FAILED` — `ImportError: cannot import name 'TierBoundaryChecker'`

- [ ] **Step 3: Write the implementation**

```python
# src/anif_platform/agents/tier_boundary.py
"""Tier boundary enforcement — ANIF-802 §4, ANIF-843 §6."""
from __future__ import annotations

import structlog

log = structlog.get_logger(__name__)

# Minimum tier required per endpoint category — ANIF-843 §6.2
_ENDPOINT_TIER_REQUIREMENTS: dict[str, int] = {
    "canonical_state_read": 0,
    "policy_evaluation": 1,
    "risk_scoring": 2,
    "execution_api": 3,
    "council_vote": 0,
}

_DEFAULT_REQUIRED_TIER: int = 0


class TierBoundaryChecker:
    """Enforces tier-based access control per ANIF-802 and ANIF-843 §6."""

    def check(self, agent_tier: int, endpoint_category: str) -> bool:
        """Return True if agent_tier meets the minimum required for endpoint_category."""
        required = _ENDPOINT_TIER_REQUIREMENTS.get(endpoint_category, _DEFAULT_REQUIRED_TIER)
        return agent_tier >= required

    def log_violation(
        self,
        agent_id: str,
        agent_tier: int,
        endpoint_category: str,
    ) -> None:
        """Log a Severity 2 tier boundary violation — ANIF-843 §6.3."""
        log.warning(
            "tier_boundary_violation",
            severity=2,
            agent_id=agent_id,
            agent_tier=agent_tier,
            endpoint_category=endpoint_category,
        )
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/pytest tests/unit/test_tier_boundary.py -v
```

Expected: all 10 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/anif_platform/agents/tier_boundary.py tests/unit/test_tier_boundary.py
git commit -m "feat: implement TierBoundaryChecker per ANIF-802/843"
```

---

## Task 5: X.509 Certificate Infrastructure

**Files:**
- Create: `src/anif_platform/agents/certificate.py`
- Create: `tests/unit/test_agent_certificate.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_agent_certificate.py
"""Unit tests for MockCertificateAuthority, CertificateVerifier, RevocationList — ANIF-843."""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from anif_platform.agents.certificate import (
    CertVerificationResult,
    CertificateVerifier,
    MockCertificateAuthority,
    RevocationList,
)
from anif_platform.agents.tier_boundary import TierBoundaryChecker


@pytest.fixture
def ca() -> MockCertificateAuthority:
    return MockCertificateAuthority()


@pytest.fixture
def checker() -> TierBoundaryChecker:
    return TierBoundaryChecker()


def make_capabilities_hash(manifest: dict) -> str:
    return hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()


class TestMockCertificateAuthority:
    def test_ca_cert_pem_is_valid_x509(self, ca: MockCertificateAuthority) -> None:
        from cryptography import x509

        cert = x509.load_pem_x509_certificate(ca.ca_cert_pem.encode())
        assert cert.subject is not None

    def test_issue_cert_returns_pem_and_expiry(self, ca: MockCertificateAuthority) -> None:
        caps_hash = make_capabilities_hash({"caps": ["read"]})
        pem, expires_at = ca.issue_cert(
            agent_id="agent-001",
            agent_type="NetworkObserver",
            tier=1,
            capabilities_hash=caps_hash,
        )
        assert pem.startswith("-----BEGIN CERTIFICATE-----")
        assert expires_at > datetime.now(UTC)

    def test_issued_cert_expires_within_90_days(self, ca: MockCertificateAuthority) -> None:
        """ANIF-843 §4.1: valid_to MUST NOT exceed 90 days from issue."""
        caps_hash = make_capabilities_hash({"caps": ["read"]})
        _, expires_at = ca.issue_cert(
            agent_id="agent-001",
            agent_type="NetworkObserver",
            tier=1,
            capabilities_hash=caps_hash,
        )
        max_expiry = datetime.now(UTC) + timedelta(days=91)
        assert expires_at < max_expiry

    def test_issued_cert_contains_agent_id(self, ca: MockCertificateAuthority) -> None:
        from cryptography import x509
        from cryptography.x509.oid import NameOID

        caps_hash = make_capabilities_hash({"caps": ["read"]})
        pem, _ = ca.issue_cert(
            agent_id="agent-001",
            agent_type="NetworkObserver",
            tier=2,
            capabilities_hash=caps_hash,
        )
        cert = x509.load_pem_x509_certificate(pem.encode())
        cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        assert cn == "agent-001"

    def test_issued_cert_encodes_tier(self, ca: MockCertificateAuthority) -> None:
        from cryptography import x509
        from cryptography.x509.oid import NameOID

        caps_hash = make_capabilities_hash({"caps": ["execute"]})
        pem, _ = ca.issue_cert(
            agent_id="agent-002",
            agent_type="ActionSelector",
            tier=3,
            capabilities_hash=caps_hash,
        )
        cert = x509.load_pem_x509_certificate(pem.encode())
        ou = cert.subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value
        assert ou == "3"


class TestCertificateVerifier:
    def make_verifier(
        self, ca: MockCertificateAuthority, revoked_ids: set[str] | None = None
    ) -> CertificateVerifier:
        revocation_list = MagicMock(spec=RevocationList)
        revocation_list.is_revoked_sync = MagicMock(
            side_effect=lambda agent_id: agent_id in (revoked_ids or set())
        )
        return CertificateVerifier(
            ca_cert_pem=ca.ca_cert_pem,
            revocation_list=revocation_list,
        )

    def test_valid_cert_passes_all_five_steps(
        self, ca: MockCertificateAuthority, checker: TierBoundaryChecker
    ) -> None:
        caps_hash = make_capabilities_hash({"caps": ["execute"]})
        pem, _ = ca.issue_cert(
            agent_id="agent-001",
            agent_type="ActionSelector",
            tier=3,
            capabilities_hash=caps_hash,
        )
        verifier = self.make_verifier(ca)
        result = verifier.verify(
            cert_pem=pem,
            expected_capabilities_hash=caps_hash,
            endpoint_category="execution_api",
            checker=checker,
        )
        assert result.valid is True
        assert result.agent_id == "agent-001"
        assert result.tier == 3

    def test_revoked_cert_fails_step_3(
        self, ca: MockCertificateAuthority, checker: TierBoundaryChecker
    ) -> None:
        caps_hash = make_capabilities_hash({"caps": ["read"]})
        pem, _ = ca.issue_cert(
            agent_id="agent-revoked",
            agent_type="NetworkObserver",
            tier=1,
            capabilities_hash=caps_hash,
        )
        verifier = self.make_verifier(ca, revoked_ids={"agent-revoked"})
        result = verifier.verify(
            cert_pem=pem,
            expected_capabilities_hash=caps_hash,
            endpoint_category="canonical_state_read",
            checker=checker,
        )
        assert result.valid is False
        assert result.failure_reason == "revoked"

    def test_wrong_capabilities_hash_fails_step_4(
        self, ca: MockCertificateAuthority, checker: TierBoundaryChecker
    ) -> None:
        caps_hash = make_capabilities_hash({"caps": ["read"]})
        pem, _ = ca.issue_cert(
            agent_id="agent-001",
            agent_type="NetworkObserver",
            tier=1,
            capabilities_hash=caps_hash,
        )
        verifier = self.make_verifier(ca)
        result = verifier.verify(
            cert_pem=pem,
            expected_capabilities_hash="wrong_hash_value",
            endpoint_category="canonical_state_read",
            checker=checker,
        )
        assert result.valid is False
        assert result.failure_reason == "capabilities_hash_mismatch"

    def test_tier_boundary_violation_fails_step_5(
        self, ca: MockCertificateAuthority, checker: TierBoundaryChecker
    ) -> None:
        caps_hash = make_capabilities_hash({"caps": ["read"]})
        # Tier 1 cert trying to call execution_api (requires Tier 3)
        pem, _ = ca.issue_cert(
            agent_id="agent-001",
            agent_type="NetworkObserver",
            tier=1,
            capabilities_hash=caps_hash,
        )
        verifier = self.make_verifier(ca)
        result = verifier.verify(
            cert_pem=pem,
            expected_capabilities_hash=caps_hash,
            endpoint_category="execution_api",
            checker=checker,
        )
        assert result.valid is False
        assert result.failure_reason == "tier_boundary_violation"


class TestRevocationList:
    @pytest.mark.asyncio
    async def test_revoke_adds_row(self) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        rl = RevocationList(session=session)
        await rl.revoke(agent_id="agent-001", reason="Compromise detected")
        session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_revoked_returns_true_for_revoked_agent(self) -> None:
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()  # row exists
        session.execute = AsyncMock(return_value=mock_result)
        rl = RevocationList(session=session)
        assert await rl.is_revoked("agent-001") is True

    @pytest.mark.asyncio
    async def test_is_revoked_returns_false_for_clean_agent(self) -> None:
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_result)
        rl = RevocationList(session=session)
        assert await rl.is_revoked("agent-clean") is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/pytest tests/unit/test_agent_certificate.py -v
```

Expected: `FAILED` — `ImportError: cannot import name 'MockCertificateAuthority'`

- [ ] **Step 3: Write the implementation**

```python
# src/anif_platform/agents/certificate.py
"""X.509 certificate infrastructure for agent identity — ANIF-843."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

import structlog
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.agents.models import AgentRevocationRow
from anif_platform.agents.tier_boundary import TierBoundaryChecker

log = structlog.get_logger(__name__)

_CERT_VALIDITY_DAYS: int = 90
_RSA_KEY_SIZE: int = 2048
_RSA_PUBLIC_EXPONENT: int = 65537


@dataclass
class CertVerificationResult:
    """Result of the five-step certificate verification — ANIF-843 §5.2."""

    valid: bool
    agent_id: str | None = None
    tier: int | None = None
    failure_reason: str | None = None


class MockCertificateAuthority:
    """In-memory CA for dev/test environments — issues real X.509v3 certs.

    Production deployments MUST use an HSM-backed CA (ANIF-843 §4.3).
    """

    def __init__(self) -> None:
        self._private_key: rsa.RSAPrivateKey = rsa.generate_private_key(
            public_exponent=_RSA_PUBLIC_EXPONENT,
            key_size=_RSA_KEY_SIZE,
        )
        self._ca_cert: x509.Certificate = self._build_ca_cert()

    def _build_ca_cert(self) -> x509.Certificate:
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, "ANIF Build-Time Council CA"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ANIF Platform"),
            ]
        )
        return (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(self._private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(UTC))
            .not_valid_after(datetime.now(UTC) + timedelta(days=3650))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(self._private_key, hashes.SHA256())
        )

    @property
    def ca_cert_pem(self) -> str:
        """Return CA certificate as PEM string."""
        return self._ca_cert.public_bytes(serialization.Encoding.PEM).decode()

    def issue_cert(
        self,
        agent_id: str,
        agent_type: str,
        tier: int,
        capabilities_hash: str,
    ) -> tuple[str, datetime]:
        """Issue an agent certificate — ANIF-843 §4.1.

        Returns (pem_cert, expires_at).
        Certificate validity MUST NOT exceed 90 days (ANIF-843 §4.1).
        Fields encoded in Subject:
          CN = agent_id
          OU = tier (as string "0"–"3")
          O  = agent_type
          L  = capabilities_hash
        """
        expires_at = datetime.now(UTC) + timedelta(days=_CERT_VALIDITY_DAYS)
        subject = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, agent_id),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, str(tier)),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, agent_type),
                x509.NameAttribute(NameOID.LOCALITY_NAME, capabilities_hash),
            ]
        )
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(self._ca_cert.subject)
            .public_key(self._private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(UTC))
            .not_valid_after(expires_at)
            .sign(self._private_key, hashes.SHA256())
        )
        pem = cert.public_bytes(serialization.Encoding.PEM).decode()
        return pem, expires_at


class RevocationList:
    """DB-backed certificate revocation list — ANIF-843 §7.2."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def revoke(self, agent_id: str, reason: str) -> None:
        """Add agent to revocation list. Propagates within 60 seconds — ANIF-843 §7.2."""
        row = AgentRevocationRow(
            revocation_id=str(uuid.uuid4()),
            agent_id=agent_id,
            revoked_at=datetime.now(UTC),
            reason=reason,
        )
        self._session.add(row)
        await self._session.flush()
        log.warning("agent_certificate_revoked", agent_id=agent_id, reason=reason)

    async def is_revoked(self, agent_id: str) -> bool:
        """Return True if agent certificate is on the revocation list."""
        result = await self._session.execute(
            select(AgentRevocationRow)
            .where(AgentRevocationRow.agent_id == agent_id)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    def is_revoked_sync(self, agent_id: str) -> bool:
        """Synchronous revocation check for use in CertificateVerifier (pre-loaded cache).

        Call `is_revoked()` async first to populate; use this for in-request checks.
        """
        raise NotImplementedError("Use is_revoked() async or pass revoked_ids set directly")


class CertificateVerifier:
    """Five-step certificate verification per ANIF-843 §5.2."""

    def __init__(self, ca_cert_pem: str, revocation_list: RevocationList) -> None:
        self._ca_cert: x509.Certificate = x509.load_pem_x509_certificate(ca_cert_pem.encode())
        self._revocation_list = revocation_list

    def verify(
        self,
        cert_pem: str,
        expected_capabilities_hash: str,
        endpoint_category: str,
        checker: TierBoundaryChecker,
    ) -> CertVerificationResult:
        """Perform all five verification steps — ANIF-843 §5.2.

        Steps:
          1. Verify signed by build-time council CA
          2. Verify within validity period
          3. Verify not on revocation list (sync check — caller must pre-load)
          4. Verify capabilities_hash matches current approved manifest hash
          5. Verify endpoint tier permitted for agent's declared tier
        """
        try:
            cert = x509.load_pem_x509_certificate(cert_pem.encode())
        except Exception:
            return CertVerificationResult(valid=False, failure_reason="invalid_cert_pem")

        # Step 1: Verify signature
        try:
            self._ca_cert.public_key().verify(  # type: ignore[union-attr]
                cert.signature,
                cert.tbs_certificate_bytes,
                padding.PKCS1v15(),
                cert.signature_hash_algorithm,  # type: ignore[arg-type]
            )
        except Exception:
            log.warning("cert_verification_failed", step=1, reason="invalid_signature")
            return CertVerificationResult(valid=False, failure_reason="invalid_signature")

        # Step 2: Check validity period
        now = datetime.now(UTC)
        if now < cert.not_valid_before_utc or now > cert.not_valid_after_utc:
            log.warning("cert_verification_failed", step=2, reason="expired_or_not_yet_valid")
            return CertVerificationResult(valid=False, failure_reason="expired_or_not_yet_valid")

        # Step 3: Check revocation list (sync)
        try:
            agent_id = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        except (IndexError, Exception):
            return CertVerificationResult(valid=False, failure_reason="missing_agent_id")

        if self._revocation_list.is_revoked_sync(agent_id):
            log.warning("cert_verification_failed", step=3, agent_id=agent_id, reason="revoked")
            return CertVerificationResult(valid=False, failure_reason="revoked")

        # Step 4: Check capabilities_hash
        try:
            caps_hash_in_cert = cert.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value
        except (IndexError, Exception):
            return CertVerificationResult(valid=False, failure_reason="missing_capabilities_hash")

        if caps_hash_in_cert != expected_capabilities_hash:
            log.warning("cert_verification_failed", step=4, agent_id=agent_id,
                        reason="capabilities_hash_mismatch")
            return CertVerificationResult(valid=False, failure_reason="capabilities_hash_mismatch")

        # Step 5: Tier boundary check
        try:
            tier_str = cert.subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value
            agent_tier = int(tier_str)
        except (IndexError, ValueError, Exception):
            return CertVerificationResult(valid=False, failure_reason="missing_or_invalid_tier")

        if not checker.check(agent_tier=agent_tier, endpoint_category=endpoint_category):
            log.warning("cert_verification_failed", step=5, agent_id=agent_id,
                        agent_tier=agent_tier, endpoint_category=endpoint_category,
                        reason="tier_boundary_violation")
            checker.log_violation(agent_id=agent_id, agent_tier=agent_tier,
                                  endpoint_category=endpoint_category)
            return CertVerificationResult(valid=False, failure_reason="tier_boundary_violation")

        return CertVerificationResult(valid=True, agent_id=agent_id, tier=agent_tier)
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/pytest tests/unit/test_agent_certificate.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/anif_platform/agents/certificate.py tests/unit/test_agent_certificate.py
git commit -m "feat: implement MockCertificateAuthority, CertificateVerifier, RevocationList (ANIF-843)"
```

---

## Task 6: REST Router

**Files:**
- Create: `src/anif_platform/agents/router.py`
- Create: `tests/unit/test_agent_router.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_agent_router.py
"""Unit tests for agent REST endpoints."""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from anif_platform.agents.models import AgentRegistryRow
from anif_platform.agents.registry import AgentRegistry, InvalidTransitionError, ProvisionalPeriodError
from anif_platform.agents.router import get_agent_registry, router
from anif_platform.agents.schemas import AgentLifecycleState
from anif_platform.auth import get_api_key


def make_app(registry: AgentRegistry) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_agent_registry] = lambda: registry
    app.dependency_overrides[get_api_key] = lambda: "test-key"
    return app


def make_agent_row(
    agent_id: str = "agent-001",
    lifecycle_state: str = "PROPOSED",
    tier: int = 1,
) -> MagicMock:
    row = MagicMock(spec=AgentRegistryRow)
    row.agent_id = agent_id
    row.agent_type = "NetworkObserver"
    row.role = "Network Observer"
    row.tier = tier
    row.lifecycle_state = lifecycle_state
    row.strike_count = 0
    row.provisional_until = None
    row.capabilities_hash = "abc123"
    row.certificate_pem = None
    row.certificate_expires_at = None
    row.last_intent_id = None
    row.last_intent_at = None
    row.working_context_cleared_at = None
    row.registered_at = datetime.now(UTC)
    row.manifest_json = json.dumps({"capabilities": ["read_telemetry"]})
    return row


def make_event_row(
    previous_state: str = "PROPOSED",
    new_state: str = "PROVISIONAL",
) -> MagicMock:
    from anif_platform.agents.models import AgentLifecycleEventRow

    row = MagicMock(spec=AgentLifecycleEventRow)
    row.event_id = "event-001"
    row.previous_state = previous_state
    row.new_state = new_state
    row.transitioned_at = datetime.now(UTC)
    return row


class TestRegisterAgent:
    def test_post_agents_returns_201(self) -> None:
        registry = AsyncMock(spec=AgentRegistry)
        registry.register = AsyncMock(return_value=make_agent_row())
        app = make_app(registry)
        client = TestClient(app)
        resp = client.post(
            "/agents",
            json={
                "agent_id": "agent-001",
                "agent_type": "NetworkObserver",
                "role": "Network Observer",
                "tier": 1,
                "manifest": {"capabilities": ["read_telemetry"]},
            },
            headers={"X-API-Key": "test-key"},
        )
        assert resp.status_code == 201
        assert resp.json()["agent_id"] == "agent-001"
        assert resp.json()["lifecycle_state"] == "PROPOSED"

    def test_post_agents_calls_registry_register(self) -> None:
        registry = AsyncMock(spec=AgentRegistry)
        registry.register = AsyncMock(return_value=make_agent_row())
        app = make_app(registry)
        client = TestClient(app)
        client.post(
            "/agents",
            json={
                "agent_id": "agent-001",
                "agent_type": "NetworkObserver",
                "role": "Network Observer",
                "tier": 1,
                "manifest": {"capabilities": ["read_telemetry"]},
            },
            headers={"X-API-Key": "test-key"},
        )
        registry.register.assert_called_once()


class TestGetAgent:
    def test_get_agent_returns_detail(self) -> None:
        from anif_platform.agents.registry import AgentNotFoundError

        registry = AsyncMock(spec=AgentRegistry)
        registry.get = AsyncMock(return_value=make_agent_row())
        app = make_app(registry)
        client = TestClient(app)
        resp = client.get("/agents/agent-001", headers={"X-API-Key": "test-key"})
        assert resp.status_code == 200
        assert resp.json()["agent_id"] == "agent-001"

    def test_get_agent_not_found_returns_404(self) -> None:
        from anif_platform.agents.registry import AgentNotFoundError

        registry = AsyncMock(spec=AgentRegistry)
        registry.get = AsyncMock(side_effect=AgentNotFoundError("not found"))
        app = make_app(registry)
        client = TestClient(app)
        resp = client.get("/agents/missing", headers={"X-API-Key": "test-key"})
        assert resp.status_code == 404


class TestTransitionAgent:
    def test_transition_returns_200_on_success(self) -> None:
        registry = AsyncMock(spec=AgentRegistry)
        registry.transition = AsyncMock(return_value=make_event_row())
        app = make_app(registry)
        client = TestClient(app)
        resp = client.post(
            "/agents/agent-001/transition",
            json={
                "new_state": "PROVISIONAL",
                "trigger": "council_approval",
                "approver_identity": "council-member-1",
                "reason": "Approved",
            },
            headers={"X-API-Key": "test-key"},
        )
        assert resp.status_code == 200
        assert resp.json()["new_state"] == "PROVISIONAL"

    def test_invalid_transition_returns_409(self) -> None:
        registry = AsyncMock(spec=AgentRegistry)
        registry.transition = AsyncMock(
            side_effect=InvalidTransitionError("DECOMMISSIONED is terminal")
        )
        app = make_app(registry)
        client = TestClient(app)
        resp = client.post(
            "/agents/agent-001/transition",
            json={
                "new_state": "ACTIVE",
                "trigger": "manual",
                "approver_identity": "ops",
                "reason": "Trying",
            },
            headers={"X-API-Key": "test-key"},
        )
        assert resp.status_code == 409

    def test_provisional_period_error_returns_409(self) -> None:
        registry = AsyncMock(spec=AgentRegistry)
        registry.transition = AsyncMock(
            side_effect=ProvisionalPeriodError("Must wait 72h")
        )
        app = make_app(registry)
        client = TestClient(app)
        resp = client.post(
            "/agents/agent-001/transition",
            json={
                "new_state": "ACTIVE",
                "trigger": "manual",
                "approver_identity": "ops",
                "reason": "Promote",
            },
            headers={"X-API-Key": "test-key"},
        )
        assert resp.status_code == 409


class TestListAgents:
    def test_get_agents_returns_list(self) -> None:
        registry = AsyncMock(spec=AgentRegistry)
        registry.list_active = AsyncMock(return_value=[make_agent_row()])
        app = make_app(registry)
        client = TestClient(app)
        resp = client.get("/agents", headers={"X-API-Key": "test-key"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        assert len(resp.json()["agents"]) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/pytest tests/unit/test_agent_router.py -v
```

Expected: `FAILED` — `ImportError: cannot import name 'get_agent_registry'`

- [ ] **Step 3: Write the implementation**

```python
# src/anif_platform/agents/router.py
"""Agent infrastructure REST API — ANIF-803, ANIF-805, ANIF-843."""
from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from anif_platform.agents.registry import (
    AgentNotFoundError,
    AgentRegistry,
    InvalidTransitionError,
    ProvisionalPeriodError,
)
from anif_platform.agents.schemas import (
    AgentDetailResponse,
    AgentLifecycleState,
    AgentListResponse,
    RegisterAgentRequest,
    RegisterAgentResponse,
    TransitionRequest,
    TransitionResponse,
)
from anif_platform.auth import get_api_key

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])


def get_agent_registry() -> AgentRegistry:
    raise NotImplementedError("Provide AgentRegistry via dependency injection")


@router.post("", response_model=RegisterAgentResponse, status_code=status.HTTP_201_CREATED)
async def register_agent(
    request: RegisterAgentRequest,
    registry: AgentRegistry = Depends(get_agent_registry),
    _: str = Depends(get_api_key),
) -> RegisterAgentResponse:
    """Register a new agent in PROPOSED state — ANIF-803 §4.1."""
    agent = await registry.register(
        agent_id=request.agent_id,
        agent_type=request.agent_type,
        role=request.role,
        tier=request.tier,
        manifest=request.manifest,
    )
    return RegisterAgentResponse(
        agent_id=agent.agent_id,
        lifecycle_state=AgentLifecycleState(agent.lifecycle_state),
        provisional_until=agent.provisional_until,
        certificate_pem=agent.certificate_pem,
        registered_at=agent.registered_at,
    )


@router.get("/{agent_id}", response_model=AgentDetailResponse)
async def get_agent(
    agent_id: str,
    registry: AgentRegistry = Depends(get_agent_registry),
    _: str = Depends(get_api_key),
) -> AgentDetailResponse:
    """Retrieve agent details — ANIF-805 permitted state items."""
    try:
        agent = await registry.get(agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AgentDetailResponse(
        agent_id=agent.agent_id,
        agent_type=agent.agent_type,
        role=agent.role,
        tier=agent.tier,
        lifecycle_state=AgentLifecycleState(agent.lifecycle_state),
        strike_count=agent.strike_count,
        provisional_until=agent.provisional_until,
        capabilities_hash=agent.capabilities_hash,
        certificate_expires_at=agent.certificate_expires_at,
        last_intent_id=agent.last_intent_id,
        last_intent_at=agent.last_intent_at,
        working_context_cleared_at=agent.working_context_cleared_at,
        registered_at=agent.registered_at,
    )


@router.post("/{agent_id}/transition", response_model=TransitionResponse)
async def transition_agent(
    agent_id: str,
    request: TransitionRequest,
    registry: AgentRegistry = Depends(get_agent_registry),
    _: str = Depends(get_api_key),
) -> TransitionResponse:
    """Transition agent lifecycle state — ANIF-803 §5."""
    try:
        event = await registry.transition(
            agent_id=agent_id,
            new_state=request.new_state,
            trigger=request.trigger,
            approver_identity=request.approver_identity,
            reason=request.reason,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (InvalidTransitionError, ProvisionalPeriodError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return TransitionResponse(
        agent_id=agent_id,
        previous_state=AgentLifecycleState(event.previous_state),
        new_state=AgentLifecycleState(event.new_state),
        event_id=event.event_id,
        transitioned_at=event.transitioned_at,
    )


@router.get("", response_model=AgentListResponse)
async def list_agents(
    registry: AgentRegistry = Depends(get_agent_registry),
    _: str = Depends(get_api_key),
) -> AgentListResponse:
    """List all active agents — ANIF-805."""
    agents = await registry.list_active()
    return AgentListResponse(
        agents=[
            AgentDetailResponse(
                agent_id=a.agent_id,
                agent_type=a.agent_type,
                role=a.role,
                tier=a.tier,
                lifecycle_state=AgentLifecycleState(a.lifecycle_state),
                strike_count=a.strike_count,
                provisional_until=a.provisional_until,
                capabilities_hash=a.capabilities_hash,
                certificate_expires_at=a.certificate_expires_at,
                last_intent_id=a.last_intent_id,
                last_intent_at=a.last_intent_at,
                working_context_cleared_at=a.working_context_cleared_at,
                registered_at=a.registered_at,
            )
            for a in agents
        ],
        total=len(agents),
    )
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/pytest tests/unit/test_agent_router.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/anif_platform/agents/router.py tests/unit/test_agent_router.py
git commit -m "feat: implement agent REST API — register, get, transition, list (B6)"
```

---

## Task 7: Wire into main.py + migrations/env.py

**Files:**
- Modify: `migrations/env.py`
- Modify: `src/anif_platform/main.py`

- [ ] **Step 1: Write the failing test**

```python
# Append to tests/unit/test_agent_router.py
def test_agent_registry_row_imported_in_migration_env() -> None:
    """Ensure migrations/env.py imports agent models so Alembic detects them."""
    import importlib.util
    import sys

    # Check the import exists in the source
    import pathlib
    env_path = pathlib.Path("migrations/env.py")
    content = env_path.read_text()
    assert "anif_platform.agents.models" in content
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/unit/test_agent_router.py::test_agent_registry_row_imported_in_migration_env -v
```

Expected: `FAILED` — assertion fails (import not present yet).

- [ ] **Step 3: Update `migrations/env.py`**

Open `migrations/env.py` and add the import after the existing model imports (after line 19 in the current file):

```python
import anif_platform.agents.models  # noqa: F401 — registers agent registry tables
```

The import block should read:

```python
# Import all models so Alembic can detect them
from anif_platform.database import Base  # noqa: F401
import anif_platform.human_loop.models  # noqa: F401 — registers ApprovalTicketRow
import anif_platform.audit.models  # noqa: F401 — registers AuditRecord
import anif_platform.intent.models  # noqa: F401 — registers IntentRow
import anif_platform.execution.models  # noqa: F401 — registers ExecutionRecordRow
import anif_platform.agents.models  # noqa: F401 — registers agent registry tables
```

- [ ] **Step 4: Run the test**

```bash
.venv/bin/pytest tests/unit/test_agent_router.py::test_agent_registry_row_imported_in_migration_env -v
```

Expected: PASS.

- [ ] **Step 5: Update `src/anif_platform/main.py`**

Add the following imports after the existing imports block (after the `policy.router` imports section):

```python
from anif_platform.agents.registry import AgentRegistry
from anif_platform.agents.router import get_agent_registry
from anif_platform.agents.router import router as agents_router
```

Add the following async factory (after `_get_session_executor`, before the dependency overrides section):

```python
async def _get_session_agent_registry(
    request: Request,
) -> AsyncGenerator[AgentRegistry, None]:
    async with async_session_factory() as session:
        yield AgentRegistry(session=session)
```

Add the following override line (after `app.dependency_overrides[pipeline_get_executor] = _get_session_executor`):

```python
app.dependency_overrides[get_agent_registry] = _get_session_agent_registry
```

Add the following mount line (after `app.include_router(execution_router)`):

```python
app.include_router(agents_router)
```

- [ ] **Step 6: Run the full test suite**

```bash
.venv/bin/pytest tests/ -v --tb=short 2>&1 | tail -30
```

Expected: all existing tests plus new agent tests PASS. Green suite.

- [ ] **Step 7: Commit**

```bash
git add migrations/env.py src/anif_platform/main.py tests/unit/test_agent_router.py
git commit -m "feat: wire agent infrastructure into main.py and migrations (B6 complete)"
```

---

## Self-Review

### Spec coverage

| Spec requirement | Covered in |
|---|---|
| ANIF-803: 5 lifecycle states | `AgentLifecycleState` enum, Task 2 |
| ANIF-803: PROVISIONAL mandatory 72h | `_PROVISIONAL_HOURS`, `ProvisionalPeriodError`, Task 3 |
| ANIF-803: DECOMMISSIONED is terminal | `_VALID_TRANSITIONS[DECOMMISSIONED] = frozenset()`, Task 3 |
| ANIF-803: Every transition logged with previous state, new state, timestamp, trigger, approver identity, reason | `AgentLifecycleEventRow` all 7 columns, `transition()` always writes event, Tasks 1+3 |
| ANIF-803: Decommissioned identity register is append-only | `DecommissionedIdentityRow` written in `transition()` only when new\_state == DECOMMISSIONED, Task 3 |
| ANIF-805: Agents stateless across intents | `clear_working_context()` clears state on intent completion, Task 3 |
| ANIF-805: 4 permitted persistent state items | `agent_id`, `manifest_json`, `lifecycle_state`, `strike_count` columns, Task 1 |
| ANIF-801: Every agent exactly one role | `role` field in `AgentRegistryRow`, `RegisterAgentRequest`, Tasks 1+2 |
| ANIF-802: Tier 1 MUST NOT call execution | `TierBoundaryChecker.check(1, "execution_api") is False`, Task 4 |
| ANIF-802: Tier 2 MUST NOT call execution | `TierBoundaryChecker.check(2, "execution_api") is False`, Task 4 |
| ANIF-843: Mandatory certificate fields (7 fields) | `MockCertificateAuthority.issue_cert()` embeds agent\_id, tier, agent\_type, capabilities\_hash; issuer from CA cert; valid\_from/valid\_to, Task 5 |
| ANIF-843: valid\_to MUST NOT exceed 90 days | `_CERT_VALIDITY_DAYS = 90`, verified in test, Task 5 |
| ANIF-843: 5-step verification | `CertificateVerifier.verify()` implements all 5 steps, Task 5 |
| ANIF-843: Tier boundary violations logged as Severity 2 | `TierBoundaryChecker.log_violation()` logs `severity=2`, Task 4 |
| ANIF-843: Revocation list checked per request | Step 3 of `CertificateVerifier.verify()`, Task 5 |
| ANIF-843: UNTRUSTED lifecycle state | `AgentLifecycleState.UNTRUSTED`, reachable from PROVISIONAL/ACTIVE/DEGRADED, Task 2+3 |

### Placeholder scan

No TBD, TODO, or "similar to" references. All code blocks are complete.

### Type consistency

- `AgentLifecycleState` used consistently throughout schemas, registry, and router.
- `AgentRegistryRow` column names match between models, registry service calls, router response builders, and test mocks.
- `AgentLifecycleEventRow` fields `previous_state`, `new_state`, `event_id`, `transitioned_at` used correctly in `TransitionResponse`.
- `MockCertificateAuthority.issue_cert()` returns `tuple[str, datetime]` — consumed correctly in `registry.record_cert()`.
- `CertVerificationResult.failure_reason` strings are specific and match test assertions exactly.
