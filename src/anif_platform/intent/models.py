"""SQLAlchemy ORM model for intents — ANIF-301."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from anif_platform.database import Base


class IntentRow(Base):
    """Registered, validated intent record."""

    __tablename__ = "intents"

    intent_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
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
