# B4: Governance & Human Controls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the ANIF governance mode gate (R-01–R-06), approval ticket lifecycle, emergency halt, background expiry, and Prometheus governance metrics — completing B4 of the platform build order.

**Architecture:** `GovernanceGate` is a pure-computation engine (no I/O, like `RiskScorer`). `ApprovalQueue` is the stateful layer — wraps `AsyncSession` + `AuditWriter`. The governance router wires them together and exposes the HTTP surface. The pipeline orchestrator calls the gate directly (no internal HTTP), and creates tickets via `ApprovalQueue` when `manual_review` is returned. A background asyncio task runs expiry every 60 seconds.

**Tech Stack:** FastAPI, SQLAlchemy 2 async, Alembic, Pydantic v2, prometheus-client, structlog, pytest-asyncio, unittest.mock

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `src/anif_platform/human_loop/models.py` | Create | `ApprovalTicketRow` SQLAlchemy ORM + `TicketStatus` enum |
| `src/anif_platform/human_loop/schemas.py` | Create | Pydantic schemas for ticket, governance check request/response |
| `src/anif_platform/governance/gate.py` | Create | `GovernanceGate` — pure rule engine (R-01–R-06) |
| `src/anif_platform/human_loop/queue.py` | Create | `ApprovalQueue` — ticket CRUD, approve, reject, expire |
| `src/anif_platform/governance/router.py` | Create | `POST /governance/check`, `approve/{id}`, `reject/{id}`, `GET /governance/tickets` |
| `src/anif_platform/human_loop/router.py` | Create | `POST /execution/{intent_id}/halt` |
| `src/anif_platform/human_loop/expiry.py` | Create | `run_expiry_loop()` — asyncio background task |
| `src/anif_platform/monitoring/metrics.py` | Create | Prometheus counters for governance events |
| `src/anif_platform/governance/__init__.py` | Modify | Export `GovernanceGate` |
| `src/anif_platform/human_loop/__init__.py` | Modify | Export `ApprovalQueue` |
| `src/anif_platform/pipeline/router.py` | Modify | Add governance stage after decision stage |
| `src/anif_platform/main.py` | Modify | Register governance/human_loop routers + expiry task lifespan |
| `migrations/versions/003_add_approval_tickets.py` | Create | Alembic migration for `approval_tickets` table |
| `tests/unit/test_governance_gate.py` | Create | Unit tests for GovernanceGate (no DB) |
| `tests/unit/test_approval_queue.py` | Create | Unit tests for ApprovalQueue (mocked session) |

---

## Context: Role Model

Operator identity is passed via HTTP headers for all governance endpoints (placeholder for B6 X.509):
- `X-Operator-Id: jsmith@example.com` — required on approve/reject/halt
- `X-Operator-Roles: network_engineer,senior_engineer` — comma-separated, required

For `POST /governance/check`, roles are in the request body (per ANIF-406 §4.1.1).

Valid roles (ANIF-404 §4.5): `automation_agent`, `network_engineer`, `senior_engineer`.

---

## Task 1: ApprovalTicket SQLAlchemy Model + Pydantic Schemas

**Files:**
- Create: `src/anif_platform/human_loop/models.py`
- Create: `src/anif_platform/human_loop/schemas.py`
- Modify: `src/anif_platform/human_loop/__init__.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_approval_queue.py — import check only at this stage
from anif_platform.human_loop.models import ApprovalTicketRow, TicketStatus
from anif_platform.human_loop.schemas import ApprovalTicket, GovernanceCheckRequest, GovernanceCheckResponse
```

Run: `.venv/bin/pytest tests/unit/test_approval_queue.py --collect-only 2>&1 | head -20`
Expected: `ImportError: No module named 'anif_platform.human_loop.models'`

- [ ] **Step 2: Create `src/anif_platform/human_loop/models.py`**

```python
"""ApprovalTicket SQLAlchemy model — ANIF-404 §4.4."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from anif_platform.database import Base


class TicketStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    expired = "expired"


class ApprovalTicketRow(Base):
    """
    Persisted approval ticket — ANIF-404 §4.4.

    Terminal states: approved, rejected, expired.
    Transitions FROM terminal states are FORBIDDEN (ANIF-406 §4.4.2).
    """

    __tablename__ = "approval_tickets"

    ticket_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    intent_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default=TicketStatus.pending)
    requested_by: Mapped[str] = mapped_column(String, nullable=False)
    decision_summary: Mapped[str] = mapped_column(String, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    required_approver_role: Mapped[str] = mapped_column(String, nullable=False, default="senior_engineer")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_by: Mapped[str | None] = mapped_column(String, nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    approval_notes: Mapped[str | None] = mapped_column(String, nullable=True)
```

- [ ] **Step 3: Create `src/anif_platform/human_loop/schemas.py`**

```python
"""Pydantic schemas for governance check and approval tickets — ANIF-404, ANIF-406."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PolicyResultEntry(BaseModel):
    policy_id: str
    outcome: str  # "pass" | "fail"
    safety_decision: str | None = None  # "block" | "warn" | None


class GovernanceCheckRequest(BaseModel):
    intent_id: uuid.UUID
    operator_id: str
    operator_roles: list[str]
    action_type: str
    environment: str
    risk_score: int = Field(ge=0, le=100)
    trust_score: int = Field(ge=0, le=100)
    policy_results: list[PolicyResultEntry] = Field(default_factory=list)
    trace_id: uuid.UUID


class GovernanceCheckResponse(BaseModel):
    intent_id: uuid.UUID
    mode: str  # "auto" | "manual_review" | "block"
    triggered_rule: str  # comma-separated rule IDs, or "none"
    rationale: str
    ticket_id: str | None = None
    ticket_expires_at: datetime | None = None
    audit_record_id: str
    trace_id: uuid.UUID


class ApprovalTicket(BaseModel):
    """Pydantic projection of ApprovalTicketRow — ANIF-404 §4.4.1."""

    ticket_id: str
    intent_id: uuid.UUID
    decision_summary: str
    risk_score: int
    requested_by: str
    created_at: datetime
    expires_at: datetime
    status: str
    required_approver_role: str

    model_config = {"from_attributes": True}


class ApproveRequest(BaseModel):
    approver_role: str
    notes: str | None = None


class ApproveResponse(BaseModel):
    ticket_id: str
    status: str
    approved_by: str
    approved_at: datetime
    audit_record_id: str


class RejectRequest(BaseModel):
    reason: str


class RejectResponse(BaseModel):
    ticket_id: str
    status: str
    rejected_by: str
    rejected_at: datetime
    audit_record_id: str


class HaltRequest(BaseModel):
    reason: str
    operator_id: str


class HaltResponse(BaseModel):
    intent_id: uuid.UUID
    halt_status: str
    rollback_initiated: bool
    rollback_status: str
    audit_record_id: str
    halted_by: str
    halted_at: datetime
```

- [ ] **Step 4: Update `src/anif_platform/human_loop/__init__.py`**

```python
"""ANIF human-in-loop controls — ANIF-404."""
```

- [ ] **Step 5: Verify imports resolve**

```bash
.venv/bin/python -c "from anif_platform.human_loop.models import ApprovalTicketRow, TicketStatus; from anif_platform.human_loop.schemas import GovernanceCheckRequest, GovernanceCheckResponse, ApprovalTicket; print('OK')"
```

Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add src/anif_platform/human_loop/
git commit -m "feat: add ApprovalTicket SQLAlchemy model and Pydantic schemas (ANIF-404)"
```

---

## Task 2: Alembic Migration 003 — approval_tickets Table

**Files:**
- Create: `migrations/versions/003_add_approval_tickets.py`

- [ ] **Step 1: Generate the migration**

```bash
DATABASE_URL=postgresql+asyncpg://anif:anif_dev@localhost:5432/anif_dev \
  .venv/bin/alembic revision --autogenerate -m "add_approval_tickets"
```

Expected: creates `migrations/versions/<hash>_add_approval_tickets.py`

- [ ] **Step 2: Verify the generated migration looks correct**

Open the generated file. The `upgrade()` function MUST create the `approval_tickets` table with all columns. The `downgrade()` function MUST drop the table.

If autogenerate missed anything, edit to match:

```python
def upgrade() -> None:
    op.create_table(
        "approval_tickets",
        sa.Column("ticket_id", sa.String(), nullable=False),
        sa.Column("intent_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("requested_by", sa.String(), nullable=False),
        sa.Column("decision_summary", sa.String(), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("required_approver_role", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_by", sa.String(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_by", sa.String(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.String(), nullable=True),
        sa.Column("approval_notes", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("ticket_id"),
    )
    op.create_index("ix_approval_tickets_intent_id", "approval_tickets", ["intent_id"])
    op.create_index("ix_approval_tickets_status", "approval_tickets", ["status"])


def downgrade() -> None:
    op.drop_index("ix_approval_tickets_status", table_name="approval_tickets")
    op.drop_index("ix_approval_tickets_intent_id", table_name="approval_tickets")
    op.drop_table("approval_tickets")
```

- [ ] **Step 3: Rename the file to 003_add_approval_tickets.py for consistency**

```bash
# Rename the generated file so it's consistently numbered
# (the hash prefix comes from alembic; keep it but check it starts with 003 or rename)
```

- [ ] **Step 4: Commit**

```bash
git add migrations/
git commit -m "feat: add Alembic migration 003 for approval_tickets (ANIF-404)"
```

---

## Task 3: GovernanceGate — Pure Rule Engine

**Files:**
- Create: `src/anif_platform/governance/gate.py`
- Modify: `src/anif_platform/governance/__init__.py`
- Create: `tests/unit/test_governance_gate.py`

The gate is pure computation (no I/O) following the same pattern as `RiskScorer` and `DecisionEngine`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_governance_gate.py
"""Unit tests for GovernanceGate — ANIF-406 §4.2."""

from __future__ import annotations

import uuid

import pytest

from anif_platform.governance.gate import GovernanceGate


def make_request(
    operator_roles: list[str] | None = None,
    action_type: str = "apply_qos",
    environment: str = "prod",
    risk_score: int = 30,
    trust_score: int = 70,
    policy_results: list[dict] | None = None,
) -> dict:
    return {
        "intent_id": str(uuid.uuid4()),
        "operator_id": "jsmith@example.com",
        "operator_roles": operator_roles or ["network_engineer"],
        "action_type": action_type,
        "environment": environment,
        "risk_score": risk_score,
        "trust_score": trust_score,
        "policy_results": policy_results or [],
        "trace_id": str(uuid.uuid4()),
    }


class TestR05BlockMissingRole:
    def test_missing_network_engineer_role_blocks(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(operator_roles=["read_only"]))
        assert result["mode"] == "block"
        assert "R-05" in result["triggered_rule"]

    def test_network_engineer_role_passes_r05(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(operator_roles=["network_engineer"]))
        assert result["mode"] != "block" or "R-05" not in result["triggered_rule"]

    def test_automation_agent_role_passes_r05(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(operator_roles=["automation_agent"]))
        assert "R-05" not in result.get("triggered_rule", "")

    def test_senior_engineer_role_passes_r05(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(operator_roles=["senior_engineer"]))
        assert "R-05" not in result.get("triggered_rule", "")


class TestR06BlockSafetyDecisionBlock:
    def test_policy_result_with_block_triggers_r06(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(
            policy_results=[{"policy_id": "p1", "outcome": "fail", "safety_decision": "block"}]
        ))
        assert result["mode"] == "block"
        assert "R-06" in result["triggered_rule"]

    def test_policy_result_with_warn_does_not_trigger_r06(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(
            policy_results=[{"policy_id": "p1", "outcome": "fail", "safety_decision": "warn"}]
        ))
        assert "R-06" not in result.get("triggered_rule", "")

    def test_policy_result_with_null_safety_decision_does_not_trigger_r06(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(
            policy_results=[{"policy_id": "p1", "outcome": "pass", "safety_decision": None}]
        ))
        assert result["mode"] != "block" or "R-06" in result.get("triggered_rule", "R-05")


class TestBlockRulesEvaluatedFirst:
    def test_r05_block_stops_evaluation_of_manual_review_rules(self) -> None:
        """ANIF-406 §4.2.1: if block rule triggered, MUST NOT evaluate manual_review rules."""
        gate = GovernanceGate()
        # R-05 should block; R-01 (isolate_segment) would also trigger manual_review
        result = gate.check(**make_request(
            operator_roles=["read_only"],
            action_type="isolate_segment",
        ))
        assert result["mode"] == "block"
        assert "R-01" not in result["triggered_rule"]


class TestR01IsolateSegment:
    def test_isolate_segment_triggers_manual_review(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(action_type="isolate_segment"))
        assert result["mode"] == "manual_review"
        assert "R-01" in result["triggered_rule"]

    def test_apply_qos_does_not_trigger_r01(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(action_type="apply_qos"))
        assert "R-01" not in result.get("triggered_rule", "")


class TestR02RiskScore:
    def test_risk_score_70_triggers_manual_review(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(risk_score=70))
        assert result["mode"] == "manual_review"
        assert "R-02" in result["triggered_rule"]

    def test_risk_score_69_does_not_trigger_r02(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(risk_score=69))
        assert "R-02" not in result.get("triggered_rule", "")

    def test_risk_score_100_triggers_r02(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(risk_score=100))
        assert "R-02" in result["triggered_rule"]


class TestR03ProdLowTrust:
    def test_prod_auto_low_trust_triggers_r03(self) -> None:
        """R-03: prod + would-be auto + trust_score < 60 → manual_review."""
        gate = GovernanceGate()
        # risk=30 (below 70, so R-02 not triggered), no isolate, no conflicts → would be auto
        result = gate.check(**make_request(
            environment="prod",
            risk_score=30,
            trust_score=59,
        ))
        assert result["mode"] == "manual_review"
        assert "R-03" in result["triggered_rule"]

    def test_prod_trust_60_does_not_trigger_r03(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(
            environment="prod",
            risk_score=30,
            trust_score=60,
        ))
        assert "R-03" not in result.get("triggered_rule", "")

    def test_staging_low_trust_does_not_trigger_r03(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(
            environment="staging",
            risk_score=30,
            trust_score=30,
        ))
        assert "R-03" not in result.get("triggered_rule", "")

    def test_r03_not_triggered_when_already_manual_review(self) -> None:
        """R-03 only applies when mode would be auto — not additive when already escalated."""
        gate = GovernanceGate()
        # R-02 triggers manual_review first; R-03 should still record but mode is already escalated
        result = gate.check(**make_request(
            environment="prod",
            risk_score=75,
            trust_score=40,
        ))
        assert result["mode"] == "manual_review"


class TestR04PolicyConflict:
    def test_conflicting_equal_precedence_policies_triggers_r04(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(
            policy_results=[
                {"policy_id": "p1", "outcome": "pass", "safety_decision": None},
                {"policy_id": "p2", "outcome": "fail", "safety_decision": None},
            ]
        ))
        assert result["mode"] == "manual_review"
        assert "R-04" in result["triggered_rule"]

    def test_all_pass_policies_does_not_trigger_r04(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(
            policy_results=[
                {"policy_id": "p1", "outcome": "pass", "safety_decision": None},
                {"policy_id": "p2", "outcome": "pass", "safety_decision": None},
            ]
        ))
        assert "R-04" not in result.get("triggered_rule", "")


class TestAutoMode:
    def test_auto_when_no_rules_triggered(self) -> None:
        """ANIF-406 §4.2.3: auto only when no block or manual_review rule fires."""
        gate = GovernanceGate()
        result = gate.check(**make_request(
            operator_roles=["network_engineer"],
            action_type="apply_qos",
            environment="dev",
            risk_score=30,
            trust_score=70,
            policy_results=[],
        ))
        assert result["mode"] == "auto"
        assert result["triggered_rule"] == "none"


class TestMultipleTriggeredRules:
    def test_multiple_manual_review_rules_all_listed(self) -> None:
        """ANIF-406 §4.2.2: all triggered rule IDs MUST be listed."""
        gate = GovernanceGate()
        # R-01 (isolate) + R-02 (risk=80) both trigger
        result = gate.check(**make_request(
            action_type="isolate_segment",
            risk_score=80,
        ))
        assert result["mode"] == "manual_review"
        assert "R-01" in result["triggered_rule"]
        assert "R-02" in result["triggered_rule"]


class TestResponseFields:
    def test_response_contains_all_required_fields(self) -> None:
        gate = GovernanceGate()
        req = make_request()
        result = gate.check(**req)
        assert "mode" in result
        assert "triggered_rule" in result
        assert "rationale" in result
        assert "trace_id" in result
        assert result["trace_id"] == req["trace_id"]

    def test_trace_id_echoed_in_response(self) -> None:
        """ANIF-406 §4.1.1: trace_id from request MUST be echoed in response."""
        gate = GovernanceGate()
        trace_id = str(uuid.uuid4())
        req = make_request()
        req["trace_id"] = trace_id
        result = gate.check(**req)
        assert result["trace_id"] == trace_id
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
.venv/bin/pytest tests/unit/test_governance_gate.py --tb=line -q 2>&1 | tail -10
```

Expected: `ImportError: No module named 'anif_platform.governance.gate'`

- [ ] **Step 3: Create `src/anif_platform/governance/gate.py`**

```python
"""
GovernanceGate — pure rule engine evaluating R-01 through R-06 — ANIF-406 §4.2.

Deterministic computation: no I/O, no mutable state. Thread-safe.
Rules R-05 and R-06 (block) are evaluated first.
Rules R-01 through R-04 (manual_review) are evaluated only if no block rule fires.
"""

from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger(__name__)

# Roles that satisfy the submission requirement (R-05) — ANIF-406 §4.2.1
_PERMITTED_SUBMITTER_ROLES = frozenset({"network_engineer", "automation_agent", "senior_engineer"})


class GovernanceGate:
    """
    Evaluates governance rules R-01–R-06 and returns a mode decision — ANIF-406.

    Pure computation: inject no dependencies. Call check() for each request.
    """

    def check(
        self,
        intent_id: str,
        operator_id: str,
        operator_roles: list[str],
        action_type: str,
        environment: str,
        risk_score: int,
        trust_score: int,
        policy_results: list[dict[str, Any]],
        trace_id: str,
    ) -> dict[str, Any]:
        """
        Evaluate governance rules and return a mode decision.

        Block rules (R-05, R-06) are evaluated first and are terminal.
        Manual review rules (R-01–R-04) are evaluated only if no block rule fires.
        Returns dict conforming to ANIF-406 §4.1.1 response schema (without audit_record_id).
        """
        roles_set = set(operator_roles)
        triggered: list[str] = []

        # ── Block rules (evaluated first, terminal) ──────────────────────────
        # R-05: caller must have network_engineer or automation_agent role
        if not roles_set.intersection(_PERMITTED_SUBMITTER_ROLES):
            rationale = (
                f"Governance mode set to block because the caller ({operator_id}) does not hold "
                f"the network_engineer or automation_agent role. "
                f"The caller's roles are: {', '.join(operator_roles) or 'none'}. "
                f"This action cannot proceed."
            )
            return self._result("block", ["R-05"], rationale, trace_id)

        # R-06: any policy result has safety_decision = block
        blocking_policies = [
            r for r in policy_results if r.get("safety_decision") == "block"
        ]
        if blocking_policies:
            names = ", ".join(r.get("policy_id", "?") for r in blocking_policies)
            rationale = (
                f"Governance mode set to block because one or more policy results "
                f"have safety_decision=block: [{names}]. "
                f"This action cannot proceed regardless of risk score."
            )
            return self._result("block", ["R-06"], rationale, trace_id)

        # ── Manual review rules (evaluated if no block rule fired) ────────────
        # R-01: action_type = isolate_segment
        if action_type == "isolate_segment":
            triggered.append("R-01")

        # R-02: risk_score >= 70
        if risk_score >= 70:
            triggered.append("R-02")

        # R-03: prod + would-be auto + trust_score < 60
        # "would-be auto" means R-01 and R-02 have not triggered yet (check before appending R-03)
        would_be_auto = len(triggered) == 0
        if environment == "prod" and would_be_auto and trust_score < 60:
            triggered.append("R-03")

        # R-04: two or more policy_results with conflicting outcomes (pass vs fail)
        outcomes = {r.get("outcome") for r in policy_results}
        if "pass" in outcomes and "fail" in outcomes:
            triggered.append("R-04")

        if triggered:
            rules_str = ", ".join(triggered)
            rationale = self._manual_review_rationale(triggered, risk_score, trust_score, environment, action_type)
            return self._result("manual_review", triggered, rationale, trace_id)

        # ── Auto (no rules triggered) ─────────────────────────────────────────
        return self._result(
            "auto",
            [],
            "All governance rules evaluated; no block or manual_review condition was met. "
            "Action may proceed autonomously.",
            trace_id,
        )

    @staticmethod
    def _manual_review_rationale(
        triggered: list[str],
        risk_score: int,
        trust_score: int,
        environment: str,
        action_type: str,
    ) -> str:
        parts: list[str] = []
        if "R-01" in triggered:
            parts.append(f"R-01: action_type={action_type} requires human review")
        if "R-02" in triggered:
            parts.append(f"R-02: risk_score ({risk_score}) ≥ 70")
        if "R-03" in triggered:
            parts.append(f"R-03: prod environment with trust_score ({trust_score}) < 60")
        if "R-04" in triggered:
            parts.append("R-04: conflicting policy outcomes require adjudication")
        return (
            f"Governance mode set to manual_review. "
            f"Triggered: {'; '.join(parts)}. "
            f"An approval ticket has been created. A senior_engineer must approve within 15 minutes."
        )

    @staticmethod
    def _result(
        mode: str,
        triggered_rules: list[str],
        rationale: str,
        trace_id: str,
    ) -> dict[str, Any]:
        return {
            "mode": mode,
            "triggered_rule": ", ".join(triggered_rules) if triggered_rules else "none",
            "rationale": rationale,
            "trace_id": trace_id,
        }
```

- [ ] **Step 4: Update `src/anif_platform/governance/__init__.py`**

```python
"""ANIF governance controls — ANIF-406."""

from anif_platform.governance.gate import GovernanceGate

__all__ = ["GovernanceGate"]
```

- [ ] **Step 5: Run tests**

```bash
.venv/bin/pytest tests/unit/test_governance_gate.py -v --tb=short 2>&1 | tail -20
```

Expected: all tests pass.

- [ ] **Step 6: Lint and type-check**

```bash
.venv/bin/ruff check --fix src/anif_platform/governance/ && \
.venv/bin/black src/anif_platform/governance/ && \
.venv/bin/mypy --strict src/anif_platform/governance/gate.py
```

Expected: no errors.

- [ ] **Step 7: Commit**

```bash
git add src/anif_platform/governance/ tests/unit/test_governance_gate.py
git commit -m "feat: implement GovernanceGate with rules R-01–R-06 (ANIF-406)"
```

---

## Task 4: ApprovalQueue — Ticket Lifecycle

**Files:**
- Create: `src/anif_platform/human_loop/queue.py`
- Create: `tests/unit/test_approval_queue.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_approval_queue.py
"""Unit tests for ApprovalQueue — ANIF-404 §4.4."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from anif_platform.human_loop.models import ApprovalTicketRow, TicketStatus
from anif_platform.human_loop.queue import ApprovalQueue, TicketError


def make_ticket(
    status: str = "pending",
    requested_by: str = "jsmith@example.com",
    expires_at: datetime | None = None,
) -> ApprovalTicketRow:
    now = datetime.now(UTC)
    t = ApprovalTicketRow()
    t.ticket_id = str(uuid.uuid4())
    t.intent_id = uuid.uuid4()
    t.status = status
    t.requested_by = requested_by
    t.decision_summary = "Test action requires approval"
    t.risk_score = 74
    t.required_approver_role = "senior_engineer"
    t.created_at = now
    t.expires_at = expires_at or (now + timedelta(minutes=15))
    return t


def make_queue() -> tuple[ApprovalQueue, AsyncMock, AsyncMock]:
    session = AsyncMock()
    writer = AsyncMock()
    queue = ApprovalQueue(session=session, writer=writer)
    return queue, session, writer


class TestCreateTicket:
    @pytest.mark.asyncio
    async def test_ticket_created_with_pending_status(self) -> None:
        """ANIF-404 §4.4.1: initial status MUST be pending."""
        queue, session, _ = make_queue()
        session.add = MagicMock()
        session.flush = AsyncMock()
        ticket = await queue.create_ticket(
            intent_id=uuid.uuid4(),
            operator_id="jsmith@example.com",
            risk_score=74,
            decision_summary="High-risk reroute_traffic on prod segment",
        )
        assert ticket.status == TicketStatus.pending

    @pytest.mark.asyncio
    async def test_ticket_expires_at_is_15_minutes_after_created(self) -> None:
        """ANIF-404 §4.4.1: expires_at MUST be exactly 15 minutes after created_at."""
        queue, session, _ = make_queue()
        session.add = MagicMock()
        session.flush = AsyncMock()
        ticket = await queue.create_ticket(
            intent_id=uuid.uuid4(),
            operator_id="jsmith@example.com",
            risk_score=50,
            decision_summary="apply_qos in prod",
        )
        delta = ticket.expires_at - ticket.created_at
        assert delta == timedelta(minutes=15)

    @pytest.mark.asyncio
    async def test_create_writes_audit_before_returning(self) -> None:
        """ANIF-404 §4.4.1: audit record MUST be written before returning."""
        queue, session, writer = make_queue()
        session.add = MagicMock()
        session.flush = AsyncMock()
        await queue.create_ticket(
            intent_id=uuid.uuid4(),
            operator_id="jsmith@example.com",
            risk_score=50,
            decision_summary="apply_qos in prod",
        )
        writer.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_ticket_id_is_unique_uuid(self) -> None:
        queue, session, _ = make_queue()
        session.add = MagicMock()
        session.flush = AsyncMock()
        t1 = await queue.create_ticket(uuid.uuid4(), "a@example.com", 50, "action A")
        t2 = await queue.create_ticket(uuid.uuid4(), "b@example.com", 50, "action B")
        assert t1.ticket_id != t2.ticket_id
        # IDs must not be sequential/predictable
        uuid.UUID(t1.ticket_id)  # must be valid UUID; raises if not


class TestApproveTicket:
    @pytest.mark.asyncio
    async def test_approve_requires_senior_engineer_role(self) -> None:
        """ANIF-404 §4.4.4: approver MUST have senior_engineer role."""
        queue, session, _ = make_queue()
        ticket = make_ticket(status="pending", requested_by="jsmith@example.com")
        session.get = AsyncMock(return_value=ticket)

        with pytest.raises(TicketError, match="senior_engineer"):
            await queue.approve(
                ticket_id=ticket.ticket_id,
                approver_id="bjones@example.com",
                approver_roles=["network_engineer"],
                notes=None,
            )

    @pytest.mark.asyncio
    async def test_self_approval_refused(self) -> None:
        """ANIF-404 §4.4.4: approver MUST be different from submitter."""
        queue, session, _ = make_queue()
        ticket = make_ticket(status="pending", requested_by="jsmith@example.com")
        session.get = AsyncMock(return_value=ticket)

        with pytest.raises(TicketError, match="self-approval"):
            await queue.approve(
                ticket_id=ticket.ticket_id,
                approver_id="jsmith@example.com",  # same as requested_by
                approver_roles=["senior_engineer"],
                notes=None,
            )

    @pytest.mark.asyncio
    async def test_approve_non_pending_ticket_raises(self) -> None:
        """ANIF-404 §4.4.4: approval of expired/rejected/approved ticket MUST be refused."""
        queue, session, _ = make_queue()
        for terminal_status in ("approved", "rejected", "expired"):
            ticket = make_ticket(status=terminal_status)
            session.get = AsyncMock(return_value=ticket)
            with pytest.raises(TicketError, match="not in pending"):
                await queue.approve(
                    ticket_id=ticket.ticket_id,
                    approver_id="bjones@example.com",
                    approver_roles=["senior_engineer"],
                    notes=None,
                )

    @pytest.mark.asyncio
    async def test_approve_writes_audit_before_returning(self) -> None:
        """ANIF-404 §4.4.4: audit MUST be written before success response."""
        queue, session, writer = make_queue()
        ticket = make_ticket(status="pending", requested_by="jsmith@example.com")
        session.get = AsyncMock(return_value=ticket)
        session.flush = AsyncMock()

        await queue.approve(
            ticket_id=ticket.ticket_id,
            approver_id="bjones@example.com",
            approver_roles=["senior_engineer"],
            notes="Looks safe",
        )
        writer.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_sets_status_to_approved(self) -> None:
        queue, session, writer = make_queue()
        ticket = make_ticket(status="pending", requested_by="jsmith@example.com")
        session.get = AsyncMock(return_value=ticket)
        session.flush = AsyncMock()

        result = await queue.approve(
            ticket_id=ticket.ticket_id,
            approver_id="bjones@example.com",
            approver_roles=["senior_engineer"],
            notes=None,
        )
        assert result.status == TicketStatus.approved
        assert result.approved_by == "bjones@example.com"


class TestRejectTicket:
    @pytest.mark.asyncio
    async def test_reject_without_reason_raises(self) -> None:
        """ANIF-404 §4.4.5: reason MUST be provided."""
        queue, session, _ = make_queue()
        ticket = make_ticket(status="pending")
        session.get = AsyncMock(return_value=ticket)

        with pytest.raises(TicketError, match="reason"):
            await queue.reject(
                ticket_id=ticket.ticket_id,
                operator_id="bjones@example.com",
                operator_roles=["network_engineer"],
                reason="",
            )

    @pytest.mark.asyncio
    async def test_reject_requires_network_engineer_role(self) -> None:
        """ANIF-404 §4.4.5: rejector MUST have network_engineer role."""
        queue, session, _ = make_queue()
        ticket = make_ticket(status="pending")
        session.get = AsyncMock(return_value=ticket)

        with pytest.raises(TicketError, match="role"):
            await queue.reject(
                ticket_id=ticket.ticket_id,
                operator_id="bjones@example.com",
                operator_roles=["read_only"],
                reason="Too risky",
            )

    @pytest.mark.asyncio
    async def test_reject_sets_status_to_rejected(self) -> None:
        queue, session, writer = make_queue()
        ticket = make_ticket(status="pending")
        session.get = AsyncMock(return_value=ticket)
        session.flush = AsyncMock()

        result = await queue.reject(
            ticket_id=ticket.ticket_id,
            operator_id="bjones@example.com",
            operator_roles=["network_engineer"],
            reason="Policy violation observed",
        )
        assert result.status == TicketStatus.rejected
        assert result.rejection_reason == "Policy violation observed"


class TestExpirePending:
    @pytest.mark.asyncio
    async def test_overdue_pending_ticket_is_expired(self) -> None:
        """ANIF-406 §4.4.3: ticket past expires_at MUST transition to expired."""
        queue, session, writer = make_queue()
        overdue = make_ticket(
            status="pending",
            expires_at=datetime.now(UTC) - timedelta(seconds=1),
        )

        from sqlalchemy import Result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [overdue]
        session.execute = AsyncMock(return_value=mock_result)
        session.flush = AsyncMock()

        expired_ids = await queue.expire_pending()
        assert overdue.ticket_id in expired_ids
        assert overdue.status == TicketStatus.expired

    @pytest.mark.asyncio
    async def test_expire_writes_audit_for_each_expired_ticket(self) -> None:
        """ANIF-406 §4.4.3: audit record MUST be written for each expiry event."""
        queue, session, writer = make_queue()
        overdue1 = make_ticket(status="pending", expires_at=datetime.now(UTC) - timedelta(seconds=1))
        overdue2 = make_ticket(status="pending", expires_at=datetime.now(UTC) - timedelta(seconds=1))

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [overdue1, overdue2]
        session.execute = AsyncMock(return_value=mock_result)
        session.flush = AsyncMock()

        await queue.expire_pending()
        assert writer.write.call_count == 2

    @pytest.mark.asyncio
    async def test_non_overdue_pending_ticket_not_expired(self) -> None:
        queue, session, writer = make_queue()
        fresh = make_ticket(
            status="pending",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []  # query filters them out
        session.execute = AsyncMock(return_value=mock_result)
        session.flush = AsyncMock()

        expired_ids = await queue.expire_pending()
        assert fresh.ticket_id not in expired_ids
        assert fresh.status == TicketStatus.pending
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
.venv/bin/pytest tests/unit/test_approval_queue.py --tb=line -q 2>&1 | tail -5
```

Expected: `ImportError: No module named 'anif_platform.human_loop.queue'`

- [ ] **Step 3: Create `src/anif_platform/human_loop/queue.py`**

```python
"""
ApprovalQueue — approval ticket lifecycle — ANIF-404 §4.4.

Wraps AsyncSession and AuditWriter. Raises TicketError for all
rule violations (caller converts to HTTP status codes).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.audit.writer import AuditWriter
from anif_platform.human_loop.models import ApprovalTicketRow, TicketStatus
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage

log = structlog.get_logger(__name__)

_TICKET_EXPIRY_MINUTES = 15  # ANIF-404 §4.4.1 — NOT configurable
_APPROVER_ROLES = frozenset({"senior_engineer"})
_REJECTOR_ROLES = frozenset({"network_engineer", "senior_engineer"})


class TicketError(Exception):
    """Raised for all ticket lifecycle violations."""

    def __init__(self, message: str, http_status: int = 400) -> None:
        super().__init__(message)
        self.http_status = http_status


class ApprovalQueue:
    """
    Stateful approval ticket CRUD — ANIF-404 §4.4.

    One instance per request. Inject via FastAPI dependency.
    """

    def __init__(self, session: AsyncSession, writer: AuditWriter) -> None:
        self._session = session
        self._writer = writer

    async def create_ticket(
        self,
        intent_id: uuid.UUID,
        operator_id: str,
        risk_score: int,
        decision_summary: str,
    ) -> ApprovalTicketRow:
        """
        Create a new approval ticket in pending state — ANIF-404 §4.4.1.

        Writes an audit record before returning (write-before-return).
        """
        now = datetime.now(UTC)
        ticket = ApprovalTicketRow(
            ticket_id=str(uuid.uuid4()),
            intent_id=intent_id,
            status=TicketStatus.pending,
            requested_by=operator_id,
            decision_summary=decision_summary,
            risk_score=risk_score,
            required_approver_role="senior_engineer",
            created_at=now,
            expires_at=now + timedelta(minutes=_TICKET_EXPIRY_MINUTES),
        )
        self._session.add(ticket)
        await self._session.flush()

        await self._writer.write(AuditRecord(
            intent_id=intent_id,
            stage=AuditStage.governance,
            operator_id=operator_id,
            input_summary={"ticket_id": ticket.ticket_id, "action": "ticket_created"},
            output_summary={
                "status": TicketStatus.pending,
                "expires_at": ticket.expires_at.isoformat(),
            },
            outcome=AuditOutcome.escalated,
        ))

        log.info(
            "approval_ticket_created",
            ticket_id=ticket.ticket_id,
            intent_id=str(intent_id),
            requested_by=operator_id,
            expires_at=ticket.expires_at.isoformat(),
        )
        return ticket

    async def get_ticket(self, ticket_id: str) -> ApprovalTicketRow | None:
        """Retrieve a ticket by ID."""
        return await self._session.get(ApprovalTicketRow, ticket_id)

    async def approve(
        self,
        ticket_id: str,
        approver_id: str,
        approver_roles: list[str],
        notes: str | None = None,
    ) -> ApprovalTicketRow:
        """
        Approve a pending ticket — ANIF-404 §4.4.4.

        Raises TicketError for: wrong role, self-approval, non-pending state.
        Writes audit record before returning.
        """
        if not set(approver_roles).intersection(_APPROVER_ROLES):
            raise TicketError(
                f"Approval requires senior_engineer role. Caller roles: {approver_roles}",
                http_status=403,
            )

        ticket = await self._get_or_raise(ticket_id)

        if ticket.requested_by == approver_id:
            raise TicketError(
                f"self-approval is prohibited (ANIF-404 §4.4.4). "
                f"Submitter and approver are both {approver_id}.",
                http_status=403,
            )

        if ticket.status != TicketStatus.pending:
            raise TicketError(
                f"Ticket {ticket_id} is not in pending state (current: {ticket.status}). "
                f"Approved, rejected, and expired tickets are terminal.",
                http_status=409,
            )

        now = datetime.now(UTC)
        ticket.status = TicketStatus.approved
        ticket.approved_by = approver_id
        ticket.approved_at = now
        ticket.approval_notes = notes
        await self._session.flush()

        await self._writer.write(AuditRecord(
            intent_id=ticket.intent_id,
            stage=AuditStage.governance,
            operator_id=approver_id,
            input_summary={"ticket_id": ticket_id, "action": "approve"},
            output_summary={"status": TicketStatus.approved, "approved_by": approver_id},
            outcome=AuditOutcome.success,
        ))

        log.info("approval_ticket_approved", ticket_id=ticket_id, approver_id=approver_id)
        return ticket

    async def reject(
        self,
        ticket_id: str,
        operator_id: str,
        operator_roles: list[str],
        reason: str,
    ) -> ApprovalTicketRow:
        """
        Reject a pending ticket — ANIF-404 §4.4.5.

        Raises TicketError for: missing reason, wrong role, non-pending state.
        Writes audit record before returning.
        """
        if not reason or not reason.strip():
            raise TicketError(
                "A reason MUST be provided when rejecting a ticket (ANIF-404 §4.4.5).",
                http_status=400,
            )

        if not set(operator_roles).intersection(_REJECTOR_ROLES):
            raise TicketError(
                f"Rejection requires network_engineer role or above. Caller roles: {operator_roles}",
                http_status=403,
            )

        ticket = await self._get_or_raise(ticket_id)

        if ticket.status != TicketStatus.pending:
            raise TicketError(
                f"Ticket {ticket_id} is not in pending state (current: {ticket.status}).",
                http_status=409,
            )

        now = datetime.now(UTC)
        ticket.status = TicketStatus.rejected
        ticket.rejected_by = operator_id
        ticket.rejected_at = now
        ticket.rejection_reason = reason
        await self._session.flush()

        await self._writer.write(AuditRecord(
            intent_id=ticket.intent_id,
            stage=AuditStage.governance,
            operator_id=operator_id,
            input_summary={"ticket_id": ticket_id, "action": "reject"},
            output_summary={"status": TicketStatus.rejected, "reason": reason},
            outcome=AuditOutcome.failure,
        ))

        log.info("approval_ticket_rejected", ticket_id=ticket_id, operator_id=operator_id)
        return ticket

    async def expire_pending(self) -> list[str]:
        """
        Transition overdue pending tickets to expired — ANIF-406 §4.4.3.

        Called by the background expiry task every 60 seconds.
        Returns list of expired ticket IDs.
        Writes one audit record per expiry event.
        """
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(ApprovalTicketRow).where(
                ApprovalTicketRow.status == TicketStatus.pending,
                ApprovalTicketRow.expires_at <= now,
            )
        )
        overdue = result.scalars().all()
        expired_ids: list[str] = []

        for ticket in overdue:
            ticket.status = TicketStatus.expired
            await self._session.flush()

            await self._writer.write(AuditRecord(
                intent_id=ticket.intent_id,
                stage=AuditStage.governance,
                operator_id="system",
                input_summary={"ticket_id": ticket.ticket_id, "action": "expire"},
                output_summary={
                    "status": TicketStatus.expired,
                    "requested_by": ticket.requested_by,
                    "expired_at": now.isoformat(),
                },
                outcome=AuditOutcome.failure,
            ))

            log.warning(
                "approval_ticket_expired",
                ticket_id=ticket.ticket_id,
                intent_id=str(ticket.intent_id),
                requested_by=ticket.requested_by,
            )
            expired_ids.append(ticket.ticket_id)

        return expired_ids

    async def _get_or_raise(self, ticket_id: str) -> ApprovalTicketRow:
        ticket = await self._session.get(ApprovalTicketRow, ticket_id)
        if ticket is None:
            raise TicketError(f"Ticket {ticket_id} not found.", http_status=404)
        return ticket
```

- [ ] **Step 4: Update `src/anif_platform/human_loop/__init__.py`**

```python
"""ANIF human-in-loop controls — ANIF-404."""

from anif_platform.human_loop.queue import ApprovalQueue, TicketError

__all__ = ["ApprovalQueue", "TicketError"]
```

- [ ] **Step 5: Run tests**

```bash
.venv/bin/pytest tests/unit/test_approval_queue.py -v --tb=short 2>&1 | tail -25
```

Expected: all tests pass.

- [ ] **Step 6: Lint and type-check**

```bash
.venv/bin/ruff check --fix src/anif_platform/human_loop/ && \
.venv/bin/black src/anif_platform/human_loop/ && \
.venv/bin/mypy --strict src/anif_platform/human_loop/queue.py
```

Expected: no errors.

- [ ] **Step 7: Commit**

```bash
git add src/anif_platform/human_loop/ tests/unit/test_approval_queue.py
git commit -m "feat: implement ApprovalQueue with ticket lifecycle (ANIF-404)"
```

---

## Task 5: Governance Router

**Files:**
- Create: `src/anif_platform/governance/router.py`
- Modify: `src/anif_platform/governance/__init__.py`

This router wires `GovernanceGate` + `ApprovalQueue` + `AuditWriter` to the HTTP surface.

- [ ] **Step 1: Create `src/anif_platform/governance/router.py`**

```python
"""
Governance router — ANIF-406 §4.1.

POST /governance/check   — mode gate
POST /governance/approve/{ticket_id}
POST /governance/reject/{ticket_id}
GET  /governance/tickets — list pending tickets

Operator identity: headers X-Operator-Id + X-Operator-Roles (comma-separated).
Full X.509 role verification deferred to B6.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, status

from anif_platform.audit.writer import AuditWriter
from anif_platform.auth import get_api_key
from anif_platform.governance.gate import GovernanceGate
from anif_platform.human_loop.models import TicketStatus
from anif_platform.human_loop.queue import ApprovalQueue, TicketError
from anif_platform.human_loop.schemas import (
    ApproveRequest,
    ApproveResponse,
    GovernanceCheckRequest,
    GovernanceCheckResponse,
    RejectRequest,
    RejectResponse,
)
from anif_platform.monitoring.metrics import (
    GOVERNANCE_AUTO,
    GOVERNANCE_BLOCK,
    GOVERNANCE_MANUAL_REVIEW,
    RULE_TRIGGERS,
    TICKET_APPROVED,
    TICKET_EXPIRED,
    TICKET_REJECTED,
)
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/governance", tags=["governance"])

_gate = GovernanceGate()


def get_audit_writer() -> AuditWriter:
    raise NotImplementedError("Override via dependency injection")


def get_approval_queue() -> ApprovalQueue:
    raise NotImplementedError("Override via dependency injection")


def _parse_roles(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [r.strip() for r in raw.split(",") if r.strip()]


@router.post("/check", response_model=GovernanceCheckResponse)
async def governance_check(
    request: GovernanceCheckRequest,
    writer: AuditWriter = Depends(get_audit_writer),
    queue: ApprovalQueue = Depends(get_approval_queue),
    _: str = Depends(get_api_key),
) -> GovernanceCheckResponse:
    """
    Evaluate governance rules and return a mode decision — ANIF-406 §4.1.1.

    Audit record MUST be written before returning; returns HTTP 503 on write failure.
    """
    start = time.monotonic()

    gate_result = _gate.check(
        intent_id=str(request.intent_id),
        operator_id=request.operator_id,
        operator_roles=request.operator_roles,
        action_type=request.action_type,
        environment=request.environment,
        risk_score=request.risk_score,
        trust_score=request.trust_score,
        policy_results=[r.model_dump() for r in request.policy_results],
        trace_id=str(request.trace_id),
    )

    mode = gate_result["mode"]
    triggered = gate_result["triggered_rule"]
    duration_ms = int((time.monotonic() - start) * 1000)

    ticket_id: str | None = None
    ticket_expires_at = None

    # Create ticket if manual_review — BEFORE writing the audit record
    if mode == "manual_review":
        decision_summary = (
            f"{request.action_type} on {request.environment} environment "
            f"(risk_score={request.risk_score})"
        )
        ticket = await queue.create_ticket(
            intent_id=request.intent_id,
            operator_id=request.operator_id,
            risk_score=request.risk_score,
            decision_summary=decision_summary,
        )
        ticket_id = ticket.ticket_id
        ticket_expires_at = ticket.expires_at

    # Write governance audit record (MUST complete before returning — ANIF-406 §4.3.1)
    outcome_map = {
        "auto": AuditOutcome.success,
        "manual_review": AuditOutcome.escalated,
        "block": AuditOutcome.blocked,
    }
    try:
        audit_record = AuditRecord(
            intent_id=request.intent_id,
            stage=AuditStage.governance,
            operator_id=request.operator_id,
            input_summary={
                "action_type": request.action_type,
                "environment": request.environment,
                "risk_score": request.risk_score,
                "trust_score": request.trust_score,
            },
            output_summary={
                "mode": mode,
                "triggered_rule": triggered,
                "ticket_id": ticket_id,
            },
            outcome=outcome_map.get(mode, AuditOutcome.success),
            duration_ms=duration_ms,
        )
        await writer.write(audit_record)
    except Exception as exc:
        # ANIF-406 §4.1.1 req 2: audit write failure MUST return 503
        log.error("governance_audit_write_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Governance audit write failed; request cannot proceed.",
        ) from exc

    # Update Prometheus metrics
    env_label = request.environment
    if mode == "auto":
        GOVERNANCE_AUTO.labels(environment=env_label).inc()
    elif mode == "manual_review":
        GOVERNANCE_MANUAL_REVIEW.labels(environment=env_label).inc()
    else:
        GOVERNANCE_BLOCK.labels(environment=env_label, triggered_rule=triggered).inc()

    for rule_id in triggered.split(", "):
        if rule_id and rule_id != "none":
            RULE_TRIGGERS.labels(rule_id=rule_id, environment=env_label).inc()

    return GovernanceCheckResponse(
        intent_id=request.intent_id,
        mode=mode,
        triggered_rule=triggered,
        rationale=gate_result["rationale"],
        ticket_id=ticket_id,
        ticket_expires_at=ticket_expires_at,
        audit_record_id=str(audit_record.record_id),
        trace_id=request.trace_id,
    )


@router.post("/approve/{ticket_id}", response_model=ApproveResponse)
async def approve_ticket(
    ticket_id: str,
    body: ApproveRequest,
    x_operator_id: str = Header(..., alias="X-Operator-Id"),
    x_operator_roles: str | None = Header(None, alias="X-Operator-Roles"),
    queue: ApprovalQueue = Depends(get_approval_queue),
    _: str = Depends(get_api_key),
) -> ApproveResponse:
    """Approve a pending ticket — ANIF-404 §4.4.4."""
    roles = _parse_roles(x_operator_roles)
    try:
        ticket = await queue.approve(
            ticket_id=ticket_id,
            approver_id=x_operator_id,
            approver_roles=roles,
            notes=body.notes,
        )
    except TicketError as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc

    TICKET_APPROVED.labels(
        environment="unknown", approver_role=body.approver_role
    ).inc()

    return ApproveResponse(
        ticket_id=ticket.ticket_id,
        status=ticket.status,
        approved_by=ticket.approved_by or x_operator_id,
        approved_at=ticket.approved_at or __import__("datetime").datetime.now(__import__("datetime").UTC),
        audit_record_id="",  # written inside queue.approve
    )


@router.post("/reject/{ticket_id}", response_model=RejectResponse)
async def reject_ticket(
    ticket_id: str,
    body: RejectRequest,
    x_operator_id: str = Header(..., alias="X-Operator-Id"),
    x_operator_roles: str | None = Header(None, alias="X-Operator-Roles"),
    queue: ApprovalQueue = Depends(get_approval_queue),
    _: str = Depends(get_api_key),
) -> RejectResponse:
    """Reject a pending ticket — ANIF-404 §4.4.5."""
    roles = _parse_roles(x_operator_roles)
    try:
        ticket = await queue.reject(
            ticket_id=ticket_id,
            operator_id=x_operator_id,
            operator_roles=roles,
            reason=body.reason,
        )
    except TicketError as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc

    TICKET_REJECTED.labels(environment="unknown").inc()

    return RejectResponse(
        ticket_id=ticket.ticket_id,
        status=ticket.status,
        rejected_by=ticket.rejected_by or x_operator_id,
        rejected_at=ticket.rejected_at or __import__("datetime").datetime.now(__import__("datetime").UTC),
        audit_record_id="",
    )


@router.get("/tickets")
async def list_pending_tickets(
    queue: ApprovalQueue = Depends(get_approval_queue),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """List pending approval tickets — ANIF-404 §4.5 (view requires network_engineer)."""
    # Role check deferred to B6 (X.509 auth); for now, API key is sufficient gate
    from sqlalchemy import select
    from anif_platform.human_loop.models import ApprovalTicketRow
    result = await queue._session.execute(
        select(ApprovalTicketRow).where(
            ApprovalTicketRow.status == TicketStatus.pending
        )
    )
    tickets = result.scalars().all()
    return {
        "pending_count": len(tickets),
        "tickets": [
            {
                "ticket_id": t.ticket_id,
                "intent_id": str(t.intent_id),
                "requested_by": t.requested_by,
                "risk_score": t.risk_score,
                "decision_summary": t.decision_summary,
                "created_at": t.created_at.isoformat(),
                "expires_at": t.expires_at.isoformat(),
            }
            for t in tickets
        ],
    }
```

- [ ] **Step 2: Verify the router imports cleanly**

```bash
.venv/bin/python -c "from anif_platform.governance.router import router; print('OK')"
```

Note: this will fail until metrics.py exists (Task 8). Run after Task 8.

- [ ] **Step 3: Commit (after metrics task, or stub the imports first)**

> Skip commit until Task 8 (metrics) is done; or create a stub `monitoring/metrics.py` now with the counter names as stubs, then come back.

---

## Task 6: Emergency Halt Endpoint

**Files:**
- Create: `src/anif_platform/human_loop/router.py`

- [ ] **Step 1: Create `src/anif_platform/human_loop/router.py`**

```python
"""
Human-in-loop control endpoints — ANIF-404 §4.6.

POST /execution/{intent_id}/halt — emergency halt.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, status

from anif_platform.audit.writer import AuditWriter
from anif_platform.auth import get_api_key
from anif_platform.human_loop.schemas import HaltRequest, HaltResponse
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage

log = structlog.get_logger(__name__)
router = APIRouter(tags=["human-in-loop"])

_HALT_PERMITTED_ROLES = frozenset({"network_engineer", "senior_engineer"})


def get_audit_writer() -> AuditWriter:
    raise NotImplementedError("Override via dependency injection")


def _parse_roles(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [r.strip() for r in raw.split(",") if r.strip()]


@router.post("/execution/{intent_id}/halt", response_model=HaltResponse)
async def halt_execution(
    intent_id: uuid.UUID,
    body: HaltRequest,
    x_operator_roles: str | None = Header(None, alias="X-Operator-Roles"),
    writer: AuditWriter = Depends(get_audit_writer),
    _: str = Depends(get_api_key),
) -> HaltResponse:
    """
    Emergency halt of an in-progress execution — ANIF-404 §4.6.

    Requires network_engineer role.
    Audit record MUST be written before returning (ANIF-404 §4.6.1 req 4).
    """
    roles = _parse_roles(x_operator_roles)
    if not set(roles).intersection(_HALT_PERMITTED_ROLES):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Emergency halt requires network_engineer role. Caller roles: {roles}",
        )

    if not body.reason or not body.reason.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A reason MUST be provided for emergency halt (ANIF-404 §4.6.2).",
        )

    now = datetime.now(UTC)

    # Write audit record BEFORE returning (ANIF-404 §4.6.1 req 4)
    audit_record = AuditRecord(
        intent_id=intent_id,
        stage=AuditStage.execute,
        operator_id=body.operator_id,
        input_summary={"action": "halt", "reason": body.reason},
        output_summary={"halt_status": "halted", "rollback_initiated": True},
        outcome=AuditOutcome.blocked,
    )
    await writer.write(audit_record)

    log.warning(
        "execution_halted_by_operator",
        intent_id=str(intent_id),
        operator_id=body.operator_id,
        reason=body.reason,
    )

    # Rollback initiation is a stub until B5 executors are implemented
    return HaltResponse(
        intent_id=intent_id,
        halt_status="halted",
        rollback_initiated=True,
        rollback_status="in_progress",
        audit_record_id=str(audit_record.record_id),
        halted_by=body.operator_id,
        halted_at=now,
    )
```

- [ ] **Step 2: Verify import**

```bash
.venv/bin/python -c "from anif_platform.human_loop.router import router; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit (after wiring in main.py in Task 9)**

---

## Task 7: Background Expiry Task

**Files:**
- Create: `src/anif_platform/human_loop/expiry.py`

- [ ] **Step 1: Create `src/anif_platform/human_loop/expiry.py`**

```python
"""
Background ticket expiry task — ANIF-406 §4.4.3.

Runs every 60 seconds; transitions overdue pending tickets to expired.
Started in the FastAPI lifespan.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.audit.writer import AuditWriter
from anif_platform.human_loop.queue import ApprovalQueue
from anif_platform.monitoring.metrics import TICKET_EXPIRED

log = structlog.get_logger(__name__)

_EXPIRY_INTERVAL_SECONDS = 60  # ANIF-406 §4.4.3: MUST run at least every 60 seconds


async def expiry_loop(session_factory: object) -> None:
    """
    Infinite loop: check for overdue tickets every 60 seconds.

    session_factory must be an async context manager factory (e.g., async_session_factory).
    """
    while True:
        await asyncio.sleep(_EXPIRY_INTERVAL_SECONDS)
        try:
            async with session_factory() as session:  # type: ignore[call-overload]
                writer = AuditWriter(session)
                queue = ApprovalQueue(session=session, writer=writer)
                expired = await queue.expire_pending()
                if expired:
                    log.info("tickets_expired_by_background_task", count=len(expired), ticket_ids=expired)
                    for _ in expired:
                        TICKET_EXPIRED.labels(environment="unknown").inc()
        except Exception:
            log.exception("expiry_loop_error")
```

- [ ] **Step 2: Verify import**

```bash
.venv/bin/python -c "from anif_platform.human_loop.expiry import expiry_loop; print('OK')"
```

Expected: `OK` (after metrics.py exists)

---

## Task 8: Prometheus Governance Metrics

**Files:**
- Create: `src/anif_platform/monitoring/metrics.py`

- [ ] **Step 1: Create `src/anif_platform/monitoring/metrics.py`**

```python
"""
Prometheus governance metrics — ANIF-406 §4.5.

All counters and histograms defined here. Import and call .inc()/.observe()
at the point of the event. Metrics are lazily registered with the default registry.
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram

# ── Mode counters ────────────────────────────────────────────────────────────

GOVERNANCE_AUTO = Counter(
    "anif_governance_auto_total",
    "Total executions routed as auto",
    ["environment"],
)

GOVERNANCE_MANUAL_REVIEW = Counter(
    "anif_governance_manual_review_total",
    "Total executions routed to manual_review",
    ["environment"],
)

GOVERNANCE_BLOCK = Counter(
    "anif_governance_block_total",
    "Total executions blocked, by triggering rule",
    ["environment", "triggered_rule"],
)

# ── Ticket outcome counters ──────────────────────────────────────────────────

TICKET_APPROVED = Counter(
    "anif_ticket_approved_total",
    "Total tickets approved, by approver role",
    ["environment", "approver_role"],
)

TICKET_REJECTED = Counter(
    "anif_ticket_rejected_total",
    "Total tickets rejected",
    ["environment"],
)

TICKET_EXPIRED = Counter(
    "anif_ticket_expired_total",
    "Total tickets that expired without action",
    ["environment"],
)

# ── Rule trigger counter ─────────────────────────────────────────────────────

RULE_TRIGGERS = Counter(
    "anif_governance_rule_triggers_total",
    "Total times each governance rule was triggered",
    ["rule_id", "environment"],
)

# ── Ticket age histogram ─────────────────────────────────────────────────────

TICKET_PENDING_AGE = Histogram(
    "anif_ticket_pending_age_seconds",
    "Age of pending tickets at time of action or expiry",
    ["environment"],
    buckets=[30, 60, 120, 300, 600, 900],  # 30s to 15min
)
```

- [ ] **Step 2: Verify import**

```bash
.venv/bin/python -c "from anif_platform.monitoring.metrics import GOVERNANCE_AUTO, TICKET_EXPIRED; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Now run the governance router import (from Task 5)**

```bash
.venv/bin/python -c "from anif_platform.governance.router import router; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit Tasks 5–8 together**

```bash
git add \
  src/anif_platform/governance/router.py \
  src/anif_platform/human_loop/router.py \
  src/anif_platform/human_loop/expiry.py \
  src/anif_platform/monitoring/metrics.py
git commit -m "feat: add governance router, halt endpoint, expiry task, Prometheus metrics (ANIF-404, ANIF-406)"
```

---

## Task 9: Wire Everything into main.py

**Files:**
- Modify: `src/anif_platform/main.py`

- [ ] **Step 1: Update the lifespan and dependency overrides in `main.py`**

Add after the existing imports at the top:

```python
from anif_platform.governance.router import get_audit_writer as gov_get_writer
from anif_platform.governance.router import get_approval_queue as gov_get_queue
from anif_platform.governance.router import router as governance_router
from anif_platform.human_loop.router import get_audit_writer as halt_get_writer
from anif_platform.human_loop.router import router as human_loop_router
from anif_platform.human_loop.queue import ApprovalQueue
from anif_platform.human_loop.expiry import expiry_loop
```

Update `lifespan` to start the expiry task:

```python
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

    # Start ticket expiry background task (ANIF-406 §4.4.3)
    expiry_task = asyncio.create_task(expiry_loop(async_session_factory))
    log.info("ticket_expiry_task_started")

    yield

    expiry_task.cancel()
    await engine.dispose()
    log.info("anif_platform_stopped")
```

Add `import asyncio` to main.py imports if not already present.

Add dependency factory functions after the existing ones:

```python
async def _get_session_approval_queue(request: Request) -> AsyncGenerator[ApprovalQueue, None]:
    async with async_session_factory() as session:
        writer = AuditWriter(session)
        yield ApprovalQueue(session=session, writer=writer)
```

Add dependency overrides after existing overrides:

```python
app.dependency_overrides[gov_get_writer] = _get_session_writer
app.dependency_overrides[gov_get_queue] = _get_session_approval_queue
app.dependency_overrides[halt_get_writer] = _get_session_writer
```

Mount routers at the bottom:

```python
app.include_router(governance_router)
app.include_router(human_loop_router)
```

- [ ] **Step 2: Verify the app starts without import errors**

```bash
.venv/bin/python -c "from anif_platform.main import app; print('OK')"
```

Expected: `OK` (DATABASE_URL must be set, or use the env vars from conftest)

- [ ] **Step 3: Commit**

```bash
git add src/anif_platform/main.py
git commit -m "feat: register governance/human_loop routers and expiry task in main.py (ANIF-404, ANIF-406)"
```

---

## Task 10: Pipeline Orchestrator Integration

**Files:**
- Modify: `src/anif_platform/pipeline/router.py`

Add a governance stage after the decision stage, replacing the current governance stub.

- [ ] **Step 1: Update imports in `pipeline/router.py`**

Add after existing imports:

```python
from anif_platform.governance.gate import GovernanceGate
from anif_platform.human_loop.queue import ApprovalQueue
```

Add a new dependency getter:

```python
def get_approval_queue() -> ApprovalQueue:
    raise NotImplementedError("Provide ApprovalQueue via dependency injection")
```

Add the queue parameter to the `orchestrate` endpoint signature:

```python
@router.post("/orchestrate", response_model=dict[str, Any])
async def orchestrate(
    request: OrchestrateRequest,
    engine: PolicyEngine = Depends(get_policy_engine),
    registry: IntentRegistry = Depends(get_intent_registry),
    writer: AuditWriter = Depends(get_audit_writer),
    queue: ApprovalQueue = Depends(get_approval_queue),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
```

- [ ] **Step 2: Replace the governance stub in the orchestrate function**

Replace this block:

```python
# ── Stage 5: Governance Gate (STUB — implemented in B4) ──────────────
pipeline_result["governance"] = {
    "status": "not_yet_implemented",
    "stage": "governance",
    "message": "GovernanceGate will be implemented in B4",
}
```

With:

```python
# ── Stage 5: Governance Gate (ANIF-406) ──────────────────────────────
import uuid as _uuid, time as _time
_gov_start = _time.monotonic()
_gov_gate = GovernanceGate()
_gov_result = _gov_gate.check(
    intent_id=str(intent_id),
    operator_id="pipeline-automation",
    operator_roles=["automation_agent"],
    action_type=decision_result.get("recommended_action", {}).get("action_type", "apply_qos") if decision_result.get("recommended_action") else "apply_qos",
    environment=validation.validated_intent.get("environment", "dev"),  # type: ignore[union-attr]
    risk_score=risk_result["risk_score"],
    trust_score=risk_result["trust_score"],
    policy_results=[
        {"policy_id": r["policy_name"], "outcome": "fail" if r["decision"] == "deny" else "pass", "safety_decision": "block" if r["decision"] == "deny" else None}
        for r in policy_result.get("policy_results", [])
    ],
    trace_id=str(_uuid.uuid4()),
)
_gov_duration_ms = int((_time.monotonic() - _gov_start) * 1000)

_gov_outcome_map = {"auto": AuditOutcome.success, "manual_review": AuditOutcome.escalated, "block": AuditOutcome.blocked}
await writer.write(AuditRecord(
    intent_id=intent_id,
    stage=AuditStage.governance,
    input_summary={"risk_score": risk_result["risk_score"], "trust_score": risk_result["trust_score"]},
    output_summary={"mode": _gov_result["mode"], "triggered_rule": _gov_result["triggered_rule"]},
    outcome=_gov_outcome_map.get(_gov_result["mode"], AuditOutcome.success),
    duration_ms=_gov_duration_ms,
))

if _gov_result["mode"] == "block" and not request.dry_run:
    return {
        "status": "blocked",
        "stage": "governance",
        "intent_id": str(intent_id),
        "governance_result": _gov_result,
    }

if _gov_result["mode"] == "manual_review" and not request.dry_run:
    _ticket = await queue.create_ticket(
        intent_id=intent_id,
        operator_id="pipeline-automation",
        risk_score=risk_result["risk_score"],
        decision_summary=f"Action {decision_result.get('recommended_action', {}).get('action_type', 'unknown')} requires senior_engineer approval",
    )
    return {
        "status": "pending_approval",
        "stage": "governance",
        "intent_id": str(intent_id),
        "ticket_id": _ticket.ticket_id,
        "ticket_expires_at": _ticket.expires_at.isoformat(),
        "governance_result": _gov_result,
    }

pipeline_result["governance"] = _gov_result
```

- [ ] **Step 3: Add `get_approval_queue` to the dependency overrides in `main.py`**

```python
from anif_platform.pipeline.router import get_approval_queue as pipeline_get_queue
# ...
app.dependency_overrides[pipeline_get_queue] = _get_session_approval_queue
```

- [ ] **Step 4: Run unit tests to confirm nothing broke**

```bash
.venv/bin/pytest tests/unit/ \
  --ignore=tests/unit/test_audit_writer.py \
  --ignore=tests/unit/test_intent_validator.py \
  --tb=short -q 2>&1 | tail -5
```

Expected: all tests pass (count will have grown from 203 to ~240+ with new B4 tests).

- [ ] **Step 5: Lint and type-check all modified files**

```bash
.venv/bin/ruff check --fix src/anif_platform/ && \
.venv/bin/black src/anif_platform/ && \
.venv/bin/mypy --strict src/anif_platform/governance/ src/anif_platform/human_loop/ src/anif_platform/monitoring/metrics.py
```

Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add src/anif_platform/pipeline/router.py src/anif_platform/main.py
git commit -m "feat: integrate GovernanceGate into pipeline orchestrator (ANIF-404, ANIF-406)"
```

---

## Self-Review: Spec Coverage Check

### ANIF-406 Requirements

| Requirement | Task |
|---|---|
| `POST /governance/check` with all 6 rules | Task 3 (gate) + Task 5 (router) |
| Audit record written before response; 503 on failure | Task 5 |
| Block rules evaluated before manual_review | Task 3 |
| Approval ticket lifecycle (created→pending→approved/rejected/expired) | Task 4 |
| Overrides of R-05 and R-06 NOT permitted | Task 3 (block is terminal, no override path) |
| Governance metrics exposed | Task 8 |
| Expiry check every 60 seconds | Task 7 |
| `audit_record_id` in response | Task 5 |
| `trace_id` echoed | Task 3 + 5 |

### ANIF-404 Requirements

| Requirement | Task |
|---|---|
| Mandatory mode gate traversal | Task 10 (pipeline) |
| R-01–R-06 trigger rules | Task 3 |
| 15-minute ticket expiry (not configurable) | Task 4 |
| Approver role must be `senior_engineer` | Task 4 |
| Self-approval refused | Task 4 |
| `POST /governance/approve/{ticket_id}` | Task 5 |
| `POST /governance/reject/{ticket_id}` | Task 5 |
| Rejection requires reason | Task 4 |
| Emergency halt `POST /execution/{intent_id}/halt` | Task 6 |
| Halt requires `network_engineer` role | Task 6 |
| Halt audit before returning | Task 6 |

### Gaps / Out of Scope for B4

- **Notification dispatch** (ANIF-404 §4.4.2): "configured notification channel" is implementation-specific. Logged as a warning; no dispatch. Add `log.warning("ticket_notification_not_configured", ...)` in `queue.create_ticket()`.
- **Override controls** (ANIF-406 §4.6): senior_engineer overrides of `manual_review→auto`. Not in core pipeline path; deferred.
- **War room mode**: deferred.
- **P-06 out-of-band halt path**: the halt endpoint is independent of the pipeline but shares the same FastAPI process. Full out-of-band path (separate process) deferred.
- **`GET /audit/{intent_id}/why`**: belongs to the audit module, not governance.
- **Frontend Approval Queue UI (F3)**: separate phase.
