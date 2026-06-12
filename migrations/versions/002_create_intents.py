"""create intents table

Revision ID: 002
Revises: 001
Create Date: 2026-04-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intents",
        sa.Column("intent_id", UUID(as_uuid=True), nullable=False),
        sa.Column("change_number", sa.Integer, nullable=False, autoincrement=True),
        sa.Column("version", sa.String(64), nullable=False, server_default="0.1.0"),
        sa.Column("service", sa.String(256), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="validated"),
        # Git provenance
        sa.Column("git_repo_url", sa.Text, nullable=True),
        sa.Column("git_path", sa.Text, nullable=True),
        sa.Column("git_commit_sha", sa.String(40), nullable=True),
        # Fully resolved intent with defaults applied (ANIF-301 §6)
        sa.Column("resolved_intent", JSONB, nullable=False),
        # Validation metadata
        sa.Column("warnings", JSONB, nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("intent_id"),
        sa.UniqueConstraint("change_number", name="uq_intents_change_number"),
    )
    op.create_index("ix_intents_service", "intents", ["service"])
    op.create_index("ix_intents_status", "intents", ["status"])
    op.create_index("ix_intents_created_at", "intents", ["created_at"])
    op.create_index("ix_intents_git_commit_sha", "intents", ["git_commit_sha"])


def downgrade() -> None:
    op.drop_index("ix_intents_git_commit_sha", table_name="intents")
    op.drop_index("ix_intents_created_at", table_name="intents")
    op.drop_index("ix_intents_status", table_name="intents")
    op.drop_index("ix_intents_service", table_name="intents")
    op.drop_table("intents")
