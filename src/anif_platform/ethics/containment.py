"""ANIF-725 pipeline containment contract — execute() mandatory parameter enforcement."""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from pydantic import BaseModel

from anif_platform.ethics.constraints import RollbackPlan
from anif_platform.exceptions import ANIFError

log = structlog.get_logger(__name__)


class ContainmentViolationError(ANIFError):
    """Raised when execute() is called without evidence that a required pipeline stage ran.

    This is a Severity 1 ethics incident — ANIF-725 §4.5.
    """


class PipelineContext(BaseModel):
    """Evidence that all eight required pipeline stages have run — ANIF-725 §4.2.

    Passed to execute() as the first parameter. execute() validates this object
    before any other logic runs. No default values are permitted for any field.
    """

    intent_id: uuid.UUID
    policy_result: dict[str, Any] | None
    risk_score_result: dict[str, Any] | None
    harm_classification_result: dict[str, Any] | None
    fairness_check_result: dict[str, Any] | None
    llm_validation_result: dict[str, Any] | None  # None permitted when no LLM was used
    governance_decision: dict[str, Any] | None
    rollback_plan: RollbackPlan | None


class ContainmentContract:
    """Validates that a PipelineContext has all mandatory fields populated.

    Call ContainmentContract.validate(ctx) as the first operation inside execute().
    Raises ContainmentViolationError if any mandatory parameter is missing.
    """

    # Fields that MUST be present — None is not permitted
    _MANDATORY_FIELDS = (
        "policy_result",
        "risk_score_result",
        "harm_classification_result",
        "fairness_check_result",
        "governance_decision",
        "rollback_plan",
    )

    @classmethod
    def validate(cls, ctx: PipelineContext) -> None:
        """Validate all mandatory fields are present. Raises ContainmentViolationError if not."""
        for field in cls._MANDATORY_FIELDS:
            if getattr(ctx, field) is None:
                log.critical(
                    "containment_violation_SEVERITY_1",
                    missing_field=field,
                    intent_id=str(ctx.intent_id),
                )
                raise ContainmentViolationError(
                    f"execute() called without {field} — "
                    f"Severity 1 ethics incident (ANIF-725 §4). "
                    f"intent_id={ctx.intent_id}"
                )
        log.debug("containment_contract_validated", intent_id=str(ctx.intent_id))
