"""Tests for PolicyEngine — ANIF-302."""

import pytest

from anif_platform.policy.engine import PolicyEngine
from anif_platform.policy.loader import PolicyLoader


def make_engine(policies_dir: str) -> PolicyEngine:
    loader = PolicyLoader(policies_dir)
    return PolicyEngine(loader)


@pytest.fixture
def engine(tmp_path) -> PolicyEngine:
    """Engine loaded with the real built-in policies."""
    import shutil
    from pathlib import Path
    src = Path(__file__).parent.parent.parent / "policies"
    dst = tmp_path / "policies"
    shutil.copytree(src, dst)
    return PolicyEngine(PolicyLoader(dst))


class TestOverallResult:
    def test_pass_when_all_policies_allow(self, engine: PolicyEngine) -> None:
        intent = {
            "service": "payments",
            "environment": "prod",
            "objectives": {"latency_ms": 50, "availability_percent": 99.5},
            "constraints": {
                "region": "EU",
                "encryption": True,
                "allowed_zones": ["eu-a", "eu-b"],
            },
            "policies": [],
            "priority": "high",
        }
        result = engine.evaluate(intent_id="test-id", resolved_intent=intent)
        assert result["overall_result"] == "pass"

    def test_fail_when_any_policy_denies(self, engine: PolicyEngine) -> None:
        intent = {
            "service": "payments",
            "environment": "prod",
            "objectives": {"latency_ms": 50},
            "constraints": {"region": "EU", "encryption": False},
            "policies": [],
            "priority": "high",
        }
        result = engine.evaluate(intent_id="test-id", resolved_intent=intent)
        assert result["overall_result"] == "fail"

    def test_evaluation_id_is_always_set(self, engine: PolicyEngine) -> None:
        intent = {
            "service": "svc",
            "constraints": {"region": "EU", "encryption": True, "allowed_zones": ["eu-a"]},
            "objectives": {"latency_ms": 50},
            "policies": [],
        }
        result = engine.evaluate(intent_id="test-id", resolved_intent=intent)
        assert result["evaluation_id"] is not None

    def test_deterministic_same_inputs_same_outputs(self, engine: PolicyEngine) -> None:
        """ANIF-302 §4: identical inputs MUST produce identical outputs."""
        intent = {
            "service": "svc",
            "constraints": {"region": "EU", "encryption": True, "allowed_zones": ["eu-a"]},
            "objectives": {"latency_ms": 50},
            "policies": [],
        }
        r1 = engine.evaluate(intent_id="test-id", resolved_intent=intent)
        r2 = engine.evaluate(intent_id="test-id", resolved_intent=intent)
        assert r1["overall_result"] == r2["overall_result"]
        assert len(r1["policy_results"]) == len(r2["policy_results"])

    def test_dry_run_flag_is_returned(self, engine: PolicyEngine) -> None:
        """ANIF-302 §10: dry_run response must include dry_run: true."""
        intent = {
            "service": "svc",
            "constraints": {"region": "EU", "encryption": True, "allowed_zones": ["eu-a"]},
            "objectives": {"latency_ms": 50},
            "policies": [],
        }
        result = engine.evaluate(intent_id="test-id", resolved_intent=intent, dry_run=True)
        assert result["dry_run"] is True

    def test_all_four_builtin_policies_always_evaluated(self, engine: PolicyEngine) -> None:
        """ANIF-302 §11.2: all 4 built-in policies active for every evaluation."""
        intent = {
            "service": "svc",
            "constraints": {"region": "EU", "encryption": True, "allowed_zones": ["eu-a"]},
            "objectives": {"latency_ms": 50},
            "policies": [],
        }
        result = engine.evaluate(intent_id="test-id", resolved_intent=intent)
        evaluated_names = {r["policy_name"] for r in result["policy_results"]}
        assert "zero_trust" in evaluated_names
        assert "no_public_ingress" in evaluated_names
        assert "pci_compliant" in evaluated_names
        assert "data_residency" in evaluated_names
