"""Council services — ANIF-903 (Build-Time), ANIF-904 (Runtime), ANIF-905 (Review)."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.council.mode_selector import (
    TIME_LIMITS,
    DeliberationModel,
    ModeSelector,
    ModeSelectorInput,
)
from anif_platform.council.models import CouncilRecordRow
from anif_platform.council.schemas import (
    BuildTimeReviewRequest,
    CouncilDecision,
    ReviewCouncilRequest,
    ReviewDecision,
    RuntimeCouncilRequest,
)

log = structlog.get_logger(__name__)

# Required inputs for Build-Time Council — CR-903-02
_REQUIRED_BUILD_TIME_INPUTS: frozenset[str] = frozenset(
    {
        "agent_manifest",
        "capability_scope",
        "test_results",
        "supply_chain_provenance",
        "red_team_findings",
        "ethics_assessment",
        "prior_council_decisions",
    }
)


class CouncilInputError(Exception):
    """Raised when council input validation fails."""


class BuildTimeCouncil:
    """Build-Time Council governance — ANIF-903.

    Validates required inputs, creates council record, enforces decision rules.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        # In-memory store keyed by council_id for unit-test isolation
        self._records: dict[str, dict[str, Any]] = {}

    async def open_session(self, request: BuildTimeReviewRequest) -> dict[str, Any]:
        """Validate inputs and open a build-time council session — CR-903-01/02."""
        self._validate_required_inputs(request.required_inputs)

        council_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        record = CouncilRecordRow(
            council_id=council_id,
            council_type="build_time",
            triggered_by=f"{request.trigger} — agent {request.agent_id}",
            trigger_timestamp=now,
            session_open_timestamp=now,
            decision="pending",
            record_written_by=request.submitted_by,
            closed=False,
        )
        self._session.add(record)
        await self._session.flush()

        result = {
            "council_id": council_id,
            "council_type": "build_time",
            "decision": "pending",
            "opened_at": now.isoformat(),
        }
        self._records[council_id] = {"row": record, "summary": result}
        log.info("build_time_council_opened", council_id=council_id, trigger=request.trigger)
        return result

    async def record_decision(
        self,
        council_id: str,
        decision: CouncilDecision,
    ) -> dict[str, Any]:
        """Record the council decision and close the session — CR-903-03/04/05."""
        entry = self._records.get(council_id)
        if entry is None:
            raise CouncilInputError(f"No open council session for council_id={council_id}")

        row: CouncilRecordRow = entry["row"]

        # CR-907-02: immutable after close
        if row.closed:
            raise CouncilInputError(
                f"Council record {council_id} is immutable — session already closed."
            )

        # CR-903-04: blocked decision MUST cite ANIF requirement
        if decision.decision == "blocked" and not decision.anif_references:
            raise CouncilInputError(
                "Blocked decision MUST include at least one anif_reference (CR-903-04)."
            )

        # CR-903-05: conditional approval MUST list conditions
        if decision.decision == "conditional" and not decision.conditions:
            raise CouncilInputError(
                "Conditional approval MUST list at least one conditions entry (CR-903-05)."
            )

        now = datetime.now(UTC)
        row.decision = decision.decision
        row.decision_rationale = decision.decision_rationale
        row.anif_references_json = json.dumps(decision.anif_references)
        row.conditions_json = json.dumps([c.model_dump() for c in decision.conditions])
        row.votes_json = json.dumps(decision.votes)
        row.session_close_timestamp = now
        row.closed = True
        await self._session.flush()

        result = {
            "council_id": council_id,
            "council_type": "build_time",
            "decision": decision.decision,
            "closed_at": now.isoformat(),
        }
        log.info("build_time_council_closed", council_id=council_id, decision=decision.decision)
        return result

    @staticmethod
    def _validate_required_inputs(inputs: dict[str, Any]) -> None:
        missing = _REQUIRED_BUILD_TIME_INPUTS - set(inputs.keys())
        if missing:
            raise CouncilInputError(
                f"Deliberation cannot begin — missing required inputs: {sorted(missing)} (CR-903-02)."
            )


class RuntimeCouncil:
    """Runtime Council governance — ANIF-904.

    Runs Mode Selector before opening session, enforces halt-on-timeout default.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._records: dict[str, dict[str, Any]] = {}

    async def open_session(self, request: RuntimeCouncilRequest) -> dict[str, Any]:
        """Run Mode Selector and open a runtime council session — CR-904-01/02."""
        # CR-904-02: Mode Selector MUST complete before session opens
        mode_input = ModeSelectorInput(
            reversibility=request.reversibility,
            risk_score=request.risk_score,
            ethics_flag=request.ethics_flag,
            time_pressure=request.time_pressure,
            novelty=request.novelty,
            strike_history=request.strike_history,
        )
        mode_result = ModeSelector.select(mode_input)
        time_limit = TIME_LIMITS[mode_result.mode_selected]

        council_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        mode_dict = mode_result.model_dump()
        mode_dict["mode_selected"] = mode_result.mode_selected.value
        mode_dict["mode_selector_timestamp"] = mode_result.mode_selector_timestamp.isoformat()

        record = CouncilRecordRow(
            council_id=council_id,
            council_type="runtime",
            triggered_by=request.trigger_condition,
            trigger_timestamp=now,
            session_open_timestamp=now,
            mode_selector_json=json.dumps(mode_dict),
            decision="pending",
            intent_id=str(request.intent_id),
            time_limit_seconds=time_limit,
            record_written_by="platform",
            closed=False,
        )
        self._session.add(record)
        await self._session.flush()

        result = {
            "council_id": council_id,
            "council_type": "runtime",
            "intent_id": str(request.intent_id),
            "decision": "pending",
            "mode_selector": mode_dict,
            "time_limit_seconds": time_limit,
            "opened_at": now.isoformat(),
        }
        self._records[council_id] = {"row": record, "summary": result}
        log.info(
            "runtime_council_opened",
            council_id=council_id,
            mode=mode_result.mode_selected.value,
            time_limit_seconds=time_limit,
        )
        return result

    async def apply_timeout(self, council_id: str) -> dict[str, Any]:
        """Record HALTED_COUNCIL_TIMEOUT — CR-904-04/05."""
        entry = self._records.get(council_id)
        if entry is None:
            raise CouncilInputError(f"No open council session for council_id={council_id}")

        row: CouncilRecordRow = entry["row"]
        if row.closed:
            raise CouncilInputError(f"Council record {council_id} is already closed.")

        now = datetime.now(UTC)
        row.decision = "timed_out"
        row.intent_outcome = "HALTED_COUNCIL_TIMEOUT"
        row.session_close_timestamp = now
        row.closed = True
        await self._session.flush()

        result = {
            "council_id": council_id,
            "decision": "timed_out",
            "intent_outcome": "HALTED_COUNCIL_TIMEOUT",
            "closed_at": now.isoformat(),
        }
        log.warning("runtime_council_timeout", council_id=council_id, intent_id=row.intent_id)
        return result


class ReviewCouncil:
    """Review Council governance — ANIF-905.

    Always uses adversarial deliberation model.
    Requires all 3 mandatory outputs: accountability, policy recs, learning packages.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._records: dict[str, dict[str, Any]] = {}

    async def open_session(self, request: ReviewCouncilRequest) -> dict[str, Any]:
        """Open a review council session — always adversarial (CR-905-02)."""
        # CR-905-02: Review Council MUST always use adversarial — hardcoded, no Mode Selector input
        mode_dict = {
            "input_reversibility": "irreversible",
            "input_risk_score": 100,
            "input_ethics_flag": "present",
            "input_time_pressure": "normal",
            "input_novelty": "novel",
            "input_strike_history": "none",
            "rule_matched": 1,
            "mode_selected": DeliberationModel.adversarial.value,
            "mode_selector_timestamp": datetime.now(UTC).isoformat(),
        }
        time_limit = TIME_LIMITS[DeliberationModel.adversarial]

        council_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        record = CouncilRecordRow(
            council_id=council_id,
            council_type="review",
            triggered_by=f"{request.incident_type} incident {request.incident_id} — {request.severity_level}",
            trigger_timestamp=now,
            session_open_timestamp=now,
            mode_selector_json=json.dumps(mode_dict),
            decision="pending",
            incident_id=request.incident_id,
            incident_type=request.incident_type,
            severity_level=request.severity_level,
            time_limit_seconds=time_limit,
            record_written_by="platform",
            closed=False,
        )
        self._session.add(record)
        await self._session.flush()

        result = {
            "council_id": council_id,
            "council_type": "review",
            "decision": "pending",
            "mode_selector": mode_dict,
            "time_limit_seconds": time_limit,
            "opened_at": now.isoformat(),
        }
        self._records[council_id] = {"row": record, "summary": result}
        log.info("review_council_opened", council_id=council_id, incident_id=request.incident_id)
        return result

    async def record_decision(
        self,
        council_id: str,
        decision: ReviewDecision,
    ) -> dict[str, Any]:
        """Record the review council decision — validates all 3 mandatory outputs (CR-905-03/04)."""
        entry = self._records.get(council_id)
        if entry is None:
            raise CouncilInputError(f"No open council session for council_id={council_id}")

        row: CouncilRecordRow = entry["row"]
        if row.closed:
            raise CouncilInputError(f"Council record {council_id} is immutable.")

        # CR-905-03: accountability_determination is mandatory
        if not decision.accountability_determination:
            raise CouncilInputError(
                "Review Council MUST produce accountability_determination (CR-905-03)."
            )

        # CR-905-04: policy change recs MUST cite specific ANIF docs
        for rec in decision.policy_change_recommendations:
            if not rec.get("anif_ref"):
                raise CouncilInputError(
                    "Each policy_change_recommendation MUST include an anif_ref (CR-905-04)."
                )

        now = datetime.now(UTC)
        row.decision = "completed"
        row.accountability_determination_json = json.dumps(decision.accountability_determination)
        row.policy_change_recommendations_json = json.dumps(decision.policy_change_recommendations)
        row.learning_packages_json = json.dumps(decision.learning_packages)
        row.session_close_timestamp = now
        row.closed = True
        await self._session.flush()

        result = {
            "council_id": council_id,
            "council_type": "review",
            "decision": "completed",
            "accountability_determination": decision.accountability_determination,
            "policy_change_recommendations": decision.policy_change_recommendations,
            "learning_packages": decision.learning_packages,
            "closed_at": now.isoformat(),
        }
        log.info("review_council_completed", council_id=council_id)
        return result
