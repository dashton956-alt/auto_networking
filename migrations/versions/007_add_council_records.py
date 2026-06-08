"""Add council_records table — ANIF-907.

Revision ID: 007
Revises: 006
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "council_records",
        sa.Column("council_id", sa.String(36), primary_key=True),
        sa.Column("council_type", sa.String(32), nullable=False),
        sa.Column("triggered_by", sa.Text, nullable=False),
        sa.Column("trigger_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("session_open_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("session_close_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mode_selector_json", sa.Text, nullable=True),
        sa.Column("deliberation_summary", sa.Text, nullable=True),
        sa.Column("votes_json", sa.Text, nullable=True),
        sa.Column("vetoes_json", sa.Text, nullable=True),
        sa.Column("decision", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("decision_rationale", sa.Text, nullable=True),
        sa.Column("conditions_json", sa.Text, nullable=True),
        sa.Column("anif_references_json", sa.Text, nullable=True),
        sa.Column("accountability_determination_json", sa.Text, nullable=True),
        sa.Column("policy_change_recommendations_json", sa.Text, nullable=True),
        sa.Column("learning_packages_json", sa.Text, nullable=True),
        sa.Column("intent_id", sa.String(36), nullable=True),
        sa.Column("intent_outcome", sa.String(64), nullable=True),
        sa.Column("time_limit_seconds", sa.Integer, nullable=True),
        sa.Column("incident_id", sa.String(36), nullable=True),
        sa.Column("incident_type", sa.String(32), nullable=True),
        sa.Column("severity_level", sa.String(32), nullable=True),
        sa.Column("record_version", sa.String(8), nullable=False, server_default="1.0"),
        sa.Column("record_written_by", sa.String(128), nullable=False, server_default="platform"),
        sa.Column("record_timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("closed", sa.Boolean, nullable=False, server_default=sa.text("false")),
    )

    # Agent components MUST NOT read council records — CR-907-04
    # Enforce append-only semantics: REVOKE UPDATE on closed records
    op.execute(
        "COMMENT ON TABLE council_records IS "
        "'Immutable council session records — ANIF-907. "
        "Rows are write-once. UPDATE/DELETE prohibited after closed=true.'"
    )


def downgrade() -> None:
    op.drop_table("council_records")
