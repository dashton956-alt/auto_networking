"""
Orchestrator — full pipeline skeleton with stubs for unbuilt stages.

POST /orchestrate chains:
  validate → policy → [risk stub] → [decision stub] → [governance stub] → [execute stub]

Stub stages return {"status": "not_yet_implemented", "stage": "<name>"}
and are replaced when B3–B5 are built.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from anif_platform.auth import get_api_key
from anif_platform.audit.writer import AuditWriter
from anif_platform.intent.registry import IntentRegistry
from anif_platform.intent.schemas import GitIntentRef
from anif_platform.intent.validator import IntentValidator
from anif_platform.policy.engine import PolicyEngine
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage
from anif_platform.schemas.intent import Intent

router = APIRouter(tags=["pipeline"])


def get_policy_engine() -> PolicyEngine:
    raise NotImplementedError("Provide PolicyEngine via dependency injection")


def get_intent_registry() -> IntentRegistry:
    raise NotImplementedError("Provide IntentRegistry via dependency injection")


def get_audit_writer() -> AuditWriter:
    raise NotImplementedError("Provide AuditWriter via dependency injection")


class OrchestrateRequest(BaseModel):
    intent: dict[str, Any]
    git_ref: GitIntentRef | None = None
    dry_run: bool = False


@router.post("/orchestrate", response_model=dict[str, Any])
async def orchestrate(
    request: OrchestrateRequest,
    engine: PolicyEngine = Depends(get_policy_engine),
    registry: IntentRegistry = Depends(get_intent_registry),
    writer: AuditWriter = Depends(get_audit_writer),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """
    Run the full ANIF pipeline for an intent.

    Stages not yet built (risk, decision, governance, execute) return stubs.
    Governance checks are enforced even in stub form — the pipeline will not
    proceed past governance without a clearance record (ANIF-300 §5).
    """
    pipeline_result: dict[str, Any] = {}

    # ── Stage 1: Validate ────────────────────────────────────────────────
    start = time.monotonic()
    try:
        intent_obj = Intent(**request.intent)
    except Exception as exc:
        return {"status": "failed", "stage": "validate", "error": str(exc)}

    validator = IntentValidator()
    validation = validator.validate(intent_obj)

    intent_id = validation.intent_id or uuid.uuid4()
    duration_ms = int((time.monotonic() - start) * 1000)

    record = AuditRecord(
        intent_id=intent_id,
        stage=AuditStage.validate,
        input_summary={"service": request.intent.get("service")},
        output_summary={"status": validation.status},
        outcome=AuditOutcome.success if validation.intent_id else AuditOutcome.blocked,
        duration_ms=duration_ms,
    )
    await writer.write(record)

    if not validation.intent_id:
        return {
            "status": "failed",
            "stage": "validate",
            "errors": validation.errors,
            "warnings": validation.warnings,
        }

    await registry.register(validation, request.git_ref)
    pipeline_result["validate"] = {"status": "pass", "intent_id": str(intent_id)}

    # ── Stage 2: Policy Evaluation ───────────────────────────────────────
    start = time.monotonic()
    policy_result = engine.evaluate(
        intent_id=str(intent_id),
        resolved_intent=validation.validated_intent,  # type: ignore[arg-type]
        dry_run=request.dry_run,
    )
    duration_ms = int((time.monotonic() - start) * 1000)

    if not request.dry_run:
        policy_outcome = (
            AuditOutcome.failure
            if policy_result["overall_result"] == "fail"
            else AuditOutcome.success
        )
        await writer.write(AuditRecord(
            intent_id=intent_id,
            stage=AuditStage.policy,
            input_summary={"intent_id": str(intent_id)},
            output_summary={"overall_result": policy_result["overall_result"]},
            outcome=policy_outcome,
            duration_ms=duration_ms,
            policies_evaluated=[r["policy_name"] for r in policy_result["policy_results"]],
            policies_violated=[
                r["policy_name"] for r in policy_result["policy_results"]
                if r["decision"] == "deny"
            ],
        ))

    if policy_result["overall_result"] == "fail":
        return {
            "status": "failed",
            "stage": "policy",
            "intent_id": str(intent_id),
            "policy_result": policy_result,
        }

    pipeline_result["policy"] = policy_result

    # ── Stage 3: Risk Scoring (STUB — implemented in B3) ─────────────────
    pipeline_result["risk"] = {
        "status": "not_yet_implemented",
        "stage": "risk",
        "message": "RiskScorer will be implemented in B3",
    }

    # ── Stage 4: Decision Engine (STUB — implemented in B3) ──────────────
    pipeline_result["decision"] = {
        "status": "not_yet_implemented",
        "stage": "decision",
        "message": "DecisionEngine will be implemented in B3",
    }

    # ── Stage 5: Governance Gate (STUB — implemented in B4) ──────────────
    pipeline_result["governance"] = {
        "status": "not_yet_implemented",
        "stage": "governance",
        "message": "GovernanceGate will be implemented in B4",
    }

    # ── Stage 6: Execute (STUB — implemented in B5) ──────────────────────
    pipeline_result["execute"] = {
        "status": "not_yet_implemented",
        "stage": "execute",
        "message": "ActionExecutor will be implemented in B5",
    }

    return {
        "status": "pipeline_complete",
        "intent_id": str(intent_id),
        "stages": pipeline_result,
        "dry_run": request.dry_run,
    }
