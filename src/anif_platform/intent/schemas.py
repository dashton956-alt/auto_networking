"""Pydantic schemas for the Intent Engine — ANIF-301."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


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

    intent_id: UUID | None = None
    status: str  # "validated" | "validation_failed"
    errors: list[str] = []
    warnings: list[str] = []
    validated_intent: dict[str, Any] | None = None


class ValidatedIntent(BaseModel):
    """A registered, validated intent with its assigned UUID and Git provenance."""

    intent_id: UUID
    change_number: int
    version: str
    service: str
    status: str
    git_ref: GitIntentRef | None = None
    resolved_intent: dict[str, Any]
    warnings: list[str]
    created_at: datetime


class IntentListResponse(BaseModel):
    """Paginated intent listing — F2 Intent Dashboard list view."""

    items: list[ValidatedIntent]
    total: int
    limit: int
    offset: int
