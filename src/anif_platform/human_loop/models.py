"""ApprovalTicket SQLAlchemy model — ANIF-404 §4.4."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from anif_platform.database import Base


class TicketStatus(StrEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    expired = "expired"


class ApprovalTicketRow(Base):
    """
    Persisted approval ticket — ANIF-404 §4.4.

    Terminal states: approved, rejected, expired.
    Transitions FROM terminal states are FORBIDDEN (ANIF-406 §4.4.2).
    """

    __tablename__ = "approval_tickets"

    ticket_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    intent_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default=TicketStatus.pending)
    requested_by: Mapped[str] = mapped_column(String, nullable=False)
    decision_summary: Mapped[str] = mapped_column(String, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    required_approver_role: Mapped[str] = mapped_column(
        String, nullable=False, default="senior_engineer"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_by: Mapped[str | None] = mapped_column(String, nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    approval_notes: Mapped[str | None] = mapped_column(String, nullable=True)
