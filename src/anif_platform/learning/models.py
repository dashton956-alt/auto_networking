"""SQLAlchemy models for Knowledge Packages — ANIF-812."""

from __future__ import annotations

import uuid as _uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from anif_platform.database import Base


class KnowledgePackageRow(Base):
    """A versioned, human-approved collection of knowledge items — ANIF-812 §6."""

    __tablename__ = "knowledge_packages"

    package_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(_uuid.uuid4())
    )
    category: Mapped[str] = mapped_column(String(32))  # network_pattern | operational | resolution
    target_roles_json: Mapped[str] = mapped_column(Text)
    submitted_by: Mapped[str] = mapped_column(String(128))
    approval_status: Mapped[str] = mapped_column(String(16), default="pending")
    approver_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    approval_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reject_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    knowledge_items_json: Mapped[str] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class SourceQualityRow(Base):
    """Tracks per-source quality scores — CR-812-05."""

    __tablename__ = "knowledge_source_quality"

    source_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    quality_score: Mapped[float] = mapped_column(Float)
    flagged: Mapped[bool] = mapped_column(default=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
