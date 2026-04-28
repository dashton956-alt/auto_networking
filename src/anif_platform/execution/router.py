"""
Execution router — ANIF-306.

POST /execute                    — execute an approved action
POST /rollback/{intent_id}       — manual rollback
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from anif_platform.auth import get_api_key
from anif_platform.execution.executor import ActionExecutor, PreconditionError
from anif_platform.execution.schemas import ExecuteRequest

log = structlog.get_logger(__name__)
router = APIRouter(tags=["execution"])


def get_action_executor() -> ActionExecutor:
    raise NotImplementedError("Override via dependency injection")


@router.post("/execute", response_model=dict[str, Any])
async def execute_action(
    request: ExecuteRequest,
    executor: ActionExecutor = Depends(get_action_executor),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """
    Execute an approved action — ANIF-306 §6.1.

    Returns 403 if governance preconditions are not met.
    """
    if request.dry_run:
        return {
            "execution_id": str(uuid.uuid4()),
            "intent_id": str(request.intent_id),
            "decision_id": request.decision_id,
            "action_type": request.action_type,
            "status": "dry_run",
            "adapter_response": None,
            "duration_ms": 0,
            "rollback_available": False,
            "rollback_status": None,
            "executed_at": None,
            "completed_at": None,
        }

    try:
        result = await executor.execute(
            intent_id=request.intent_id,
            decision={
                "decision_id": request.decision_id,
                "recommended_action": {
                    "action_type": request.action_type,
                    "parameters": request.parameters,
                    "risk_level": "medium",
                },
            },
            parameters=request.parameters,
            governance_result=request.governance_result,
            ticket_id=request.ticket_id,
        )
    except PreconditionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return result


@router.post("/rollback/{intent_id}", response_model=dict[str, Any])
async def rollback_action(
    intent_id: uuid.UUID,
    executor: ActionExecutor = Depends(get_action_executor),
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """
    Roll back the most recent execution for an intent — ANIF-306 §6.2.

    Callable using only intent_id.
    """
    try:
        result = await executor.rollback(intent_id=intent_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return result
