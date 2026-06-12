"""
GovernanceGate — pure rule engine evaluating R-01 through R-06 — ANIF-406 §4.2.

Deterministic computation: no I/O, no mutable state. Thread-safe.
Rules R-05 and R-06 (block) are evaluated first and are terminal.
Rules R-01 through R-04 (manual_review) are evaluated only if no block rule fires.
"""

from __future__ import annotations

from typing import Any

# Roles that satisfy the submission requirement (R-05) — ANIF-406 §4.2.1
_PERMITTED_SUBMITTER_ROLES = frozenset({"network_engineer", "automation_agent", "senior_engineer"})


class GovernanceGate:
    """
    Evaluates governance rules R-01–R-06 and returns a mode decision — ANIF-406.

    Pure computation: inject no dependencies. Call check() for each request.
    """

    def check(
        self,
        intent_id: str,
        operator_id: str,
        operator_roles: list[str],
        action_type: str,
        environment: str,
        risk_score: int,
        trust_score: int,
        policy_results: list[dict[str, Any]],
        trace_id: str,
    ) -> dict[str, Any]:
        """
        Evaluate governance rules and return a mode decision.

        Block rules (R-05, R-06) are evaluated first and are terminal.
        Manual review rules (R-01–R-04) are evaluated only if no block rule fires.
        Returns dict with keys: mode, triggered_rule, rationale, trace_id.
        """
        roles_set = set(operator_roles)
        triggered: list[str] = []

        # ── Block rules (evaluated first, terminal) ──────────────────────────
        # R-05: caller must have a permitted role
        if not roles_set.intersection(_PERMITTED_SUBMITTER_ROLES):
            rationale = (
                f"Governance mode set to block because the caller ({operator_id}) does not hold "
                f"a permitted submitter role (network_engineer, automation_agent, or senior_engineer). "
                f"The caller's roles are: {', '.join(operator_roles) or 'none'}. "
                f"This action cannot proceed."
            )
            return self._result("block", ["R-05"], rationale, trace_id)

        # R-06: any policy result has safety_decision = block
        blocking_policies = [r for r in policy_results if r.get("safety_decision") == "block"]
        if blocking_policies:
            names = ", ".join(r.get("policy_id", "?") for r in blocking_policies)
            rationale = (
                f"Governance mode set to block because one or more policy results "
                f"have safety_decision=block: [{names}]. "
                f"This action cannot proceed regardless of risk score."
            )
            return self._result("block", ["R-06"], rationale, trace_id)

        # ── Manual review rules (evaluated if no block rule fired) ────────────
        # R-01: action_type = isolate_segment
        if action_type == "isolate_segment":
            triggered.append("R-01")

        # R-02: risk_score >= 70
        if risk_score >= 70:
            triggered.append("R-02")

        # R-03: prod + would-be auto + trust_score < 60
        # "would-be auto" means R-01 and R-02 have not triggered yet
        would_be_auto = len(triggered) == 0
        if environment == "prod" and would_be_auto and trust_score < 60:
            triggered.append("R-03")

        # R-04: conflicting policy outcomes (pass vs fail present simultaneously)
        outcomes = {r.get("outcome") for r in policy_results}
        if "pass" in outcomes and "fail" in outcomes:
            triggered.append("R-04")

        if triggered:
            rationale = self._manual_review_rationale(
                triggered, risk_score, trust_score, environment, action_type
            )
            return self._result("manual_review", triggered, rationale, trace_id)

        # ── Auto (no rules triggered) ─────────────────────────────────────────
        return self._result(
            "auto",
            [],
            "All governance rules evaluated; no block or manual_review condition was met. "
            "Action may proceed autonomously.",
            trace_id,
        )

    @staticmethod
    def _manual_review_rationale(
        triggered: list[str],
        risk_score: int,
        trust_score: int,
        environment: str,
        action_type: str,
    ) -> str:
        parts: list[str] = []
        if "R-01" in triggered:
            parts.append(f"R-01: action_type={action_type} requires human review")
        if "R-02" in triggered:
            parts.append(f"R-02: risk_score ({risk_score}) >= 70")
        if "R-03" in triggered:
            parts.append(f"R-03: prod environment with trust_score ({trust_score}) < 60")
        if "R-04" in triggered:
            parts.append("R-04: conflicting policy outcomes require adjudication")
        return (
            f"Governance mode set to manual_review. "
            f"Triggered: {'; '.join(parts)}. "
            f"An approval ticket has been created. A senior_engineer must approve within 15 minutes."
        )

    @staticmethod
    def _result(
        mode: str,
        triggered_rules: list[str],
        rationale: str,
        trace_id: str,
    ) -> dict[str, Any]:
        return {
            "mode": mode,
            "triggered_rule": ", ".join(triggered_rules) if triggered_rules else "none",
            "rationale": rationale,
            "trace_id": trace_id,
        }
