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
