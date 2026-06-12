"""add_execution_records

Revision ID: 004
Revises: 003
Create Date: 2026-04-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "execution_records",
        sa.Column("execution_id", sa.String(), nullable=False),
        sa.Column("intent_id", sa.Uuid(), nullable=False),
        sa.Column("decision_id", sa.String(), nullable=False),
        sa.Column("action_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("adapter_name", sa.String(), nullable=False),
        sa.Column("adapter_status_code", sa.Integer(), nullable=False),
        sa.Column("adapter_message", sa.Text(), nullable=False),
        sa.Column("applied_changes", sa.Text(), nullable=False),
        sa.Column("rollback_reference", sa.String(), nullable=True),
        sa.Column("rollback_available", sa.Boolean(), nullable=False),
        sa.Column("rollback_status", sa.String(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("parameters_json", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("execution_id"),
    )
    op.create_index("ix_execution_records_intent_id", "execution_records", ["intent_id"])
    op.create_index("ix_execution_records_status", "execution_records", ["status"])


def downgrade() -> None:
    op.drop_index("ix_execution_records_status", table_name="execution_records")
    op.drop_index("ix_execution_records_intent_id", table_name="execution_records")
    op.drop_table("execution_records")
