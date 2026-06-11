"""Unit tests for GovernanceGate — ANIF-406 §4.2."""

from __future__ import annotations

import uuid

from anif_platform.governance.gate import GovernanceGate


def make_request(
    operator_roles: list[str] | None = None,
    action_type: str = "apply_qos",
    environment: str = "prod",
    risk_score: int = 30,
    trust_score: int = 70,
    policy_results: list[dict] | None = None,
) -> dict:
    return {
        "intent_id": str(uuid.uuid4()),
        "operator_id": "jsmith@example.com",
        "operator_roles": operator_roles or ["network_engineer"],
        "action_type": action_type,
        "environment": environment,
        "risk_score": risk_score,
        "trust_score": trust_score,
        "policy_results": policy_results or [],
        "trace_id": str(uuid.uuid4()),
    }


class TestR05BlockMissingRole:
    def test_missing_network_engineer_role_blocks(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(operator_roles=["read_only"]))
        assert result["mode"] == "block"
        assert "R-05" in result["triggered_rule"]

    def test_network_engineer_role_passes_r05(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(operator_roles=["network_engineer"]))
        assert result["mode"] != "block" or "R-05" not in result["triggered_rule"]

    def test_automation_agent_role_passes_r05(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(operator_roles=["automation_agent"]))
        assert "R-05" not in result.get("triggered_rule", "")

    def test_senior_engineer_role_passes_r05(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(operator_roles=["senior_engineer"]))
        assert "R-05" not in result.get("triggered_rule", "")


class TestR06BlockSafetyDecisionBlock:
    def test_policy_result_with_block_triggers_r06(self) -> None:
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                policy_results=[{"policy_id": "p1", "outcome": "fail", "safety_decision": "block"}]
            )
        )
        assert result["mode"] == "block"
        assert "R-06" in result["triggered_rule"]

    def test_policy_result_with_warn_does_not_trigger_r06(self) -> None:
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                policy_results=[{"policy_id": "p1", "outcome": "fail", "safety_decision": "warn"}]
            )
        )
        assert "R-06" not in result.get("triggered_rule", "")

    def test_policy_result_with_null_safety_decision_does_not_trigger_r06(self) -> None:
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                policy_results=[{"policy_id": "p1", "outcome": "pass", "safety_decision": None}]
            )
        )
        assert result["mode"] != "block" or "R-06" not in result.get("triggered_rule", "R-05")


class TestBlockRulesEvaluatedFirst:
    def test_r05_block_stops_evaluation_of_manual_review_rules(self) -> None:
        """ANIF-406 §4.2.1: if block rule triggered, MUST NOT evaluate manual_review rules."""
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                operator_roles=["read_only"],
                action_type="isolate_segment",
            )
        )
        assert result["mode"] == "block"
        assert "R-01" not in result["triggered_rule"]

    def test_r06_block_stops_evaluation_of_manual_review_rules(self) -> None:
        """ANIF-406 §4.2.1: if R-06 block rule fires, MUST NOT evaluate manual_review rules."""
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                action_type="isolate_segment",
                policy_results=[{"policy_id": "p1", "outcome": "fail", "safety_decision": "block"}],
            )
        )
        assert result["mode"] == "block"
        assert "R-06" in result["triggered_rule"]
        assert "R-01" not in result["triggered_rule"]


class TestR01IsolateSegment:
    def test_isolate_segment_triggers_manual_review(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(action_type="isolate_segment"))
        assert result["mode"] == "manual_review"
        assert "R-01" in result["triggered_rule"]

    def test_apply_qos_does_not_trigger_r01(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(action_type="apply_qos"))
        assert "R-01" not in result.get("triggered_rule", "")


class TestR02RiskScore:
    def test_risk_score_70_triggers_manual_review(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(risk_score=70))
        assert result["mode"] == "manual_review"
        assert "R-02" in result["triggered_rule"]

    def test_risk_score_69_does_not_trigger_r02(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(risk_score=69))
        assert "R-02" not in result.get("triggered_rule", "")

    def test_risk_score_100_triggers_r02(self) -> None:
        gate = GovernanceGate()
        result = gate.check(**make_request(risk_score=100))
        assert "R-02" in result["triggered_rule"]


class TestR03ProdLowTrust:
    def test_prod_auto_low_trust_triggers_r03(self) -> None:
        """R-03: prod + would-be auto + trust_score < 60 → manual_review."""
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                environment="prod",
                risk_score=30,
                trust_score=59,
            )
        )
        assert result["mode"] == "manual_review"
        assert "R-03" in result["triggered_rule"]

    def test_prod_trust_60_does_not_trigger_r03(self) -> None:
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                environment="prod",
                risk_score=30,
                trust_score=60,
            )
        )
        assert "R-03" not in result.get("triggered_rule", "")

    def test_staging_low_trust_does_not_trigger_r03(self) -> None:
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                environment="staging",
                risk_score=30,
                trust_score=30,
            )
        )
        assert "R-03" not in result.get("triggered_rule", "")

    def test_r03_not_triggered_when_already_manual_review(self) -> None:
        """R-03 only applies when mode would be auto."""
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                environment="prod",
                risk_score=75,
                trust_score=40,
            )
        )
        assert result["mode"] == "manual_review"


class TestR04PolicyConflict:
    def test_conflicting_equal_precedence_policies_triggers_r04(self) -> None:
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                policy_results=[
                    {"policy_id": "p1", "outcome": "pass", "safety_decision": None},
                    {"policy_id": "p2", "outcome": "fail", "safety_decision": None},
                ]
            )
        )
        assert result["mode"] == "manual_review"
        assert "R-04" in result["triggered_rule"]

    def test_all_pass_policies_does_not_trigger_r04(self) -> None:
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                policy_results=[
                    {"policy_id": "p1", "outcome": "pass", "safety_decision": None},
                    {"policy_id": "p2", "outcome": "pass", "safety_decision": None},
                ]
            )
        )
        assert "R-04" not in result.get("triggered_rule", "")


class TestAutoMode:
    def test_auto_when_no_rules_triggered(self) -> None:
        """ANIF-406 §4.2.3: auto only when no block or manual_review rule fires."""
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                operator_roles=["network_engineer"],
                action_type="apply_qos",
                environment="dev",
                risk_score=30,
                trust_score=70,
                policy_results=[],
            )
        )
        assert result["mode"] == "auto"
        assert result["triggered_rule"] == "none"


class TestMultipleTriggeredRules:
    def test_multiple_manual_review_rules_all_listed(self) -> None:
        """ANIF-406 §4.2.2: all triggered rule IDs MUST be listed."""
        gate = GovernanceGate()
        result = gate.check(
            **make_request(
                action_type="isolate_segment",
                risk_score=80,
            )
        )
        assert result["mode"] == "manual_review"
        assert "R-01" in result["triggered_rule"]
        assert "R-02" in result["triggered_rule"]


class TestResponseFields:
    def test_response_contains_all_required_fields(self) -> None:
        gate = GovernanceGate()
        req = make_request()
        result = gate.check(**req)
        assert "mode" in result
        assert "triggered_rule" in result
        assert "rationale" in result
        assert "trace_id" in result
        assert result["trace_id"] == req["trace_id"]

    def test_trace_id_echoed_in_response(self) -> None:
        """ANIF-406 §4.1.1: trace_id from request MUST be echoed in response."""
        gate = GovernanceGate()
        trace_id = str(uuid.uuid4())
        req = make_request()
        req["trace_id"] = trace_id
        result = gate.check(**req)
        assert result["trace_id"] == trace_id
