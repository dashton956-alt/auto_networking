"""Unit tests for AgentRegistry and DB models — ANIF-803, ANIF-805."""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from anif_platform.agents.models import (
    AgentLifecycleEventRow,
    AgentRegistryRow,
    AgentRevocationRow,
    DecommissionedIdentityRow,
)
from anif_platform.agents.registry import (
    AgentNotFoundError,
    AgentRegistry,
    InvalidTransitionError,
    ProvisionalPeriodError,
)
from anif_platform.agents.schemas import (
    AgentLifecycleState,
    RegisterAgentRequest,
    RegisterAgentResponse,
    TransitionRequest,
    TransitionResponse,
)
from anif_platform.schemas import AgentTier


def make_registry() -> tuple[AgentRegistry, AsyncMock]:
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    writer = AsyncMock()
    registry = AgentRegistry(session=session, writer=writer)
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


def test_register_agent_request_rejects_out_of_range_tier() -> None:
    with pytest.raises(ValidationError):
        RegisterAgentRequest(
            agent_id="agent-001",
            agent_type="NetworkObserver",
            role="Network Observer",
            tier=4,
            manifest={},
        )


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
    expected_min = datetime.now(UTC) + timedelta(hours=71)
    expected_max = datetime.now(UTC) + timedelta(hours=73)
    assert expected_min < mock_agent.provisional_until < expected_max


@pytest.mark.asyncio
async def test_transition_provisional_to_active_blocked_before_72h() -> None:
    registry, session = make_registry()

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


@pytest.mark.asyncio
async def test_record_cert_stores_pem_and_expiry() -> None:
    registry, session = make_registry()
    mock_agent = make_mock_agent_row("ACTIVE")
    mock_agent.certificate_pem = None
    mock_agent.certificate_expires_at = None
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = mock_agent
    session.execute = AsyncMock(return_value=result_mock)

    expires = datetime.now(UTC) + timedelta(days=90)
    await registry.record_cert(
        agent_id="agent-001",
        certificate_pem="-----BEGIN CERTIFICATE-----\nMOCK\n-----END CERTIFICATE-----",
        certificate_expires_at=expires,
    )
    assert mock_agent.certificate_pem is not None
    assert mock_agent.certificate_expires_at == expires


@pytest.mark.asyncio
async def test_transition_proposed_to_active_raises_invalid() -> None:
    """PROPOSED → ACTIVE is not a permitted transition."""
    registry, session = make_registry()
    mock_agent = make_mock_agent_row("PROPOSED")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = mock_agent
    session.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(InvalidTransitionError):
        await registry.transition(
            agent_id="agent-001",
            new_state=AgentLifecycleState.ACTIVE,
            trigger="test",
            approver_identity="ops",
            reason="Skip PROVISIONAL",
        )


@pytest.mark.asyncio
async def test_transition_provisional_to_active_raises_when_provisional_until_is_none() -> None:
    """When provisional_until is None, 72h guard must block — not silently pass."""
    registry, session = make_registry()
    mock_agent = make_mock_agent_row("PROVISIONAL", provisional_until=None)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = mock_agent
    session.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(ProvisionalPeriodError):
        await registry.transition(
            agent_id="agent-001",
            new_state=AgentLifecycleState.ACTIVE,
            trigger="manual",
            approver_identity="ops",
            reason="Promote with null provisional_until",
        )
