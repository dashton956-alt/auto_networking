"""Test stubs for RiskScorer — ANIF-304.

Every MUST requirement from ANIF-304 has a corresponding test.
All tests MUST FAIL before implementation (SDD step 3).
"""

from __future__ import annotations

import uuid

from anif_platform.risk.scorer import RiskScorer

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_intent(
    environment: str = "dev",
    priority: str = "medium",
    latency_ms: float | None = None,
    availability_percent: float | None = None,
) -> dict:
    objectives: dict = {}
    if latency_ms is not None:
        objectives["latency_ms"] = latency_ms
    if availability_percent is not None:
        objectives["availability_percent"] = availability_percent
    return {
        "service": "test-svc",
        "environment": environment,
        "priority": priority,
        "objectives": objectives,
        "constraints": {"allowed_zones": ["zone-a"]},
    }


def make_policy_result(
    denials: int = 0,
    warnings: int = 0,
    has_escalated_conflict: bool = False,
) -> dict:
    policy_results = []
    for i in range(denials):
        policy_results.append({"policy_name": f"deny_policy_{i}", "decision": "deny"})
    for i in range(warnings):
        policy_results.append({"policy_name": f"warn_policy_{i}", "decision": "warn"})
    for i in range(max(0, 4 - denials - warnings)):
        policy_results.append({"policy_name": f"pass_policy_{i}", "decision": "allow"})
    conflicts = [{"resolution_type": "escalated"}] if has_escalated_conflict else []
    return {
        "overall_result": "fail" if denials else ("warn" if warnings else "pass"),
        "policy_results": policy_results,
        "conflicts": conflicts,
        "resolved_policy_set": policy_results,
    }


NORMAL_NETWORK = {"status": "normal"}
DEGRADED_NETWORK = {"status": "degraded"}
CRITICAL_NETWORK = {"status": "critical"}


# ---------------------------------------------------------------------------
# RF-001: Environment Weight (ANIF-304 §6.1)
# ---------------------------------------------------------------------------


class TestRF001EnvironmentWeight:
    def test_prod_adds_30(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent("prod"), make_policy_result(), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-001")
        assert entry["contribution"] == 30

    def test_staging_adds_10(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent("staging"), make_policy_result(), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-001")
        assert entry["contribution"] == 10

    def test_dev_adds_0(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent("dev"), make_policy_result(), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-001")
        assert entry["contribution"] == 0

    def test_dev_entry_still_in_justification(self) -> None:
        """Non-applicable factors MUST appear in justification with 0 contribution — ANIF-304 §11.3."""
        scorer = RiskScorer()
        result = scorer.score(make_intent("dev"), make_policy_result(), NORMAL_NETWORK)
        entry = next((e for e in result["justification"] if e["factor_id"] == "RF-001"), None)
        assert entry is not None
        assert entry["condition_met"] is False


# ---------------------------------------------------------------------------
# RF-002: Priority Weight (ANIF-304 §6.2)
# ---------------------------------------------------------------------------


class TestRF002PriorityWeight:
    def test_critical_adds_10(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent("dev", "critical"), make_policy_result(), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-002")
        assert entry["contribution"] == 10

    def test_high_adds_5(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent("dev", "high"), make_policy_result(), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-002")
        assert entry["contribution"] == 5

    def test_medium_adds_0(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent("dev", "medium"), make_policy_result(), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-002")
        assert entry["contribution"] == 0

    def test_low_adds_0(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent("dev", "low"), make_policy_result(), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-002")
        assert entry["contribution"] == 0


# ---------------------------------------------------------------------------
# RF-003 / RF-004: Policy Failure Weight (ANIF-304 §6.3)
# ---------------------------------------------------------------------------


class TestRF003RF004PolicyWeight:
    def test_two_denials_add_30(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(denials=2), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-003")
        assert entry["contribution"] == 30  # 2 × 15

    def test_one_warning_adds_5(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(warnings=1), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-004")
        assert entry["contribution"] == 5

    def test_no_denials_rf003_contributes_0_but_appears(self) -> None:
        """ANIF-304 §11.3: non-applicable factors MUST appear with 0 contribution."""
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(denials=0), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-003")
        assert entry["contribution"] == 0
        assert entry["condition_met"] is False

    def test_no_warnings_rf004_contributes_0_but_appears(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(warnings=0), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-004")
        assert entry["contribution"] == 0
        assert entry["condition_met"] is False

    def test_two_warnings_add_10(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(warnings=2), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-004")
        assert entry["contribution"] == 10  # 2 × 5


# ---------------------------------------------------------------------------
# RF-005: Network State Weight (ANIF-304 §6.4)
# ---------------------------------------------------------------------------


class TestRF005NetworkStateWeight:
    def test_degraded_adds_20(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(), DEGRADED_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-005")
        assert entry["contribution"] == 20

    def test_critical_adds_35(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(), CRITICAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-005")
        assert entry["contribution"] == 35

    def test_normal_adds_0(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-005")
        assert entry["contribution"] == 0

    def test_none_network_state_applies_fallback_20(self) -> None:
        """ANIF-304 §6.4: unavailable network state MUST apply +20 (degraded fallback)."""
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(), None)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-005")
        assert entry["contribution"] == 20

    def test_none_network_state_records_fallback_in_justification(self) -> None:
        """ANIF-304 §6.4: fallback MUST be noted in the justification entry."""
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(), None)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-005")
        note_or_source = (entry.get("note") or "") + (entry.get("source") or "")
        assert "fallback" in note_or_source.lower()


# ---------------------------------------------------------------------------
# RF-006: Action Type Risk Weight (ANIF-304 §6.5)
# ---------------------------------------------------------------------------


class TestRF006ActionTypeWeight:
    def test_isolate_segment_adds_25(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(
            make_intent(),
            make_policy_result(),
            NORMAL_NETWORK,
            candidate_action_type="isolate_segment",
        )
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-006")
        assert entry["contribution"] == 25

    def test_reroute_traffic_adds_15(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(
            make_intent(),
            make_policy_result(),
            NORMAL_NETWORK,
            candidate_action_type="reroute_traffic",
        )
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-006")
        assert entry["contribution"] == 15

    def test_apply_qos_adds_5(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(
            make_intent(),
            make_policy_result(),
            NORMAL_NETWORK,
            candidate_action_type="apply_qos",
        )
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-006")
        assert entry["contribution"] == 5

    def test_scale_bandwidth_adds_5(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(
            make_intent(),
            make_policy_result(),
            NORMAL_NETWORK,
            candidate_action_type="scale_bandwidth",
        )
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-006")
        assert entry["contribution"] == 5

    def test_no_action_adds_0_and_appears_in_justification(self) -> None:
        """ANIF-304 §11.3: RF-006 with no action MUST appear with 0 contribution."""
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(), NORMAL_NETWORK)
        entry = next(e for e in result["justification"] if e["factor_id"] == "RF-006")
        assert entry["contribution"] == 0
        assert entry["condition_met"] is False


# ---------------------------------------------------------------------------
# Risk score clamping (ANIF-304 §5.1, §11.1)
# ---------------------------------------------------------------------------


class TestRiskScoreClamping:
    def test_risk_score_clamped_to_100(self) -> None:
        """ANIF-304 §5.1: sum exceeding 100 MUST be recorded as 100."""
        scorer = RiskScorer()
        # prod(30) + critical(10) + 2 denials(30) + degraded(20) + isolate(25) = 115 → 100
        result = scorer.score(
            make_intent("prod", "critical"),
            make_policy_result(denials=2),
            DEGRADED_NETWORK,
            candidate_action_type="isolate_segment",
        )
        assert result["risk_score"] == 100

    def test_risk_score_not_negative(self) -> None:
        """ANIF-304 §5.1: risk score MUST NOT be negative."""
        scorer = RiskScorer()
        result = scorer.score(make_intent("dev"), make_policy_result(), NORMAL_NETWORK)
        assert result["risk_score"] >= 0


# ---------------------------------------------------------------------------
# Trust score (ANIF-304 §5.2, §11.4)
# ---------------------------------------------------------------------------


class TestTrustScore:
    def test_base_trust_is_100_minus_risk_with_no_penalties(self) -> None:
        """ANIF-304 §5.2: base trust = 100 − risk_score."""
        scorer = RiskScorer()
        # dev + medium + no issues + apply_qos(5) → risk=5
        result = scorer.score(
            make_intent("dev", "medium"),
            make_policy_result(),
            NORMAL_NETWORK,
            candidate_action_type="apply_qos",
        )
        assert result["trust_score"] == 100 - result["risk_score"]

    def test_critical_priority_applies_minus_10_trust_penalty(self) -> None:
        """ANIF-304 §5.2: priority=critical applies −10 trust penalty."""
        scorer = RiskScorer()
        result = scorer.score(
            make_intent("dev", "critical"),
            make_policy_result(),
            NORMAL_NETWORK,
        )
        expected = max(0, 100 - result["risk_score"] - 10)
        assert result["trust_score"] == expected
        penalties = result["trust_penalties"]
        assert any(p["penalty"] == -10 for p in penalties)

    def test_trust_score_not_negative(self) -> None:
        """ANIF-304 §5.2: trust score MUST NOT be negative."""
        scorer = RiskScorer()
        result = scorer.score(
            make_intent("prod", "critical"),
            make_policy_result(denials=2),
            DEGRADED_NETWORK,
            candidate_action_type="isolate_segment",
        )
        assert result["trust_score"] >= 0

    def test_trust_score_clamped_to_100(self) -> None:
        """ANIF-304 §5.2: trust score MUST be clamped to [0, 100]."""
        scorer = RiskScorer()
        result = scorer.score(make_intent("dev", "medium"), make_policy_result(), NORMAL_NETWORK)
        assert result["trust_score"] <= 100


# ---------------------------------------------------------------------------
# Threshold selection (ANIF-304 §7, §11.5, §11.6)
# ---------------------------------------------------------------------------


class TestThresholdSelection:
    def test_prod_uses_prod_threshold_set(self) -> None:
        """ANIF-304 §7.3: prod environment MUST use production threshold."""
        scorer = RiskScorer()
        result = scorer.score(make_intent("prod"), make_policy_result(), NORMAL_NETWORK)
        assert result["threshold_applied"] == "prod"

    def test_staging_uses_non_prod_threshold_set(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent("staging"), make_policy_result(), NORMAL_NETWORK)
        assert result["threshold_applied"] == "non_prod"

    def test_dev_uses_non_prod_threshold_set(self) -> None:
        scorer = RiskScorer()
        result = scorer.score(make_intent("dev"), make_policy_result(), NORMAL_NETWORK)
        assert result["threshold_applied"] == "non_prod"

    def test_threshold_applied_always_present(self) -> None:
        """ANIF-304 §11.6: threshold_applied MUST be recorded in every result."""
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(), NORMAL_NETWORK)
        assert "threshold_applied" in result


# ---------------------------------------------------------------------------
# Safety decision correctness (ANIF-304 §7.1, §7.2)
# ---------------------------------------------------------------------------


class TestSafetyDecision:
    def test_prod_allow_below_40(self) -> None:
        """ANIF-304 §7.1: prod risk < 40 → allow."""
        scorer = RiskScorer()
        # dev + medium + no issues = 0
        result = scorer.score(make_intent("dev"), make_policy_result(), NORMAL_NETWORK)
        assert result["safety_decision"] == "allow"

    def test_prod_warn_between_40_and_69(self) -> None:
        """ANIF-304 §7.1: prod 40 ≤ risk < 70 → warn."""
        scorer = RiskScorer()
        # prod(30) + reroute(15) = 45 → warn (prod threshold)
        result = scorer.score(
            make_intent("prod"),
            make_policy_result(),
            NORMAL_NETWORK,
            candidate_action_type="reroute_traffic",
        )
        assert result["risk_score"] == 45
        assert result["safety_decision"] == "warn"

    def test_prod_block_at_70(self) -> None:
        """ANIF-304 §7.1: prod risk ≥ 70 → block."""
        scorer = RiskScorer()
        # prod(30) + isolate(25) + 1 denial(15) = 70 → block
        result = scorer.score(
            make_intent("prod"),
            make_policy_result(denials=1),
            NORMAL_NETWORK,
            candidate_action_type="isolate_segment",
        )
        assert result["risk_score"] == 70
        assert result["safety_decision"] == "block"

    def test_non_prod_allow_below_60(self) -> None:
        """ANIF-304 §7.2: non-prod risk < 60 → allow."""
        scorer = RiskScorer()
        # staging(10) + isolate(25) + 1 denial(15) = 50 → allow (non_prod: <60)
        result = scorer.score(
            make_intent("staging"),
            make_policy_result(denials=1),
            NORMAL_NETWORK,
            candidate_action_type="isolate_segment",
        )
        assert result["risk_score"] == 50
        assert result["safety_decision"] == "allow"

    def test_non_prod_warn_between_60_and_84(self) -> None:
        """ANIF-304 §7.2: non-prod 60 ≤ risk < 85 → warn."""
        scorer = RiskScorer()
        # dev(0) + degraded(20) + 2 denials(30) + isolate(25) = 75 → warn (non_prod)
        result = scorer.score(
            make_intent("dev"),
            make_policy_result(denials=2),
            DEGRADED_NETWORK,
            candidate_action_type="isolate_segment",
        )
        assert result["risk_score"] == 75
        assert result["safety_decision"] == "warn"

    def test_non_prod_block_at_85(self) -> None:
        """ANIF-304 §7.2: non-prod risk ≥ 85 → block."""
        scorer = RiskScorer()
        # staging(10) + critical(10) + degraded(20) + 2 denials(30) + isolate(25) = 95 → block
        result = scorer.score(
            make_intent("staging", "critical"),
            make_policy_result(denials=2),
            DEGRADED_NETWORK,
            candidate_action_type="isolate_segment",
        )
        assert result["risk_score"] == 95
        assert result["safety_decision"] == "block"


# ---------------------------------------------------------------------------
# Justification format (ANIF-304 §8, §11.7)
# ---------------------------------------------------------------------------


class TestJustificationFormat:
    def test_all_six_factors_present(self) -> None:
        """ANIF-304 §11.2: all six factors MUST be evaluated for every intent."""
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(), NORMAL_NETWORK)
        factor_ids = {e["factor_id"] for e in result["justification"]}
        assert factor_ids == {"RF-001", "RF-002", "RF-003", "RF-004", "RF-005", "RF-006"}

    def test_justification_ordered_by_factor_id(self) -> None:
        """ANIF-304 §8: justification MUST be ordered by Factor ID."""
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(), NORMAL_NETWORK)
        ids = [e["factor_id"] for e in result["justification"]]
        assert ids == sorted(ids)

    def test_each_entry_has_all_required_fields(self) -> None:
        """ANIF-304 §8: each entry MUST have factor_id, factor_name, condition_met, contribution, source."""
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(), NORMAL_NETWORK)
        for entry in result["justification"]:
            assert "factor_id" in entry
            assert "factor_name" in entry
            assert isinstance(entry["condition_met"], bool)
            assert isinstance(entry["contribution"], int)
            assert "source" in entry


# ---------------------------------------------------------------------------
# Determinism (ANIF-304 §4, §11.8)
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_inputs_same_scores(self) -> None:
        """ANIF-304 §4: given identical inputs, engine MUST always produce identical outputs."""
        scorer = RiskScorer()
        intent = make_intent("prod", "high")
        policy_result = make_policy_result(warnings=1)
        r1 = scorer.score(intent, policy_result, DEGRADED_NETWORK)
        r2 = scorer.score(intent, policy_result, DEGRADED_NETWORK)
        assert r1["risk_score"] == r2["risk_score"]
        assert r1["trust_score"] == r2["trust_score"]
        assert r1["safety_decision"] == r2["safety_decision"]
        assert r1["threshold_applied"] == r2["threshold_applied"]


# ---------------------------------------------------------------------------
# scoring_id (ANIF-304 §9, §11.9)
# ---------------------------------------------------------------------------


class TestScoringId:
    def test_scoring_id_is_valid_uuid(self) -> None:
        """ANIF-304 §11.9: scoring result MUST be assigned a unique scoring_id (UUID v4)."""
        scorer = RiskScorer()
        result = scorer.score(make_intent(), make_policy_result(), NORMAL_NETWORK)
        parsed = uuid.UUID(result["scoring_id"])
        assert parsed.version == 4

    def test_each_call_gets_unique_scoring_id(self) -> None:
        scorer = RiskScorer()
        r1 = scorer.score(make_intent(), make_policy_result(), NORMAL_NETWORK)
        r2 = scorer.score(make_intent(), make_policy_result(), NORMAL_NETWORK)
        assert r1["scoring_id"] != r2["scoring_id"]


# ---------------------------------------------------------------------------
# Worked example (ANIF-304 §10)
# ---------------------------------------------------------------------------


class TestWorkedExample:
    def test_anif_304_section_10(self) -> None:
        """ANIF-304 §10: payments-gateway, prod, critical, 1 warning, degraded, reroute."""
        scorer = RiskScorer()
        intent = {
            "service": "payments-gateway",
            "environment": "prod",
            "priority": "critical",
            "objectives": {"latency_ms": 50},
            "constraints": {"allowed_zones": ["zone-a"]},
        }
        policy_result = make_policy_result(warnings=1)
        network = {"status": "degraded"}
        result = scorer.score(
            intent, policy_result, network, candidate_action_type="reroute_traffic"
        )
        # 30 + 10 + 0 + 5 + 20 + 15 = 80
        assert result["risk_score"] == 80
        # trust: 100 - 80 = 20, penalty -10 (critical) → 10
        assert result["trust_score"] == 10
        # prod threshold: ≥70 → block
        assert result["safety_decision"] == "block"
