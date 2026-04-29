"""Pydantic schemas for agent infrastructure — ANIF-801, ANIF-803, ANIF-805, ANIF-843."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentLifecycleState(str, Enum):
    """Agent lifecycle states — ANIF-803 §4."""

    PROPOSED = "PROPOSED"
    PROVISIONAL = "PROVISIONAL"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    DECOMMISSIONED = "DECOMMISSIONED"
    UNTRUSTED = "UNTRUSTED"


class AgentTier(int, Enum):
    """Agent tier classification — ANIF-801 §4–7."""

    TIER_0 = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class RegisterAgentRequest(BaseModel):
    agent_id: str = Field(..., description="Unique agent instance identifier")
    agent_type: str = Field(..., description="Registered agent type from ANIF-801 catalogue")
    role: str = Field(..., description="Role from ANIF-801 role catalogue")
    tier: int = Field(..., ge=0, le=3, description="Agent tier 0–3")
    manifest: dict[str, Any] = Field(..., description="Agent capability manifest")


class RegisterAgentResponse(BaseModel):
    agent_id: str
    lifecycle_state: AgentLifecycleState
    provisional_until: datetime | None
    certificate_pem: str | None
    registered_at: datetime


class TransitionRequest(BaseModel):
    new_state: AgentLifecycleState
    trigger: str = Field(..., description="Event that caused the transition")
    approver_identity: str = Field(..., description="Identity of the approving operator")
    reason: str = Field(..., description="Human-readable reason for transition")


class TransitionResponse(BaseModel):
    agent_id: str
    previous_state: AgentLifecycleState
    new_state: AgentLifecycleState
    event_id: str
    transitioned_at: datetime


class AgentDetailResponse(BaseModel):
    agent_id: str
    agent_type: str
    role: str
    tier: int
    lifecycle_state: AgentLifecycleState
    strike_count: int
    provisional_until: datetime | None
    capabilities_hash: str
    certificate_expires_at: datetime | None
    last_intent_id: str | None
    last_intent_at: datetime | None
    working_context_cleared_at: datetime | None
    registered_at: datetime


class AgentListResponse(BaseModel):
    agents: list[AgentDetailResponse]
    total: int
