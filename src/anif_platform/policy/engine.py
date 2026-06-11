"""PolicyEngine — 100% deterministic policy evaluation — ANIF-302."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from anif_platform.policy.condition import ConditionEvaluator
from anif_platform.policy.conflict import ConflictResolver
from anif_platform.policy.loader import PolicyLoader

# Built-in policies that MUST always be active (ANIF-302 §11.2)
_BUILTIN_POLICY_NAMES = {"zero_trust", "no_public_ingress", "pci_compliant", "data_residency"}


class PolicyEngine:
    """
    Evaluates all active policies against an intent — ANIF-302.

    Evaluation is 100% deterministic: same inputs always produce same outputs.
    All four built-in policies are always included.
    Custom policies load from the policies/ directory.
    """

    def __init__(self, loader: PolicyLoader) -> None:
        self._policies = loader.load_all()
        self._resolver = ConflictResolver()

    def evaluate(
        self,
        intent_id: str,
        resolved_intent: dict[str, Any],
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """
        Evaluate all active policies against a resolved intent.

        Returns the full evaluation result conforming to ANIF-302 §9.
        dry_run=True: no audit records written, evaluation_id is ephemeral.
        """
        # Active policy set = all loaded policies (built-ins + custom)
        policy_results: list[dict[str, Any]] = []

        for name, policy in sorted(self._policies.items()):
            result = self._evaluate_single(name, policy, resolved_intent)
            policy_results.append(result)

        # Additional zero_trust logic — ANIF-302 §7.1
        if "zero_trust" in self._policies:
            zt_result = self._evaluate_zero_trust_extra(resolved_intent, policy_results)
            if zt_result is not None:
                # Replace the existing zero_trust result
                policy_results = [
                    zt_result if r["policy_name"] == "zero_trust" else r for r in policy_results
                ]

        # Additional no_public_ingress logic — ANIF-302 §7.2
        if "no_public_ingress" in self._policies:
            npi_result = self._evaluate_no_public_ingress_extra(resolved_intent, policy_results)
            if npi_result is not None:
                policy_results = [
                    npi_result if r["policy_name"] == "no_public_ingress" else r
                    for r in policy_results
                ]

        # Conflict detection and resolution — ANIF-303
        conflicts, resolved_set = self._resolver.resolve(policy_results)

        # Determine overall_result
        decisions = [r["decision"] for r in policy_results]
        if "deny" in decisions:
            overall_result = "fail"
        elif "warn" in decisions:
            overall_result = "warn"
        else:
            overall_result = "pass"

        return {
            "intent_id": intent_id,
            "evaluation_id": str(uuid4()),
            "overall_result": overall_result,
            "policy_results": policy_results,
            "conflicts": conflicts,
            "resolved_policy_set": resolved_set,
            "evaluated_at": datetime.now(UTC).isoformat(),
            "dry_run": dry_run,
        }

    def _evaluate_single(
        self, name: str, policy: dict[str, Any], intent: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate one policy: first matching rule wins; no match = allow."""
        category = policy.get("category", "performance")
        for rule in policy.get("rules", []):
            condition = rule.get("condition", "")
            action = rule.get("action", "allow")
            reason = rule.get("reason", "")
            try:
                if ConditionEvaluator.evaluate(condition, intent):
                    return {
                        "policy_name": name,
                        "category": category,
                        "decision": action,
                        "triggered_rule": condition,
                        "reason": reason,
                    }
            except Exception:
                # Malformed condition treated as non-matching (safe default)
                continue

        return {
            "policy_name": name,
            "category": category,
            "decision": "allow",
            "triggered_rule": "no rule matched",
            "reason": f"All rules evaluated; no condition matched for {name}",
        }

    @staticmethod
    def _evaluate_zero_trust_extra(
        intent: dict[str, Any], current_results: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """
        Additional zero_trust logic not expressible in grammar v0.1 — ANIF-302 §7.1.
        If allowed_zones is absent, produce deny.
        """
        constraints = intent.get("constraints") or {}
        if "allowed_zones" not in constraints:
            return {
                "policy_name": "zero_trust",
                "category": "security",
                "decision": "deny",
                "triggered_rule": "constraints.allowed_zones:absent",
                "reason": "zero_trust: allowed_zones must be explicitly declared",
            }
        return None

    @staticmethod
    def _evaluate_no_public_ingress_extra(
        intent: dict[str, Any], current_results: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """
        Additional no_public_ingress logic — ANIF-302 §7.2.
        If allowed_zones is entirely absent, produce deny.
        """
        constraints = intent.get("constraints") or {}
        if "allowed_zones" not in constraints:
            return {
                "policy_name": "no_public_ingress",
                "category": "security",
                "decision": "deny",
                "triggered_rule": "constraints.allowed_zones:absent",
                "reason": "Public ingress is prohibited; at least one allowed zone must be specified",
            }
        return None
