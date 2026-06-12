"""add strike_records table with append-only RLS

Revision ID: 006
Revises: 005
Create Date: 2026-06-08
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "strike_records",
        sa.Column("strike_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("intent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.String(255), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_strike_records_agent_id", "strike_records", ["agent_id"])

    # ANIF-721 §7.2: enforce append-only at the database level.
    # The application role must NOT be able to UPDATE or DELETE strike records.
    op.execute(
        """
        ALTER TABLE strike_records ENABLE ROW LEVEL SECURITY;
        CREATE POLICY strike_records_insert_only
            ON strike_records
            FOR ALL
            USING (true)
            WITH CHECK (true);
        REVOKE UPDATE, DELETE ON strike_records FROM PUBLIC;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS strike_records_insert_only ON strike_records")
    op.drop_table("strike_records")
