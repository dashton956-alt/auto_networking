"""FastAPI router for Policy Engine endpoints — ANIF-302."""

from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from anif_platform.auth import get_api_key
from anif_platform.audit.writer import AuditWriter
from anif_platform.intent.registry import IntentRegistry
from anif_platform.policy.engine import PolicyEngine
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage

router = APIRouter(tags=["policy"])


def get_policy_engine() -> PolicyEngine:
    raise NotImplementedError("Provide PolicyEngine via dependency injection")


def get_intent_registry() -> IntentRegistry:
    raise NotImplementedError("Provide IntentRegistry via dependency injection")


def get_audit_writer() -> AuditWriter:
    raise NotImplementedError("Provide AuditWriter via dependency injection")


class EvaluatePolicyRequest(BaseModel):
    intent_id: uuid.UUID
    dry_run: bool = False


@router.post("/evaluate-policy", response_model=dict[str, Any])
async def evaluate_policy(
    request: EvaluatePolicyRequest,
    engine: PolicyEngine = Depends(get_policy_engine),
    registry: IntentRegistry = Depends(get_intent_registry),
    writer: AuditWriter = Depends(get_audit_writer),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """
    Evaluate all active policies against a validated intent.

    Writes audit record unless dry_run=True (ANIF-302 §10).
    — ANIF-302 §9
    """
    start = time.monotonic()

    intent = await registry.get(request.intent_id)
    if intent is None:
        return {
            "error": f"Intent {request.intent_id} not found",
            "intent_id": str(request.intent_id),
        }

    result = engine.evaluate(
        intent_id=str(request.intent_id),
        resolved_intent=intent.resolved_intent,
        dry_run=request.dry_run,
    )

    duration_ms = int((time.monotonic() - start) * 1000)
    outcome = AuditOutcome.failure if result["overall_result"] == "fail" else AuditOutcome.success

    # Dry-run MUST NOT write audit records (ANIF-302 §10)
    if not request.dry_run:
        record = AuditRecord(
            intent_id=request.intent_id,
            stage=AuditStage.policy,
            input_summary={"intent_id": str(request.intent_id)},
            output_summary={
                "overall_result": result["overall_result"],
                "policy_count": len(result["policy_results"]),
                "conflict_count": len(result["conflicts"]),
            },
            outcome=outcome,
            duration_ms=duration_ms,
            policies_evaluated=[r["policy_name"] for r in result["policy_results"]],
            policies_violated=[
                r["policy_name"] for r in result["policy_results"] if r["decision"] == "deny"
            ],
        )
        await writer.write(record)

    return result
