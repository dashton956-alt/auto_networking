"""SQLAlchemy model for council records — ANIF-907.

Council records are append-only and immutable after session close.
No UPDATE or DELETE permitted on existing rows (CR-907-02/03).
"""

from __future__ import annotations

import uuid as _uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from anif_platform.database import Base


class CouncilRecordRow(Base):
    """Immutable council session record — ANIF-907.

    Rows are written once and never modified after session_close_timestamp is set.
    agent components MUST NOT read this table (CR-907-04).
    """

    __tablename__ = "council_records"

    council_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(_uuid.uuid4())
    )
    council_type: Mapped[str] = mapped_column(String(32))  # build_time | runtime | review
    triggered_by: Mapped[str] = mapped_column(Text)
    trigger_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    session_open_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    session_close_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Mode selector fields — ANIF-902 §5
    mode_selector_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Deliberation
    deliberation_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    votes_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    vetoes_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Decision
    decision: Mapped[str] = mapped_column(
        String(32), default="pending"
    )  # pending | approved | blocked | conditional | deferred | escalated | timed_out | completed
    decision_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    anif_references_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Review Council outputs
    accountability_determination_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    policy_change_recommendations_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    learning_packages_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Runtime Council
    intent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    intent_outcome: Mapped[str | None] = mapped_column(String(64), nullable=True)
    time_limit_seconds: Mapped[int | None] = mapped_column(nullable=True)
    # Incident linkage (review council)
    incident_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    incident_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    severity_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # Metadata
    record_version: Mapped[str] = mapped_column(String(8), server_default=text("'1.0'"))
    record_written_by: Mapped[str] = mapped_column(String(128), default="platform")
    record_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    closed: Mapped[bool] = mapped_column(Boolean, default=False)
