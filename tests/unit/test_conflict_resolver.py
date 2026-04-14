"""Tests for ConflictDetector and ConflictResolver — ANIF-303."""

from anif_platform.policy.conflict import ConflictResolver


class TestPrecedenceHierarchy:
    def test_compliance_beats_performance(self) -> None:
        policy_results = [
            {"policy_name": "pci_compliant", "category": "compliance", "decision": "deny",
             "triggered_rule": "constraints.encryption:equals:false", "reason": "needs encryption"},
            {"policy_name": "perf_opt", "category": "performance", "decision": "allow",
             "triggered_rule": "no rule matched", "reason": ""},
        ]
        resolver = ConflictResolver()
        conflicts, resolved = resolver.resolve(policy_results)
        assert len(conflicts) == 1
        assert conflicts[0]["winner"] == "pci_compliant"
        assert conflicts[0]["resolution_type"] == "precedence_hierarchy"

    def test_compliance_beats_security(self) -> None:
        policy_results = [
            {"policy_name": "data_residency", "category": "compliance", "decision": "deny",
             "triggered_rule": "constraints.region:not_in_list:[EU]", "reason": "region"},
            {"policy_name": "no_public_ingress", "category": "security", "decision": "allow",
             "triggered_rule": "no rule matched", "reason": ""},
        ]
        resolver = ConflictResolver()
        conflicts, _ = resolver.resolve(policy_results)
        assert conflicts[0]["winner"] == "data_residency"

    def test_equal_precedence_conflict_is_escalated(self) -> None:
        """ANIF-303 §6.2: equal-precedence conflict MUST escalate."""
        policy_results = [
            {"policy_name": "policy_a", "category": "security", "decision": "deny",
             "triggered_rule": "x:equals:y", "reason": ""},
            {"policy_name": "policy_b", "category": "security", "decision": "allow",
             "triggered_rule": "no rule matched", "reason": ""},
        ]
        resolver = ConflictResolver()
        conflicts, _ = resolver.resolve(policy_results)
        assert conflicts[0]["resolution_type"] == "escalated"
        assert conflicts[0]["winner"] is None

    def test_warn_not_upgraded_to_deny(self) -> None:
        """ANIF-303 §10.9: warn MUST NOT be upgraded to deny."""
        policy_results = [
            {"policy_name": "pol_a", "category": "compliance", "decision": "warn",
             "triggered_rule": "x:equals:y", "reason": ""},
            {"policy_name": "pol_b", "category": "performance", "decision": "allow",
             "triggered_rule": "no rule matched", "reason": ""},
        ]
        resolver = ConflictResolver()
        conflicts, resolved = resolver.resolve(policy_results)
        final_decisions = {r["policy_name"]: r["final_decision"] for r in resolved}
        assert final_decisions["pol_a"] != "deny"

    def test_no_conflict_when_decisions_agree(self) -> None:
        policy_results = [
            {"policy_name": "pol_a", "category": "compliance", "decision": "allow",
             "triggered_rule": "no rule matched", "reason": ""},
            {"policy_name": "pol_b", "category": "security", "decision": "allow",
             "triggered_rule": "no rule matched", "reason": ""},
        ]
        resolver = ConflictResolver()
        conflicts, _ = resolver.resolve(policy_results)
        assert conflicts == []

    def test_all_pairs_checked(self) -> None:
        """ANIF-303 §4.3: all n*(n-1)/2 pairs MUST be checked."""
        policy_results = [
            {"policy_name": f"pol_{i}", "category": "security",
             "decision": "deny" if i == 0 else "allow",
             "triggered_rule": "x:equals:y", "reason": ""}
            for i in range(4)
        ]
        resolver = ConflictResolver()
        conflicts, _ = resolver.resolve(policy_results)
        # pol_0 (deny) conflicts with pol_1, pol_2, pol_3 (allow) — 3 conflicts
        assert len(conflicts) == 3
