"""Ethics module SQLAlchemy models — ANIF-721 strike records."""

from __future__ import annotations

import uuid as _uuid
from datetime import datetime

from sqlalchemy import DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from anif_platform.database import Base


class StrikeRecordRow(Base):
    """Append-only agent strike record — ANIF-721 §7.

    The append-only property MUST be enforced at the database level.
    PostgreSQL: row-level security policy prevents UPDATE and DELETE for
    all application roles. Only INSERT and SELECT are permitted.
    See migration 006 for the RLS policy definition.
    """

    __tablename__ = "strike_records"

    strike_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    agent_id: Mapped[_uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    intent_id: Mapped[_uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
