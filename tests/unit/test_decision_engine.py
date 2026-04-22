"""Test stubs for DecisionEngine — ANIF-305.

Every MUST requirement from ANIF-305 has a corresponding test.
All tests MUST FAIL before implementation (SDD step 3).
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from anif_platform.risk.decision import DecisionEngine

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_risk_result(
    safety_decision: str = "allow",
) -> dict:
    score_map = {"allow": 30, "warn": 55, "block": 80}
    return {
        "safety_decision": safety_decision,
        "risk_score": score_map.get(safety_decision, 30),
        "trust_score": max(0, 100 - score_map.get(safety_decision, 30)),
        "scoring_id": str(uuid.uuid4()),
    }


def make_policy_result(
    has_escalated_conflict: bool = False,
    warnings: int = 0,
    denials: int = 0,
) -> dict:
    conflicts = [{"resolution_type": "escalated"}] if has_escalated_conflict else []
    policy_results = []
    for i in range(denials):
        policy_results.append({"policy_name": f"deny_{i}", "decision": "deny"})
    for i in range(warnings):
        policy_results.append({"policy_name": f"warn_{i}", "decision": "warn"})
    return {
        "overall_result": "fail" if denials else ("warn" if warnings else "pass"),
        "policy_results": policy_results,
        "conflicts": conflicts,
    }


def make_intent(
    environment: str = "prod",
    availability_percent: float | None = None,
    latency_ms: float | None = None,
) -> dict:
    objectives: dict = {}
    if availability_percent is not None:
        objectives["availability_percent"] = availability_percent
    if latency_ms is not None:
        objectives["latency_ms"] = latency_ms
    return {
        "service": "test-svc",
        "environment": environment,
        "priority": "medium",
        "objectives": objectives,
        "constraints": {"allowed_zones": ["zone-a"]},
    }


NORMAL_NETWORK: dict = {"status": "normal"}
DEGRADED_NETWORK: dict = {"status": "degraded"}


def decide(
    engine: DecisionEngine,
    intent: dict | None = None,
    risk_result: dict | None = None,
    policy_result: dict | None = None,
    network_state: dict | None = None,
) -> dict:
    """Helper to call engine.decide with sensible defaults."""
    return engine.decide(
        intent_id=str(uuid.uuid4()),
        intent=intent or make_intent(),
        risk_result=risk_result or make_risk_result("allow"),
        policy_result=policy_result or make_policy_result(),
        network_state=network_state or NORMAL_NETWORK,
    )


# ---------------------------------------------------------------------------
# Rule D-001: Block on safety_decision = block (ANIF-305 §5.1)
# ---------------------------------------------------------------------------

class TestD001BlockTerminal:
    def test_block_decision_sets_mode_block(self) -> None:
        """ANIF-305 §5.1 D-001: safety_decision=block → mode=block."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("block"))
        assert result["mode"] == "block"

    def test_block_decision_recommended_action_is_null(self) -> None:
        """ANIF-305 §5.1 D-001: mode=block → recommended_action=null."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("block"))
        assert result["recommended_action"] is None

    def test_block_decision_confidence_is_zero(self) -> None:
        """ANIF-305 §6.2: mode=block → confidence_score=0."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("block"))
        assert result["confidence_score"] == 0

    def test_block_is_terminal_d004_cannot_override(self) -> None:
        """ANIF-305 §5.2: mode=block MUST NOT be overridden by subsequent rules."""
        engine = DecisionEngine(writer=AsyncMock())
        # D-004 condition would match (availability + latency) but D-001 is terminal
        result = decide(
            engine,
            intent=make_intent(availability_percent=99.99, latency_ms=45),
            risk_result=make_risk_result("block"),
        )
        assert result["mode"] == "block"
        assert result["recommended_action"] is None

    def test_block_rollback_plan_is_null(self) -> None:
        """ANIF-305 §6 table: rollback_plan MUST be null when action is null."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("block"))
        assert result["rollback_plan"] is None


# ---------------------------------------------------------------------------
# Rule D-002: Manual review on safety_decision = warn (ANIF-305 §5.1)
# ---------------------------------------------------------------------------

class TestD002ManualReviewOnWarn:
    def test_warn_sets_manual_review(self) -> None:
        """ANIF-305 §5.1 D-002: safety_decision=warn → mode=manual_review."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("warn"))
        assert result["mode"] == "manual_review"

    def test_warn_still_selects_action(self) -> None:
        """ANIF-305 §5.1 D-002: D-002 is NOT terminal; action selection continues."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("warn"))
        # An action must still be selected (not null)
        assert result["recommended_action"] is not None


# ---------------------------------------------------------------------------
# Rule D-003: Manual review on escalated conflict (ANIF-305 §5.1)
# ---------------------------------------------------------------------------

class TestD003ManualReviewOnConflict:
    def test_escalated_conflict_sets_manual_review(self) -> None:
        """ANIF-305 §5.1 D-003: escalated conflict → mode=manual_review."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            risk_result=make_risk_result("allow"),
            policy_result=make_policy_result(has_escalated_conflict=True),
        )
        assert result["mode"] == "manual_review"

    def test_no_conflict_does_not_trigger_d003(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            risk_result=make_risk_result("allow"),
            policy_result=make_policy_result(has_escalated_conflict=False),
        )
        # Without warn, isolate, or block — should be auto
        assert result["mode"] == "auto"


# ---------------------------------------------------------------------------
# Rule D-004: High-availability + low-latency → reroute_traffic (ANIF-305 §5.1)
# ---------------------------------------------------------------------------

class TestD004HighAvailabilityLowLatency:
    def test_availability_99_99_latency_45_selects_reroute(self) -> None:
        """ANIF-305 §5.1 D-004: availability ≥ 99.99 AND latency ≤ 50 → reroute_traffic."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            intent=make_intent(availability_percent=99.99, latency_ms=45),
            risk_result=make_risk_result("allow"),
        )
        assert result["recommended_action"]["action_type"] == "reroute_traffic"

    def test_availability_exactly_99_99_latency_50_triggers_d004(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            intent=make_intent(availability_percent=99.99, latency_ms=50),
            risk_result=make_risk_result("allow"),
        )
        assert result["recommended_action"]["action_type"] == "reroute_traffic"

    def test_latency_above_50_does_not_trigger_d004(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            intent=make_intent(availability_percent=99.99, latency_ms=51),
            risk_result=make_risk_result("allow"),
        )
        # D-004 NOT triggered; D-005 (latency present) applies → apply_qos
        assert result["recommended_action"]["action_type"] == "apply_qos"

    def test_availability_below_99_99_does_not_trigger_d004(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            intent=make_intent(availability_percent=99.9, latency_ms=45),
            risk_result=make_risk_result("allow"),
        )
        # D-004 NOT triggered → D-005 (latency present) applies → apply_qos
        assert result["recommended_action"]["action_type"] == "apply_qos"


# ---------------------------------------------------------------------------
# Rule D-005: Latency-primary concern → apply_qos (ANIF-305 §5.1)
# ---------------------------------------------------------------------------

class TestD005LatencyPrimary:
    def test_latency_only_gives_apply_qos(self) -> None:
        """ANIF-305 §5.1 D-005: latency_ms present without D-004 → apply_qos."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            intent=make_intent(latency_ms=100),
            risk_result=make_risk_result("allow"),
        )
        assert result["recommended_action"]["action_type"] == "apply_qos"


# ---------------------------------------------------------------------------
# Rule D-006: Degraded network prefers reroute over scale_bandwidth (ANIF-305 §5.1)
# ---------------------------------------------------------------------------

class TestD006DegradedNetworkReroute:
    def test_degraded_with_d004_conditions_gives_reroute(self) -> None:
        """ANIF-305 §5.1 D-006: degraded network does not override reroute selection."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            intent=make_intent(availability_percent=99.99, latency_ms=45),
            risk_result=make_risk_result("allow"),
            network_state=DEGRADED_NETWORK,
        )
        assert result["recommended_action"]["action_type"] == "reroute_traffic"


# ---------------------------------------------------------------------------
# Rule D-007: isolate_segment always → manual_review (ANIF-305 §5.1)
# ---------------------------------------------------------------------------

class TestD007IsolateSegmentInChain:
    def test_d007_present_in_reasoning_chain(self) -> None:
        """ANIF-305 §8: D-007 MUST appear in the reasoning chain."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("allow"))
        rule_ids = {step["rule_id"] for step in result["reasoning_chain"]}
        assert "D-007" in rule_ids

    def test_d007_condition_not_met_when_action_is_not_isolate(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            intent=make_intent(latency_ms=100),
            risk_result=make_risk_result("allow"),
        )
        # apply_qos selected, so D-007 should not fire
        d007 = next(s for s in result["reasoning_chain"] if s["rule_id"] == "D-007")
        assert d007["condition_met"] is False


# ---------------------------------------------------------------------------
# Rule D-008: auto mode (default) (ANIF-305 §5.1)
# ---------------------------------------------------------------------------

class TestD008AutoMode:
    def test_allow_with_no_manual_triggers_gives_auto(self) -> None:
        """ANIF-305 §5.1 D-008: allow + no other mode set → auto."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            intent=make_intent(),  # no latency/availability objectives
            risk_result=make_risk_result("allow"),
            policy_result=make_policy_result(),
        )
        assert result["mode"] == "auto"


# ---------------------------------------------------------------------------
# Mode never downgraded (ANIF-305 §5.2, §10.4)
# ---------------------------------------------------------------------------

class TestModeNeverDowngraded:
    def test_manual_review_not_downgraded_to_auto(self) -> None:
        """ANIF-305 §5.2: manual_review MUST NOT be downgraded to auto."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("warn"))
        # D-002 set manual_review; D-008 must NOT override
        assert result["mode"] == "manual_review"

    def test_combined_d002_and_d003_both_manual_review(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            risk_result=make_risk_result("warn"),
            policy_result=make_policy_result(has_escalated_conflict=True),
        )
        assert result["mode"] == "manual_review"


# ---------------------------------------------------------------------------
# Bounded action constraint (ANIF-305 §4, §10.1)
# ---------------------------------------------------------------------------

PERMITTED_ACTIONS = {"reroute_traffic", "apply_qos", "scale_bandwidth", "isolate_segment"}


class TestBoundedActionConstraint:
    def test_recommended_action_within_permitted_set(self) -> None:
        """ANIF-305 §4: engine MUST ONLY select from four predefined action types."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("allow"))
        if result["recommended_action"] is not None:
            assert result["recommended_action"]["action_type"] in PERMITTED_ACTIONS

    def test_block_action_is_null_not_a_string(self) -> None:
        """ANIF-305 §4: block → recommended_action=null, not an action type string."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("block"))
        assert result["recommended_action"] is None


# ---------------------------------------------------------------------------
# Risk level assignment (ANIF-305 §6.1)
# ---------------------------------------------------------------------------

class TestRiskLevelAssignment:
    def test_reroute_traffic_risk_level_is_medium(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            intent=make_intent(availability_percent=99.99, latency_ms=45),
            risk_result=make_risk_result("allow"),
        )
        assert result["recommended_action"]["risk_level"] == "medium"

    def test_apply_qos_risk_level_is_low(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            intent=make_intent(latency_ms=100),
            risk_result=make_risk_result("allow"),
        )
        assert result["recommended_action"]["risk_level"] == "low"


# ---------------------------------------------------------------------------
# Confidence score (ANIF-305 §6.2)
# ---------------------------------------------------------------------------

class TestConfidenceScore:
    def test_block_mode_confidence_is_zero(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("block"))
        assert result["confidence_score"] == 0

    def test_apply_qos_allow_all_pass_confidence_capped_100(self) -> None:
        """apply_qos(80) + allow(+10) + all_pass(+10) = 100."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            intent=make_intent(latency_ms=100),
            risk_result=make_risk_result("allow"),
            policy_result=make_policy_result(),
            network_state=NORMAL_NETWORK,
        )
        assert result["confidence_score"] == 100

    def test_degraded_network_reduces_confidence_by_15(self) -> None:
        """ANIF-305 §6.2: degraded network → −15 confidence."""
        engine = DecisionEngine(writer=AsyncMock())
        # reroute(75) + allow(+10) + no warns(+10) + degraded(−15) = 80
        result = decide(
            engine,
            intent=make_intent(availability_percent=99.99, latency_ms=45),
            risk_result=make_risk_result("allow"),
            policy_result=make_policy_result(),
            network_state=DEGRADED_NETWORK,
        )
        assert result["confidence_score"] == 80

    def test_confidence_clamped_to_100(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("allow"))
        assert result["confidence_score"] <= 100

    def test_confidence_not_negative(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("allow"))
        assert result["confidence_score"] >= 0


# ---------------------------------------------------------------------------
# Rollback plan (ANIF-305 §7, §10.6)
# ---------------------------------------------------------------------------

class TestRollbackPlan:
    def test_non_null_action_has_rollback_plan(self) -> None:
        """ANIF-305 §7: rollback plan MUST be present for every non-null action."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("allow"))
        if result["recommended_action"] is not None:
            rp = result["rollback_plan"]
            assert rp is not None

    def test_rollback_plan_has_required_fields(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(
            engine,
            intent=make_intent(latency_ms=100),
            risk_result=make_risk_result("allow"),
        )
        rp = result["rollback_plan"]
        assert rp is not None
        assert "action_type" in rp
        assert "description" in rp
        assert "estimated_duration_ms" in rp
        assert "preconditions" in rp
        assert isinstance(rp["preconditions"], list)

    def test_null_action_rollback_plan_is_null(self) -> None:
        """ANIF-305 §10.6: rollback_plan MUST be null when action is null."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("block"))
        assert result["rollback_plan"] is None


# ---------------------------------------------------------------------------
# Reasoning chain (ANIF-305 §8, §10.7)
# ---------------------------------------------------------------------------

class TestReasoningChain:
    def test_all_eight_rules_appear_in_chain(self) -> None:
        """ANIF-305 §10.7: reasoning chain MUST contain one entry per rule."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("allow"))
        rule_ids = {step["rule_id"] for step in result["reasoning_chain"]}
        assert rule_ids == {"D-001", "D-002", "D-003", "D-004", "D-005", "D-006", "D-007", "D-008"}

    def test_chain_contains_eight_entries(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("allow"))
        assert len(result["reasoning_chain"]) == 8

    def test_chain_ordered_by_rule_id(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("allow"))
        ids = [step["rule_id"] for step in result["reasoning_chain"]]
        assert ids == sorted(ids)

    def test_each_step_has_required_fields(self) -> None:
        """ANIF-305 §8: each step MUST have step, rule_id, condition_evaluated, condition_met, outcome, rationale."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("allow"))
        for step in result["reasoning_chain"]:
            assert "step" in step
            assert "rule_id" in step
            assert "condition_evaluated" in step
            assert isinstance(step["condition_met"], bool)
            assert "outcome" in step
            assert "rationale" in step

    def test_block_chain_has_only_d001_condition_met(self) -> None:
        """ANIF-305 §5.2: block is terminal; chain MUST reflect D-001 fired."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("block"))
        d001 = next(s for s in result["reasoning_chain"] if s["rule_id"] == "D-001")
        assert d001["condition_met"] is True


# ---------------------------------------------------------------------------
# decision_id (ANIF-305 §10.10)
# ---------------------------------------------------------------------------

class TestDecisionId:
    def test_decision_id_is_uuid_v4(self) -> None:
        """ANIF-305 §10.10: decision_id MUST be UUID v4."""
        engine = DecisionEngine(writer=AsyncMock())
        result = decide(engine, risk_result=make_risk_result("allow"))
        parsed = uuid.UUID(result["decision_id"])
        assert parsed.version == 4

    def test_each_call_gets_unique_decision_id(self) -> None:
        engine = DecisionEngine(writer=AsyncMock())
        r1 = decide(engine, risk_result=make_risk_result("allow"))
        r2 = decide(engine, risk_result=make_risk_result("allow"))
        assert r1["decision_id"] != r2["decision_id"]


# ---------------------------------------------------------------------------
# Determinism (ANIF-305 §10.9)
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_identical_inputs_produce_identical_decisions(self) -> None:
        """ANIF-305 §10.9: engine MUST be deterministic."""
        engine = DecisionEngine(writer=AsyncMock())
        intent = make_intent(availability_percent=99.99, latency_ms=45)
        risk = make_risk_result("allow")
        policy = make_policy_result()
        # Use fixed intent_id so it's truly identical
        intent_id = str(uuid.uuid4())
        r1 = engine.decide(intent_id, intent, risk, policy, NORMAL_NETWORK)
        r2 = engine.decide(intent_id, intent, risk, policy, NORMAL_NETWORK)
        assert r1["mode"] == r2["mode"]
        assert r1["recommended_action"] == r2["recommended_action"]
        assert r1["confidence_score"] == r2["confidence_score"]
