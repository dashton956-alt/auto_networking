"""FastAPI router for Intent Engine endpoints — ANIF-301."""

from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from anif_platform.auth import get_api_key
from anif_platform.audit.writer import AuditWriter
from anif_platform.intent.registry import IntentRegistry
from anif_platform.intent.schemas import GitIntentRef, ValidatedIntent, ValidationResult
from anif_platform.intent.validator import IntentValidator
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage
from anif_platform.schemas.intent import Intent

router = APIRouter(prefix="/intent", tags=["intent"])


def get_intent_registry() -> IntentRegistry:
    raise NotImplementedError("Provide IntentRegistry via dependency injection")


def get_audit_writer() -> AuditWriter:
    raise NotImplementedError("Provide AuditWriter via dependency injection")


class ValidateIntentRequest(BaseModel):
    intent: dict[str, Any]
    git_ref: GitIntentRef | None = None


@router.post("/validate-intent", response_model=ValidationResult)
async def validate_intent(
    request: ValidateIntentRequest,
    registry: IntentRegistry = Depends(get_intent_registry),
    writer: AuditWriter = Depends(get_audit_writer),
    _: str = Depends(get_api_key),
) -> ValidationResult:
    """
    Validate an intent document and assign an intent_id if valid.

    Applies defaults, runs VAL-001–VAL-007, writes audit record,
    registers in the intents table if valid.
    — ANIF-301 §8
    """
    start = time.monotonic()

    try:
        intent_obj = Intent(**request.intent)
    except Exception as exc:
        return ValidationResult(
            status="validation_failed",
            errors=[str(exc)],
        )

    validator = IntentValidator()
    result = validator.validate(intent_obj)

    duration_ms = int((time.monotonic() - start) * 1000)
    outcome = AuditOutcome.success if result.intent_id else AuditOutcome.blocked

    # Write audit record before returning — ANIF-107 §4.3
    record = AuditRecord(
        intent_id=result.intent_id or uuid.uuid4(),
        stage=AuditStage.validate,
        input_summary={
            "service": request.intent.get("service"),
            "environment": request.intent.get("environment"),
        },
        output_summary={"status": result.status, "error_count": len(result.errors)},
        outcome=outcome,
        duration_ms=duration_ms,
    )
    await writer.write(record)

    if result.intent_id:
        await registry.register(result, request.git_ref)

    return result


@router.get("/intent/{intent_id}", response_model=ValidatedIntent)
async def get_intent(
    intent_id: uuid.UUID,
    registry: IntentRegistry = Depends(get_intent_registry),
    _: str = Depends(get_api_key),
) -> ValidatedIntent:
    """Return a registered intent by ID."""
    intent = await registry.get(intent_id)
    if intent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intent not found")
    return intent
