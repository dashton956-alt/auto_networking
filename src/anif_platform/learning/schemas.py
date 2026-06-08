"""Pydantic schemas for the Learning Agent — ANIF-812."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class NegativeExampleSource(StrEnum):
    failed_intent = "failed_intent"
    human_override = "human_override"
    ethics_violation = "ethics_violation"
    rollback = "rollback"


class KnowledgeItemInput(BaseModel):
    type: Literal["positive_example", "negative_example", "pattern", "fact"]
    description: str
    source: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str | None  # MUST be a verifiable record reference — CR-812-02
    applicable_conditions: str = ""


class KnowledgePackageInput(BaseModel):
    category: Literal["network_pattern", "operational", "resolution"]
    target_roles: list[str]
    submitted_by: str
    knowledge_items: list[KnowledgeItemInput]


class KnowledgePackageResponse(BaseModel):
    package_id: str
    category: str
    target_roles: list[str]
    approval_status: Literal["pending", "approved", "rejected"]
    submitted_at: str
