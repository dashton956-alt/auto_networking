"""Unit tests for Council services — ANIF-903, ANIF-904, ANIF-905, ANIF-907."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from anif_platform.council.schemas import (
    BuildTimeReviewRequest,
    CouncilDecision,
    ReviewCouncilRequest,
    RuntimeCouncilRequest,
)
from anif_platform.council.service import (
    BuildTimeCouncil,
    CouncilInputError,
    ReviewCouncil,
    RuntimeCouncil,
)


# ── Build-Time Council ────────────────────────────────────────────────────


def make_build_time_request(missing_input: str | None = None) -> BuildTimeReviewRequest:
    inputs = {
        "agent_manifest": {"agent_id": "agent-001", "tier": 2},
        "capability_scope": {"description": "Network observer"},
        "test_results": {"status": "pass", "signed_by": "test-lead"},
        "supply_chain_provenance": {"model_hash": "abc123"},
        "red_team_findings": {"status": "no_findings"},
        "ethics_assessment": {"status": "pass"},
        "prior_council_decisions": [],
    }
    if missing_input:
        del inputs[missing_input]
    return BuildTimeReviewRequest(
        trigger="new_agent_deployment",
        agent_id="agent-001",
        submitted_by="build-engineer",
        required_inputs=inputs,
    )


class TestBuildTimeCouncil:
    def make_service(self) -> tuple[BuildTimeCouncil, AsyncMock]:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        svc = BuildTimeCouncil(session=session)
        return svc, session

    @pytest.mark.asyncio
    async def test_valid_request_creates_pending_record(self) -> None:
        """CR-903-01/907-01: valid request creates council record in pending state."""
        svc, session = self.make_service()
        record = await svc.open_session(make_build_time_request())
        assert record["council_type"] == "build_time"
        assert record["decision"] == "pending"
        session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_missing_required_input_raises(self) -> None:
        """CR-903-02: deliberation MUST NOT begin with incomplete required inputs."""
        svc, _ = self.make_service()
        with pytest.raises(CouncilInputError, match="test_results"):
            await svc.open_session(make_build_time_request(missing_input="test_results"))

    @pytest.mark.asyncio
    async def test_blocked_decision_requires_anif_reference(self) -> None:
        """CR-903-04: blocked decision MUST cite specific ANIF requirement."""
        svc, session = self.make_service()
        record = await svc.open_session(make_build_time_request())
        council_id = record["council_id"]

        with pytest.raises(CouncilInputError, match="anif_reference"):
            await svc.record_decision(
                council_id=council_id,
                decision=CouncilDecision(
                    council_id=council_id,
                    decision="blocked",
                    decision_rationale="Failed supply chain check",
                    votes=[],
                    anif_references=[],  # empty — should raise
                ),
            )

    @pytest.mark.asyncio
    async def test_blocked_decision_with_anif_reference_succeeds(self) -> None:
        """CR-903-04: blocked decision with ANIF citation is accepted."""
        svc, session = self.make_service()
        record = await svc.open_session(make_build_time_request())
        council_id = record["council_id"]

        result = await svc.record_decision(
            council_id=council_id,
            decision=CouncilDecision(
                council_id=council_id,
                decision="blocked",
                decision_rationale="Failed supply chain check — ANIF-824 §3.2",
                votes=[],
                anif_references=["ANIF-824 §3.2"],
            ),
        )
        assert result["decision"] == "blocked"

    @pytest.mark.asyncio
    async def test_conditional_decision_requires_conditions(self) -> None:
        """CR-903-05: conditional approval MUST list each condition."""
        svc, session = self.make_service()
        record = await svc.open_session(make_build_time_request())
        council_id = record["council_id"]

        with pytest.raises(CouncilInputError, match="conditions"):
            await svc.record_decision(
                council_id=council_id,
                decision=CouncilDecision(
                    council_id=council_id,
                    decision="conditional",
                    decision_rationale="Approved subject to red-team",
                    votes=[],
                    anif_references=["ANIF-903 §6.2"],
                    conditions=[],  # empty — should raise
                ),
            )

    @pytest.mark.asyncio
    async def test_record_is_immutable_after_close(self) -> None:
        """CR-907-02: council records are immutable after session close."""
        svc, session = self.make_service()
        record = await svc.open_session(make_build_time_request())
        council_id = record["council_id"]

        await svc.record_decision(
            council_id=council_id,
            decision=CouncilDecision(
                council_id=council_id,
                decision="approved",
                decision_rationale="All inputs satisfied",
                votes=[],
                anif_references=[],
            ),
        )

        with pytest.raises(CouncilInputError, match="immutable"):
            await svc.record_decision(
                council_id=council_id,
                decision=CouncilDecision(
                    council_id=council_id,
                    decision="blocked",
                    decision_rationale="Changed mind",
                    votes=[],
                    anif_references=["ANIF-903"],
                ),
            )


# ── Runtime Council ───────────────────────────────────────────────────────


def make_runtime_request(**kwargs) -> RuntimeCouncilRequest:
    defaults = dict(
        intent_id=uuid.uuid4(),
        trigger_condition="harm_severity_score >= 80",
        harm_severity_score=85,
        risk_score=75,
        ethics_flag="absent",
        reversibility="reversible",
        novelty="precedented",
        strike_history="none",
        time_pressure="normal",
    )
    defaults.update(kwargs)
    return RuntimeCouncilRequest(**defaults)


class TestRuntimeCouncil:
    def make_service(self) -> tuple[RuntimeCouncil, AsyncMock]:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        svc = RuntimeCouncil(session=session)
        return svc, session

    @pytest.mark.asyncio
    async def test_open_session_runs_mode_selector_first(self) -> None:
        """CR-904-02: Mode Selector MUST complete before session opens."""
        svc, _ = self.make_service()
        record = await svc.open_session(make_runtime_request())
        assert record["mode_selector"] is not None
        assert record["mode_selector"]["mode_selected"] is not None

    @pytest.mark.asyncio
    async def test_open_session_records_mode_selector_before_status(self) -> None:
        """CR-902-03: mode selection record written before deliberation begins."""
        svc, _ = self.make_service()
        record = await svc.open_session(make_runtime_request())
        assert record["mode_selector"]["mode_selector_timestamp"] is not None

    @pytest.mark.asyncio
    async def test_timeout_halts_intent_not_proceeds(self) -> None:
        """CR-904-04/05: timeout MUST halt intent, never proceed."""
        svc, _ = self.make_service()
        record = await svc.open_session(make_runtime_request())
        council_id = record["council_id"]

        result = await svc.apply_timeout(council_id=council_id)
        assert result["decision"] == "timed_out"
        assert result["intent_outcome"] == "HALTED_COUNCIL_TIMEOUT"

    @pytest.mark.asyncio
    async def test_deliberation_model_matches_mode_selector(self) -> None:
        """CR-904-02: deliberation model MUST match Mode Selector output."""
        svc, _ = self.make_service()
        # ethics_flag=present → consensus → 30-min limit
        record = await svc.open_session(make_runtime_request(ethics_flag="present"))
        assert record["mode_selector"]["mode_selected"] == "consensus"
        assert record["time_limit_seconds"] == 30 * 60

    @pytest.mark.asyncio
    async def test_majority_model_has_fifteen_minute_limit(self) -> None:
        """CR-904-03: majority model → 15-min time limit."""
        svc, _ = self.make_service()
        record = await svc.open_session(make_runtime_request())
        # default inputs → majority (rule 9)
        assert record["mode_selector"]["mode_selected"] == "majority"
        assert record["time_limit_seconds"] == 15 * 60


# ── Review Council ────────────────────────────────────────────────────────


def make_review_request(**kwargs) -> ReviewCouncilRequest:
    defaults = dict(
        incident_id=str(uuid.uuid4()),
        incident_type="ethics",
        severity_level="severity_1",
        incident_closed_at=datetime.now(UTC).isoformat(),
    )
    defaults.update(kwargs)
    return ReviewCouncilRequest(**defaults)


class TestReviewCouncil:
    def make_service(self) -> tuple[ReviewCouncil, AsyncMock]:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        svc = ReviewCouncil(session=session)
        return svc, session

    @pytest.mark.asyncio
    async def test_review_council_always_uses_adversarial_model(self) -> None:
        """CR-905-02: Review Council MUST always use adversarial model."""
        svc, _ = self.make_service()
        record = await svc.open_session(make_review_request())
        assert record["mode_selector"]["mode_selected"] == "adversarial"

    @pytest.mark.asyncio
    async def test_record_decision_requires_all_three_outputs(self) -> None:
        """CR-905-03: MUST produce accountability_determination, policy_change_recommendations, learning_packages."""
        from anif_platform.council.schemas import ReviewDecision

        svc, _ = self.make_service()
        record = await svc.open_session(make_review_request())
        council_id = record["council_id"]

        with pytest.raises(CouncilInputError, match="accountability_determination"):
            await svc.record_decision(
                council_id=council_id,
                decision=ReviewDecision(
                    council_id=council_id,
                    accountability_determination=None,  # missing
                    policy_change_recommendations=[{"anif_ref": "ANIF-724", "change": "x"}],
                    learning_packages=[{"description": "negative example"}],
                ),
            )

    @pytest.mark.asyncio
    async def test_policy_recommendations_must_cite_anif_reference(self) -> None:
        """CR-905-04: policy change recs MUST cite specific ANIF docs."""
        from anif_platform.council.schemas import ReviewDecision

        svc, _ = self.make_service()
        record = await svc.open_session(make_review_request())
        council_id = record["council_id"]

        with pytest.raises(CouncilInputError, match="anif_ref"):
            await svc.record_decision(
                council_id=council_id,
                decision=ReviewDecision(
                    council_id=council_id,
                    accountability_determination={
                        "primary_layer": "pipeline",
                        "failure_type": "policy_gap",
                        "determination_rationale": "Pipeline missed ethics check",
                    },
                    policy_change_recommendations=[
                        {"change": "improve monitoring"}  # missing anif_ref
                    ],
                    learning_packages=[{"description": "negative example"}],
                ),
            )

    @pytest.mark.asyncio
    async def test_valid_review_decision_accepted(self) -> None:
        """CR-905-03/04: complete review decision is accepted."""
        from anif_platform.council.schemas import ReviewDecision

        svc, _ = self.make_service()
        record = await svc.open_session(make_review_request())
        council_id = record["council_id"]

        result = await svc.record_decision(
            council_id=council_id,
            decision=ReviewDecision(
                council_id=council_id,
                accountability_determination={
                    "primary_layer": "pipeline",
                    "failure_type": "policy_gap",
                    "determination_rationale": "ContainmentContract bypass",
                },
                policy_change_recommendations=[
                    {
                        "anif_ref": "ANIF-725 §4.3",
                        "change": "Enforce validate() at all execute() call sites",
                        "rationale": "Prevents containment bypass",
                    }
                ],
                learning_packages=[
                    {
                        "description": "Containment bypass negative example",
                        "type": "negative_example",
                    }
                ],
            ),
        )
        assert result["decision"] == "completed"
        assert result["accountability_determination"] is not None
