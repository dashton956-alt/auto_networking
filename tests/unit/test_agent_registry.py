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
