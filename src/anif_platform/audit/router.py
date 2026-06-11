"""FastAPI router for audit query endpoints — ANIF-107 §4.5."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from anif_platform.audit.query import AuditQueryService
from anif_platform.auth import get_api_key

# The audit trail carries operational reasoning and operator identities;
# reads require the same API-key auth as every other router.
router = APIRouter(prefix="/audit", tags=["audit"], dependencies=[Depends(get_api_key)])


def get_audit_query_service() -> AuditQueryService:
    """FastAPI dependency — overridden in tests via app.dependency_overrides."""
    raise NotImplementedError("Provide AuditQueryService via dependency injection")


class HashChainVerification(BaseModel):
    valid: bool
    broken_at: str | None
    record_count: int


@router.get("/{intent_id}", response_model=list[dict[str, Any]])
async def get_audit_records(
    intent_id: uuid.UUID,
    service: AuditQueryService = Depends(get_audit_query_service),
) -> list[dict[str, Any]]:
    """
    Return all audit records for the given intent, ordered by timestamp ascending.

    Returns an empty list (not 404) if no records exist for a valid intent_id.
    Returns 404 only if intent_id is syntactically invalid (handled by FastAPI UUID parsing).

    — ANIF-107 §4.5.1, §4.5.3
    """
    return await service.get_by_intent(intent_id)


@router.get("/{intent_id}/why", response_model=str)
async def get_audit_why(
    intent_id: uuid.UUID,
    service: AuditQueryService = Depends(get_audit_query_service),
) -> str:
    """
    Return a human-readable explanation of the pipeline decision for this intent.

    Synthesised from reasoning_chain fields of all records for the intent.
    — ANIF-107 §4.5.6
    """
    return await service.get_why(intent_id)


@router.get("/{intent_id}/verify", response_model=HashChainVerification)
async def verify_hash_chain(
    intent_id: uuid.UUID,
    service: AuditQueryService = Depends(get_audit_query_service),
) -> dict[str, Any]:
    """
    Recompute the SHA-256 hash chain and return verification result.

    Returns {"valid": true/false, "broken_at": record_id or null, "record_count": int}.
    — ANIF-107 §4.7.3
    """
    return await service.verify_chain(intent_id)


@router.get("", response_model=list[dict[str, Any]])
async def list_audit_records(
    stage: str | None = Query(None),
    outcome: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    operator_id: str | None = Query(None),
    action_type: str | None = Query(None),
    environment: str | None = Query(None),
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: AuditQueryService = Depends(get_audit_query_service),
) -> list[dict[str, Any]]:
    """
    Return paginated, filterable audit records.

    Filters: stage, outcome, date_from, date_to, operator_id, action_type, environment.
    Default page size: 50. Maximum page size: 1000.
    — ANIF-107 §4.5.2, §4.5.4
    """
    return await service.list_records(
        stage=stage,
        outcome=outcome,
        date_from=date_from,
        date_to=date_to,
        operator_id=operator_id,
        action_type=action_type,
        environment=environment,
        limit=limit,
        offset=offset,
    )
