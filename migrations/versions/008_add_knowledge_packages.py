"""Add knowledge_packages and knowledge_source_quality tables — ANIF-812.

Revision ID: 008
Revises: 007
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_packages",
        sa.Column("package_id", sa.String(36), primary_key=True),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("target_roles_json", sa.Text, nullable=False),
        sa.Column("submitted_by", sa.String(128), nullable=False),
        sa.Column("approval_status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("approver_id", sa.String(128), nullable=True),
        sa.Column("approval_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reject_reason", sa.Text, nullable=True),
        sa.Column("knowledge_items_json", sa.Text, nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "knowledge_source_quality",
        sa.Column("source_id", sa.String(128), primary_key=True),
        sa.Column("quality_score", sa.Float, nullable=False),
        sa.Column("flagged", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("knowledge_source_quality")
    op.drop_table("knowledge_packages")
