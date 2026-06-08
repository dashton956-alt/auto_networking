"""Pydantic schemas for execution and rollback — ANIF-306 §9."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AdapterResponseSchema(BaseModel):
    """Embedded adapter response in execution result — ANIF-306 §9."""

    success: bool
    adapter_status_code: int
    adapter_message: str
    applied_changes: list[str]
    rollback_reference: str | None


class ExecuteRequest(BaseModel):
    """Request body for POST /execute — ANIF-306 §9, ANIF-725 §4.2."""

    intent_id: uuid.UUID
    decision_id: str
    action_type: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    governance_result: dict[str, Any]
    # ticket_id is required when governance_result.mode == manual_review
    ticket_id: str | None = None
    dry_run: bool = False
    # PipelineContext evidence required by ContainmentContract — ANIF-725 §4.2
    # Callers that have run individual pipeline stages must supply these fields.
    # ContainmentContract.validate() will reject requests with None mandatory fields.
    policy_result: dict[str, Any] | None = None
    risk_score_result: dict[str, Any] | None = None
    harm_classification_result: dict[str, Any] | None = None
    fairness_check_result: dict[str, Any] | None = None
    llm_validation_result: dict[str, Any] | None = None
    rollback_plan: dict[str, Any] | None = None


class ExecuteResponse(BaseModel):
    """Response from POST /execute — ANIF-306 §9."""

    execution_id: str
    intent_id: uuid.UUID
    decision_id: str
    action_type: str
    status: str  # success | failed | partial
    adapter_response: AdapterResponseSchema
    duration_ms: int
    rollback_available: bool
    rollback_status: str | None
    executed_at: datetime
    completed_at: datetime


class RollbackResponse(BaseModel):
    """Response from POST /rollback/{intent_id} — ANIF-306 §6.2."""

    intent_id: uuid.UUID
    execution_id: str
    action_type: str
    rollback_status: str  # success | failed
    adapter_response: AdapterResponseSchema
    duration_ms: int
    rolled_back_at: datetime
    audit_record_id: str
