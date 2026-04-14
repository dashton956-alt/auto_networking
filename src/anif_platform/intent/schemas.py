"""Pydantic schemas for the Intent Engine — ANIF-301."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel

from anif_platform.schemas.intent import Intent


class GitIntentRef(BaseModel):
    """Provenance of an intent sourced from Git."""

    repo_url: str
    path: str
    commit_sha: str


class ValidationResult(BaseModel):
    """
    Result of validating an intent document — ANIF-301 §8.

    On success: intent_id is assigned, validated_intent has defaults applied.
    On failure: intent_id is None, errors is non-empty.
    """

    intent_id: Optional[UUID] = None
    status: str  # "validated" | "validation_failed"
    errors: list[str] = []
    warnings: list[str] = []
    validated_intent: Optional[dict[str, Any]] = None


class ValidatedIntent(BaseModel):
    """A registered, validated intent with its assigned UUID and Git provenance."""

    intent_id: UUID
    change_number: int
    version: str
    service: str
    status: str
    git_ref: Optional[GitIntentRef] = None
    resolved_intent: dict[str, Any]
    warnings: list[str]
    created_at: datetime
