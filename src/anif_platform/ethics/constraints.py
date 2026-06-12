"""ANIF-721 agent action constraints — startup validator, rollback plan, strike service."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

import structlog
from pydantic import BaseModel, Field, field_validator

from anif_platform.exceptions import ANIFError
from anif_platform.schemas.action import ActionType

log = structlog.get_logger(__name__)

# ANIF-721 §4.1: the four valid action types — do not add or remove without council review
_VALID_ACTION_TYPES: frozenset[str] = frozenset({e.value for e in ActionType})


class ActionTypeViolationError(ANIFError):
    """Raised when an action type outside the bounded enum is encountered — ANIF-721 §4.4."""


class ActionTypeValidator:
    """Validates action types against the ANIF-721 bounded enum.

    Call validate_at_startup() once during application lifespan. Call
    validate_action_type() at every boundary where an action type value
    is received from outside the application.
    """

    @staticmethod
    def validate_action_type(action_type: str) -> None:
        """Raise ActionTypeViolationError if action_type is not in the bounded enum."""
        if action_type not in _VALID_ACTION_TYPES:
            log.warning(
                "action_type_violation",
                action_type=action_type,
                valid_types=sorted(_VALID_ACTION_TYPES),
            )
            raise ActionTypeViolationError(
                f"invalid action type {action_type!r} — "
                f"must be one of {sorted(_VALID_ACTION_TYPES)} (ANIF-721 §4)"
            )

    @staticmethod
    def validate_at_startup() -> None:
        """Verify the bounded enum is intact at application startup — ANIF-721 §4.2.

        Raises RuntimeError if any of the four required action types is missing.
        """
        required = {"reroute_traffic", "apply_qos", "scale_bandwidth", "isolate_segment"}
        missing = required - _VALID_ACTION_TYPES
        if missing:
            raise RuntimeError(
                f"ANIF-721 startup validation failed: action type enum is missing {missing}"
            )
        log.info("action_type_startup_validation_passed", valid_types=sorted(_VALID_ACTION_TYPES))


class RollbackPlan(BaseModel):
    """Confirmed rollback plan required by execute() — ANIF-721 §5.

    Must be constructed before execute() is called. execute() validates
    this object as its first operation.
    """

    rollback_action_type: str
    rollback_target: Annotated[str, Field(min_length=1)]
    rollback_within_seconds: Annotated[int, Field(ge=1)]
    rollback_confirmed_at: datetime

    @field_validator("rollback_action_type")
    @classmethod
    def must_be_valid_action_type(cls, v: str) -> str:
        """ANIF-721 §5.3: rollback_action_type must be in the bounded enum."""
        ActionTypeValidator.validate_action_type(v)
        return v

    @field_validator("rollback_confirmed_at")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v.astimezone(UTC)


class StrikeRecord(BaseModel):
    """Immutable strike record — never update or delete after creation."""

    strike_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    agent_id: uuid.UUID
    intent_id: uuid.UUID
    reason: str
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class StrikeService:
    """In-memory append-only strike counter for unit testing.

    Production deployments MUST replace this with a DB-backed implementation
    using StrikeRecordRow (see models.py), which enforces append-only at the
    database level via row-level security — ANIF-721 §7.2.
    """

    def __init__(self) -> None:
        self._records: list[StrikeRecord] = []

    def record_strike(
        self,
        agent_id: uuid.UUID,
        intent_id: uuid.UUID,
        reason: str,
    ) -> StrikeRecord:
        """Append a strike record. Never updates or deletes existing records."""
        record = StrikeRecord(agent_id=agent_id, intent_id=intent_id, reason=reason)
        self._records.append(record)
        log.info(
            "strike_recorded",
            agent_id=str(agent_id),
            intent_id=str(intent_id),
            reason=reason,
            strike_id=str(record.strike_id),
        )
        return record

    def count_strikes(self, agent_id: uuid.UUID, window_minutes: int) -> int:
        """Count strikes for an agent within the given time window."""
        cutoff = datetime.now(UTC) - timedelta(minutes=window_minutes)
        return sum(1 for r in self._records if r.agent_id == agent_id and r.recorded_at >= cutoff)
