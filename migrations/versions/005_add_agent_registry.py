"""add_agent_registry

Revision ID: 005
Revises: 004
Create Date: 2026-04-29
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_registry",
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("agent_type", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("tier", sa.Integer(), nullable=False),
        sa.Column("lifecycle_state", sa.String(), nullable=False),
        sa.Column("strike_count", sa.Integer(), nullable=False),
        sa.Column("provisional_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("capabilities_hash", sa.String(), nullable=False),
        sa.Column("certificate_pem", sa.Text(), nullable=True),
        sa.Column("certificate_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_intent_id", sa.String(), nullable=True),
        sa.Column("last_intent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("working_context_cleared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("manifest_json", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("agent_id"),
    )
    op.create_table(
        "agent_lifecycle_events",
        sa.Column("event_id", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), sa.ForeignKey("agent_registry.agent_id"), nullable=False),
        sa.Column("previous_state", sa.String(), nullable=False),
        sa.Column("new_state", sa.String(), nullable=False),
        sa.Column("trigger", sa.String(), nullable=False),
        sa.Column("approver_identity", sa.String(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("transitioned_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index("ix_lifecycle_events_agent_id", "agent_lifecycle_events", ["agent_id"])
    op.create_table(
        "decommissioned_identities",
        sa.Column("record_id", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("agent_type", sa.String(), nullable=False),
        sa.Column("tier", sa.Integer(), nullable=False),
        sa.Column("capabilities_hash", sa.String(), nullable=False),
        sa.Column("decommissioned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decommissioned_by", sa.String(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("record_id"),
    )
    op.create_index(
        "ix_decommissioned_identities_agent_id", "decommissioned_identities", ["agent_id"]
    )
    op.create_table(
        "agent_revocation_list",
        sa.Column("revocation_id", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("revocation_id"),
    )
    op.create_index("ix_revocation_list_agent_id", "agent_revocation_list", ["agent_id"])


def downgrade() -> None:
    op.drop_index("ix_revocation_list_agent_id", table_name="agent_revocation_list")
    op.drop_table("agent_revocation_list")
    op.drop_index("ix_decommissioned_identities_agent_id", table_name="decommissioned_identities")
    op.drop_table("decommissioned_identities")
    op.drop_index("ix_lifecycle_events_agent_id", table_name="agent_lifecycle_events")
    op.drop_table("agent_lifecycle_events")
    op.drop_table("agent_registry")
