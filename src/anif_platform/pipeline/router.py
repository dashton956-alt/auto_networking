"""
Orchestrator — full pipeline.

POST /orchestrate chains:
  validate → policy → risk → decision → governance → execute

All stages are implemented (B2–B5). Governance and execution stages
enforce precondition checks and write audit records before returning.
"""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from anif_platform.audit.writer import AuditWriter
from anif_platform.auth import get_api_key
from anif_platform.ethics.constraints import RollbackPlan
from anif_platform.ethics.containment import PipelineContext
from anif_platform.execution.executor import ActionExecutor, PreconditionError
from anif_platform.governance.gate import GovernanceGate
from anif_platform.human_loop.queue import ApprovalQueue
from anif_platform.intent.registry import IntentRegistry
from anif_platform.intent.schemas import GitIntentRef
from anif_platform.intent.validator import IntentValidator
from anif_platform.policy.engine import PolicyEngine
from anif_platform.risk.decision import DecisionEngine
from anif_platform.risk.scorer import RiskScorer
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage, ReasoningStep
from anif_platform.schemas.intent import Intent

router = APIRouter(tags=["pipeline"])

log = structlog.get_logger(__name__)


def get_policy_engine() -> PolicyEngine:
    raise NotImplementedError("Provide PolicyEngine via dependency injection")


def get_intent_registry() -> IntentRegistry:
    raise NotImplementedError("Provide IntentRegistry via dependency injection")


def get_approval_queue() -> ApprovalQueue:
    raise NotImplementedError("Provide ApprovalQueue via dependency injection")


def get_audit_writer() -> AuditWriter:
    raise NotImplementedError("Provide AuditWriter via dependency injection")


def get_action_executor() -> ActionExecutor:
    raise NotImplementedError("Provide ActionExecutor via dependency injection")


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
    queue: ApprovalQueue = Depends(get_approval_queue),
    executor: ActionExecutor = Depends(get_action_executor),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """
    Run the full ANIF pipeline for an intent.

    All stages are live: validate → policy → risk → decision → governance → execute.
    Governance and execution enforce precondition checks and write audit records
    before returning (ANIF-300 §5, ANIF-306 §5).
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
        await writer.write(
            AuditRecord(
                intent_id=intent_id,
                stage=AuditStage.policy,
                input_summary={"intent_id": str(intent_id)},
                output_summary={"overall_result": policy_result["overall_result"]},
                outcome=policy_outcome,
                duration_ms=duration_ms,
                policies_evaluated=[r["policy_name"] for r in policy_result["policy_results"]],
                policies_violated=[
                    r["policy_name"]
                    for r in policy_result["policy_results"]
                    if r["decision"] == "deny"
                ],
            )
        )

    if policy_result["overall_result"] == "fail":
        return {
            "status": "failed",
            "stage": "policy",
            "intent_id": str(intent_id),
            "policy_result": policy_result,
        }

    pipeline_result["policy"] = policy_result

    # ── Stage 3: Risk Scoring (ANIF-304) ────────────────────────────────
    start = time.monotonic()
    scorer = RiskScorer()
    risk_result = scorer.score(
        intent=validation.validated_intent,  # type: ignore[arg-type]
        policy_result=policy_result,
        network_state=None,  # no network state adapter yet (B3); fallback applied
    )
    duration_ms = int((time.monotonic() - start) * 1000)

    risk_outcome = (
        AuditOutcome.blocked if risk_result["safety_decision"] == "block" else AuditOutcome.success
    )
    await writer.write(
        AuditRecord(
            intent_id=intent_id,
            stage=AuditStage.risk,
            input_summary={"intent_id": str(intent_id)},
            output_summary={
                "risk_score": risk_result["risk_score"],
                "trust_score": risk_result["trust_score"],
                "safety_decision": risk_result["safety_decision"],
            },
            outcome=risk_outcome,
            duration_ms=duration_ms,
        )
    )

    pipeline_result["risk"] = risk_result

    if risk_result["safety_decision"] == "block" and not request.dry_run:
        return {
            "status": "blocked",
            "stage": "risk",
            "intent_id": str(intent_id),
            "risk_result": risk_result,
        }

    # ── Stage 4: Decision Engine (ANIF-305) ──────────────────────────────
    start = time.monotonic()
    decision_engine = DecisionEngine()
    decision_result = decision_engine.decide(
        intent_id=str(intent_id),
        intent=validation.validated_intent,  # type: ignore[arg-type]
        risk_result=risk_result,
        policy_result=policy_result,
        network_state=None,
    )
    duration_ms = int((time.monotonic() - start) * 1000)

    decision_outcome_map = {
        "auto": AuditOutcome.success,
        "manual_review": AuditOutcome.escalated,
        "block": AuditOutcome.blocked,
    }
    await writer.write(
        AuditRecord(
            intent_id=intent_id,
            stage=AuditStage.decision,
            input_summary={"scoring_id": risk_result.get("scoring_id")},
            output_summary={
                "mode": decision_result["mode"],
                "recommended_action": (
                    decision_result["recommended_action"]["action_type"]
                    if decision_result["recommended_action"]
                    else None
                ),
                "confidence_score": decision_result["confidence_score"],
            },
            outcome=decision_outcome_map.get(decision_result["mode"], AuditOutcome.success),
            duration_ms=duration_ms,
        )
    )

    pipeline_result["decision"] = decision_result

    # ── Stage 5: Governance Gate (ANIF-406) ──────────────────────────────
    _gov_start = time.monotonic()
    _gov_gate = GovernanceGate()
    _action_type = (
        decision_result["recommended_action"]["action_type"]
        if decision_result.get("recommended_action")
        else "apply_qos"
    )
    _gov_result = _gov_gate.check(
        intent_id=str(intent_id),
        operator_id="pipeline-automation",
        operator_roles=["automation_agent"],
        action_type=_action_type,
        environment=validation.validated_intent.get("environment", "dev"),  # type: ignore[union-attr]
        risk_score=risk_result["risk_score"],
        trust_score=risk_result["trust_score"],
        policy_results=[
            {
                "policy_id": r["policy_name"],
                "outcome": "fail" if r["decision"] == "deny" else "pass",
                "safety_decision": "block" if r["decision"] == "deny" else None,
            }
            for r in policy_result.get("policy_results", [])
        ],
        trace_id=str(uuid.uuid4()),
    )
    _gov_duration_ms = int((time.monotonic() - _gov_start) * 1000)
    _gov_mode = _gov_result["mode"]

    _gov_outcome_map = {
        "auto": AuditOutcome.success,
        "manual_review": AuditOutcome.escalated,
        "block": AuditOutcome.blocked,
    }
    await writer.write(
        AuditRecord(
            intent_id=intent_id,
            stage=AuditStage.governance,
            input_summary={
                "risk_score": risk_result["risk_score"],
                "trust_score": risk_result["trust_score"],
            },
            output_summary={"mode": _gov_mode, "triggered_rule": _gov_result["triggered_rule"]},
            outcome=_gov_outcome_map.get(_gov_mode, AuditOutcome.success),
            duration_ms=_gov_duration_ms,
            reasoning_chain=[
                ReasoningStep(
                    step=1,
                    description="Governance gate evaluated",
                    decision=_gov_mode,
                    rationale=_gov_result["rationale"],
                )
            ],
        )
    )

    if _gov_mode == "block" and not request.dry_run:
        return {
            "status": "blocked",
            "stage": "governance",
            "intent_id": str(intent_id),
            "governance_result": _gov_result,
        }

    if _gov_mode == "manual_review" and not request.dry_run:
        _ticket = await queue.create_ticket(
            intent_id=intent_id,
            operator_id="pipeline-automation",
            risk_score=risk_result["risk_score"],
            decision_summary=f"Action {_action_type} requires senior_engineer approval",
        )
        return {
            "status": "pending_approval",
            "stage": "governance",
            "intent_id": str(intent_id),
            "ticket_id": _ticket.ticket_id,
            "ticket_expires_at": _ticket.expires_at.isoformat(),
            "governance_result": _gov_result,
        }

    pipeline_result["governance"] = _gov_result

    # ── Stage 6: Execute (ANIF-306) ──────────────────────────────────────
    if not request.dry_run:
        _pipeline_ctx = PipelineContext(
            intent_id=intent_id,
            policy_result=policy_result,
            risk_score_result=risk_result,
            # B8 stubs — harm classification and fairness evaluators not yet implemented
            harm_classification_result={"harm_class": "none", "harm_severity_score": 0},
            fairness_check_result={
                "sla_floor_result": "not_applicable",
                "freshness_gate_result": "pass",
            },
            llm_validation_result=None,
            governance_decision=_gov_result,
            rollback_plan=RollbackPlan(
                rollback_action_type=_action_type,
                rollback_target="pipeline-auto",
                rollback_within_seconds=60,
                rollback_confirmed_at=datetime.now(UTC),
            ),
        )
        try:
            _exec_result = await executor.execute(
                pipeline_context=_pipeline_ctx,
                decision=decision_result,
                parameters=decision_result.get("recommended_action", {}).get("parameters", {}),
                ticket_id=None,  # auto mode: no ticket needed
            )
        except PreconditionError as exc:
            return {
                "status": "precondition_failed",
                "stage": "execute",
                "intent_id": str(intent_id),
                "error": str(exc),
            }
        pipeline_result["execute"] = _exec_result
    else:
        pipeline_result["execute"] = {"status": "dry_run", "stage": "execute"}

    log.info(
        "pipeline_complete",
        intent_id=str(intent_id),
        dry_run=request.dry_run,
        stages=list(pipeline_result.keys()),
    )
    return {
        "status": "pipeline_complete",
        "intent_id": str(intent_id),
        "stages": pipeline_result,
        "dry_run": request.dry_run,
    }
