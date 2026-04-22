"""Pydantic schemas for governance check and approval tickets — ANIF-404, ANIF-406."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PolicyResultEntry(BaseModel):
    policy_id: str
    outcome: str  # "pass" | "fail"
    safety_decision: str | None = None  # "block" | "warn" | None


class GovernanceCheckRequest(BaseModel):
    intent_id: uuid.UUID
    operator_id: str
    operator_roles: list[str]
    action_type: str
    environment: str
    risk_score: int = Field(ge=0, le=100)
    trust_score: int = Field(ge=0, le=100)
    policy_results: list[PolicyResultEntry] = Field(default_factory=list)
    trace_id: uuid.UUID


class GovernanceCheckResponse(BaseModel):
    intent_id: uuid.UUID
    mode: str  # "auto" | "manual_review" | "block"
    triggered_rule: str  # comma-separated rule IDs, or "none"
    rationale: str
    ticket_id: str | None = None
    ticket_expires_at: datetime | None = None
    audit_record_id: str
    trace_id: uuid.UUID


class ApprovalTicket(BaseModel):
    """Pydantic projection of ApprovalTicketRow — ANIF-404 §4.4.1."""

    ticket_id: str
    intent_id: uuid.UUID
    decision_summary: str
    risk_score: int
    requested_by: str
    created_at: datetime
    expires_at: datetime
    status: str
    required_approver_role: str

    model_config = {"from_attributes": True}


class ApproveRequest(BaseModel):
    approver_role: str
    notes: str | None = None


class ApproveResponse(BaseModel):
    ticket_id: str
    status: str
    approved_by: str
    approved_at: datetime
    audit_record_id: str


class RejectRequest(BaseModel):
    reason: str


class RejectResponse(BaseModel):
    ticket_id: str
    status: str
    rejected_by: str
    rejected_at: datetime
    audit_record_id: str


class HaltRequest(BaseModel):
    reason: str
    operator_id: str


class HaltResponse(BaseModel):
    intent_id: uuid.UUID
    halt_status: str
    rollback_initiated: bool
    rollback_status: str
    audit_record_id: str
    halted_by: str
    halted_at: datetime
