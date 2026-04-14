"""ConflictDetector and ConflictResolver — ANIF-303."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

# Precedence hierarchy — normative, MUST NOT be configurable (ANIF-303 §5)
_PRECEDENCE: dict[str, int] = {
    "compliance": 1,
    "security": 2,
    "availability": 3,
    "performance": 4,
}


def _decisions_conflict(d_a: str, d_b: str) -> bool:
    """Two decisions conflict if they are not equal and at least one is deny or one is warn."""
    if d_a == d_b:
        return False
    # deny vs allow or warn
    if "deny" in (d_a, d_b):
        return True
    # warn vs allow
    if set((d_a, d_b)) == {"warn", "allow"}:
        return True
    return False


class ConflictResolver:
    """
    Detects and resolves policy conflicts — ANIF-303.

    Detection is exhaustive: all n*(n-1)/2 pairs are checked.
    Resolution applies the precedence hierarchy.
    Equal-precedence conflicts are escalated.
    """

    def resolve(
        self, policy_results: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """
        Detect conflicts and produce the resolved policy set.

        Returns:
            (conflicts, resolved_policy_set)
            conflicts: list of conflict records
            resolved_policy_set: one entry per policy with final_decision
        """
        conflicts: list[dict[str, Any]] = []
        # Track overridden policies (loser in a resolved conflict)
        overridden: set[str] = set()

        n = len(policy_results)
        for i in range(n):
            for j in range(i + 1, n):
                a = policy_results[i]
                b = policy_results[j]
                if not _decisions_conflict(a["decision"], b["decision"]):
                    continue

                cat_a = a.get("category", "performance")
                cat_b = b.get("category", "performance")
                rank_a = _PRECEDENCE.get(cat_a, 99)
                rank_b = _PRECEDENCE.get(cat_b, 99)

                if rank_a == rank_b:
                    # Equal-precedence — escalate (ANIF-303 §6.2)
                    conflict: dict[str, Any] = {
                        "conflict_id": str(uuid4()),
                        "policies": [a["policy_name"], b["policy_name"]],
                        "constraint": a.get("triggered_rule", ""),
                        "decision_a": a["decision"],
                        "decision_b": b["decision"],
                        "winner": None,
                        "loser": None,
                        "resolution_rationale": (
                            f"Both policies are category '{cat_a}'; "
                            "equal-precedence conflict cannot be resolved by hierarchy"
                        ),
                        "resolution_type": "escalated",
                        "escalation_ticket_id": str(uuid4()),
                    }
                else:
                    # Higher precedence wins (lower rank number = higher precedence)
                    if rank_a < rank_b:
                        winner, loser = a, b
                    else:
                        winner, loser = b, a

                    # warn is NEVER upgraded to deny (ANIF-303 §6.3)
                    winning_decision = winner["decision"]
                    if winning_decision == "deny" and loser["decision"] == "warn":
                        winning_decision = "warn"

                    overridden.add(loser["policy_name"])
                    conflict = {
                        "conflict_id": str(uuid4()),
                        "policies": [a["policy_name"], b["policy_name"]],
                        "constraint": a.get("triggered_rule", ""),
                        "decision_a": a["decision"],
                        "decision_b": b["decision"],
                        "winner": winner["policy_name"],
                        "loser": loser["policy_name"],
                        "resolution_rationale": (
                            f"{winner['policy_name']} ({winner.get('category', '?')}, "
                            f"rank {_PRECEDENCE.get(winner.get('category', ''), 99)}) "
                            f"overrides {loser['policy_name']} "
                            f"({loser.get('category', '?')}, "
                            f"rank {_PRECEDENCE.get(loser.get('category', ''), 99)}) "
                            "per precedence hierarchy"
                        ),
                        "resolution_type": "precedence_hierarchy",
                    }

                conflicts.append(conflict)

        # Build resolved policy set — one entry per policy, excluding overridden losers
        resolved: list[dict[str, Any]] = []
        for pr in policy_results:
            name = pr["policy_name"]
            if name in overridden:
                continue
            resolved.append({"policy_name": name, "final_decision": pr["decision"]})

        return conflicts, resolved
