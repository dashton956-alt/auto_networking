"""add_approval_tickets

Revision ID: 003
Revises: 002
Create Date: 2026-04-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "approval_tickets",
        sa.Column("ticket_id", sa.String(), nullable=False),
        sa.Column("intent_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("requested_by", sa.String(), nullable=False),
        sa.Column("decision_summary", sa.String(), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("required_approver_role", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_by", sa.String(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_by", sa.String(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.String(), nullable=True),
        sa.Column("approval_notes", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("ticket_id"),
    )
    op.create_index("ix_approval_tickets_intent_id", "approval_tickets", ["intent_id"])
    op.create_index("ix_approval_tickets_status", "approval_tickets", ["status"])


def downgrade() -> None:
    op.drop_index("ix_approval_tickets_status", table_name="approval_tickets")
    op.drop_index("ix_approval_tickets_intent_id", table_name="approval_tickets")
    op.drop_table("approval_tickets")
