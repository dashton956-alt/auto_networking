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
from anif_platform.audit.writer import AuditWriter
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage

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
    """Raised when PROVISIONAL→ACTIVE is attempted before 72h — ANIF-803."""


class AgentNotFoundError(Exception):
    """Raised when agent_id is not found in the registry."""


class AgentRegistry:
    """Manages agent lifecycle and permitted persistent state — ANIF-803, ANIF-805."""

    def __init__(self, session: AsyncSession, writer: AuditWriter) -> None:
        self._session = session
        self._writer = writer

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
        await self._writer.write(
            AuditRecord(
                stage=AuditStage.agent_lifecycle,
                intent_id=uuid.uuid4(),
                input_summary={"agent_id": agent_id, "tier": tier, "role": role},
                output_summary={"lifecycle_state": AgentLifecycleState.PROPOSED.value},
                outcome=AuditOutcome.success,
                duration_ms=0,
            )
        )
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
            if agent.provisional_until is None or datetime.now(UTC) < agent.provisional_until:
                until_str = (
                    agent.provisional_until.isoformat()
                    if agent.provisional_until is not None
                    else "unknown (provisional_until not set)"
                )
                raise ProvisionalPeriodError(
                    f"Agent must remain PROVISIONAL until {until_str}"
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
        await self._writer.write(
            AuditRecord(
                stage=AuditStage.agent_lifecycle,
                intent_id=uuid.uuid4(),
                input_summary={"agent_id": agent_id, "trigger": trigger},
                output_summary={
                    "previous_state": current_state.value,
                    "new_state": new_state.value,
                },
                outcome=AuditOutcome.success,
                duration_ms=0,
            )
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
        await self._writer.write(
            AuditRecord(
                stage=AuditStage.agent_lifecycle,
                intent_id=uuid.uuid4(),
                input_summary={"agent_id": agent_id, "intent_id": intent_id},
                output_summary={"action": "working_context_cleared"},
                outcome=AuditOutcome.success,
                duration_ms=0,
            )
        )

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
        log.info("agent_cert_recorded", agent_id=agent_id, expires_at=certificate_expires_at.isoformat())
