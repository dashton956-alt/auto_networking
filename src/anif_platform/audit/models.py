"""SQLAlchemy ORM model for audit records — ANIF-107."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from anif_platform.database import Base


class AuditRecordRow(Base):
    """
    Persistent audit record row — ANIF-107 §4.4.

    This table is APPEND-ONLY. No UPDATE or DELETE statements are ever issued
    against it. The audit store MUST be append-only with no mechanism to modify
    or delete records (ANIF-107 §4.4.1). Enforcement is at both the application
    layer (AuditWriter never issues UPDATE/DELETE) and optionally at the
    PostgreSQL layer via row-level security policies.
    """

    __tablename__ = "audit_records"

    # Primary key
    record_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, nullable=False
    )

    # Indexed lookup columns
    intent_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    stage: Mapped[str] = mapped_column(String(32), nullable=False)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    operator_id: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # Hash chain fields
    record_hash: Mapped[str | None] = mapped_column(String(71), nullable=True)  # "sha256:<64hex>"
    prev_hash: Mapped[str | None] = mapped_column(String(71), nullable=True)
    chain_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)

    # Duration for SLA monitoring
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    # Full record stored as JSONB for flexible querying and completeness
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        # Performance indexes — ANIF-107 §7.2
        Index("ix_audit_records_intent_id_timestamp", "intent_id", "timestamp"),
        Index("ix_audit_records_stage", "stage"),
        Index("ix_audit_records_outcome", "outcome"),
        Index("ix_audit_records_operator_id", "operator_id"),
        # Hash chain lookup
        Index("ix_audit_records_chain_id", "chain_id"),
        # record_id uniqueness enforced by primary key; belt-and-suspenders
        UniqueConstraint("record_id", name="uq_audit_records_record_id"),
    )
