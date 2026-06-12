"""create audit_records table

Revision ID: 001
Revises:
Create Date: 2026-04-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_records",
        sa.Column("record_id", UUID(as_uuid=True), nullable=False),
        sa.Column("intent_id", UUID(as_uuid=True), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("stage", sa.String(32), nullable=False),
        sa.Column("outcome", sa.String(32), nullable=False),
        sa.Column("operator_id", sa.String(256), nullable=True),
        sa.Column("record_hash", sa.String(71), nullable=True),
        sa.Column("prev_hash", sa.String(71), nullable=True),
        sa.Column("chain_id", UUID(as_uuid=True), nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=False),
        sa.Column("data", JSONB, nullable=False),
        sa.PrimaryKeyConstraint("record_id"),
        sa.UniqueConstraint("record_id", name="uq_audit_records_record_id"),
    )
    op.create_index("ix_audit_records_intent_id_timestamp", "audit_records", ["intent_id", "timestamp"])
    op.create_index("ix_audit_records_stage", "audit_records", ["stage"])
    op.create_index("ix_audit_records_outcome", "audit_records", ["outcome"])
    op.create_index("ix_audit_records_operator_id", "audit_records", ["operator_id"])
    op.create_index("ix_audit_records_chain_id", "audit_records", ["chain_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_records_chain_id", table_name="audit_records")
    op.drop_index("ix_audit_records_operator_id", table_name="audit_records")
    op.drop_index("ix_audit_records_outcome", table_name="audit_records")
    op.drop_index("ix_audit_records_stage", table_name="audit_records")
    op.drop_index("ix_audit_records_intent_id_timestamp", table_name="audit_records")
    op.drop_table("audit_records")
