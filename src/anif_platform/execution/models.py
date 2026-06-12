"""ExecutionRecord SQLAlchemy ORM model — ANIF-306 §9."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from anif_platform.database import Base


class ExecutionRecordRow(Base):
    """
    Persisted execution record — ANIF-306 §9.

    Written before rollback is called so rollback() can be invoked
    independently using only intent_id (ANIF-306 §6.2).
    Append-only; never updated after creation (ANIF-306 §13).
    """

    __tablename__ = "execution_records"

    execution_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    intent_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    decision_id: Mapped[str] = mapped_column(String, nullable=False)
    action_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)  # success | failed | partial
    adapter_name: Mapped[str] = mapped_column(String, nullable=False, default="mock")
    adapter_status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    adapter_message: Mapped[str] = mapped_column(Text, nullable=False)
    applied_changes: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON list
    rollback_reference: Mapped[str | None] = mapped_column(String, nullable=True)
    rollback_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rollback_status: Mapped[str | None] = mapped_column(String, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    parameters_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # JSON
