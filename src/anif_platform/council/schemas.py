"""Pydantic schemas for Council API — ANIF-903/904/905."""

from __future__ import annotations

import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field


class BuildTimeReviewRequest(BaseModel):
    trigger: Literal[
        "new_agent_deployment",
        "model_version_change",
        "capability_expansion",
        "trust_reinstatement",
    ]
    agent_id: str
    submitted_by: str
    required_inputs: dict[str, Any]


class RuntimeCouncilRequest(BaseModel):
    intent_id: uuid.UUID
    trigger_condition: str
    harm_severity_score: int = 0
    risk_score: int = Field(ge=0, le=100)
    ethics_flag: Literal["present", "absent"] = "absent"
    reversibility: Literal["reversible", "partially_reversible", "irreversible"] = "reversible"
    novelty: Literal["novel", "precedented"] = "precedented"
    strike_history: Literal["active_strike", "historical_strike", "none"] = "none"
    time_pressure: Literal["critical", "elevated", "normal"] = "normal"


class ReviewCouncilRequest(BaseModel):
    incident_id: str
    incident_type: Literal["ethics", "security"]
    severity_level: str  # e.g. "severity_1", "level_3", "level_4"
    incident_closed_at: str  # ISO 8601


class CouncilCondition(BaseModel):
    condition_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    condition_text: str
    due_date: str  # ISO 8601
    responsible_seat: str


class CouncilDecision(BaseModel):
    council_id: str
    decision: Literal["approved", "blocked", "conditional", "deferred", "escalated"]
    decision_rationale: str
    votes: list[dict[str, Any]] = Field(default_factory=list)
    anif_references: list[str] = Field(default_factory=list)
    conditions: list[CouncilCondition] = Field(default_factory=list)


class ReviewDecision(BaseModel):
    council_id: str
    accountability_determination: dict[str, Any] | None
    policy_change_recommendations: list[dict[str, Any]] = Field(default_factory=list)
    learning_packages: list[dict[str, Any]] = Field(default_factory=list)
