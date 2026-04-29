"""Unit tests for AgentRegistry and DB models — ANIF-803, ANIF-805."""
from __future__ import annotations

from anif_platform.agents.models import (
    AgentLifecycleEventRow,
    AgentRegistryRow,
    AgentRevocationRow,
    DecommissionedIdentityRow,
)
from anif_platform.agents.schemas import (
    AgentLifecycleState,
    AgentTier,
    RegisterAgentRequest,
    RegisterAgentResponse,
    TransitionRequest,
    TransitionResponse,
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
