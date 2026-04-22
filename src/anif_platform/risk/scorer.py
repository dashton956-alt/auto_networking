"""
RiskScorer — deterministic risk and trust quantification — ANIF-304.

Computes risk_score, trust_score, safety_decision, and full justification
for a validated intent, its resolved policy result, and the current network state.
All calculations are fully deterministic: same inputs always produce same outputs.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

# ---------------------------------------------------------------------------
# Risk factor weights (normative — ANIF-304 §6)
# ---------------------------------------------------------------------------

_ENV_WEIGHT: dict[str, int] = {"prod": 30, "staging": 10, "dev": 0}

_PRIORITY_WEIGHT: dict[str, int] = {"critical": 10, "high": 5, "medium": 0, "low": 0}

_NETWORK_WEIGHT: dict[str, int] = {"normal": 0, "degraded": 20, "critical": 35}
_NETWORK_FALLBACK = 20  # applied when network state is unavailable

_ACTION_WEIGHT: dict[str, int] = {
    "isolate_segment": 25,
    "reroute_traffic": 15,
    "apply_qos": 5,
    "scale_bandwidth": 5,
}

# ---------------------------------------------------------------------------
# Production threshold (ANIF-304 §7.1)
# ---------------------------------------------------------------------------
_PROD_WARN_THRESHOLD = 40
_PROD_BLOCK_THRESHOLD = 70

# ---------------------------------------------------------------------------
# Non-production threshold (ANIF-304 §7.2)
# ---------------------------------------------------------------------------
_NON_PROD_WARN_THRESHOLD = 60
_NON_PROD_BLOCK_THRESHOLD = 85

# ---------------------------------------------------------------------------
# Trust penalties (ANIF-304 §5.2)
# ---------------------------------------------------------------------------
_TRUST_PENALTY_CRITICAL = -10
_TRUST_PENALTY_UNRESOLVED_CONFLICT = -15


def _safety_decision(risk_score: int, is_prod: bool) -> str:
    if is_prod:
        if risk_score >= _PROD_BLOCK_THRESHOLD:
            return "block"
        if risk_score >= _PROD_WARN_THRESHOLD:
            return "warn"
        return "allow"
    # non-production
    if risk_score >= _NON_PROD_BLOCK_THRESHOLD:
        return "block"
    if risk_score >= _NON_PROD_WARN_THRESHOLD:
        return "warn"
    return "allow"


class RiskScorer:
    """
    Computes risk and trust scores for an intent — ANIF-304.

    Thread-safe (no mutable state). Create once and call score() per request.
    """

    def score(
        self,
        intent: dict[str, Any],
        policy_result: dict[str, Any],
        network_state: dict[str, Any] | None,
        candidate_action_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Score an intent for risk and trust — ANIF-304.

        Parameters
        ----------
        intent:
            Validated intent dict (service, environment, priority, objectives, constraints).
        policy_result:
            Output of PolicyEngine.evaluate() — must contain resolved_policy_set and conflicts.
        network_state:
            Current network state dict with a 'status' key, or None if unavailable.
        candidate_action_type:
            Optional action type hinted before decision engine runs (ANIF-304 §6.5).

        Returns
        -------
        dict conforming to ANIF-304 §9 Risk Scoring Result Schema.
        """
        environment = (intent.get("environment") or "dev").lower()
        priority = (intent.get("priority") or "medium").lower()
        is_prod = environment == "prod"

        # ── RF-001: Environment Weight ──────────────────────────────────────
        env_contribution = _ENV_WEIGHT.get(environment, 0)
        rf001: dict[str, Any] = {
            "factor_id": "RF-001",
            "factor_name": "Environment Weight",
            "condition_met": env_contribution > 0,
            "contribution": env_contribution,
            "source": f"environment: {environment}",
            "note": None,
        }

        # ── RF-002: Priority Weight ─────────────────────────────────────────
        prio_contribution = _PRIORITY_WEIGHT.get(priority, 0)
        rf002: dict[str, Any] = {
            "factor_id": "RF-002",
            "factor_name": "Priority Weight",
            "condition_met": prio_contribution > 0,
            "contribution": prio_contribution,
            "source": f"priority: {priority}",
            "note": None,
        }

        # ── RF-003: Policy Denial Weight ────────────────────────────────────
        resolved_set = policy_result.get("resolved_policy_set") or policy_result.get(
            "policy_results", []
        )
        denial_count = sum(1 for r in resolved_set if r.get("decision") == "deny")
        denial_contribution = denial_count * 15
        rf003: dict[str, Any] = {
            "factor_id": "RF-003",
            "factor_name": "Policy Denial Weight",
            "condition_met": denial_count > 0,
            "contribution": denial_contribution,
            "source": f"resolved_policy_set: {denial_count} denial(s)",
            "note": None,
        }

        # ── RF-004: Policy Warning Weight ───────────────────────────────────
        warning_count = sum(1 for r in resolved_set if r.get("decision") == "warn")
        warning_contribution = warning_count * 5
        rf004: dict[str, Any] = {
            "factor_id": "RF-004",
            "factor_name": "Policy Warning Weight",
            "condition_met": warning_count > 0,
            "contribution": warning_contribution,
            "source": f"resolved_policy_set: {warning_count} warning(s)",
            "note": None,
        }

        # ── RF-005: Network State Weight ────────────────────────────────────
        if network_state is None:
            net_status = "degraded"
            net_contribution = _NETWORK_FALLBACK
            net_note = "fallback applied: network state unavailable"
            net_source = "network_state.status: fallback (state unavailable)"
        else:
            net_status = (network_state.get("status") or "normal").lower()
            net_contribution = _NETWORK_WEIGHT.get(net_status, 0)
            net_note = None
            net_source = f"network_state.status: {net_status}"

        rf005: dict[str, Any] = {
            "factor_id": "RF-005",
            "factor_name": "Network State Weight",
            "condition_met": net_contribution > 0,
            "contribution": net_contribution,
            "source": net_source,
            "note": net_note,
        }

        # ── RF-006: Action Type Risk Weight ─────────────────────────────────
        action_contribution = _ACTION_WEIGHT.get(candidate_action_type or "", 0)
        rf006: dict[str, Any] = {
            "factor_id": "RF-006",
            "factor_name": "Action Type Risk",
            "condition_met": action_contribution > 0,
            "contribution": action_contribution,
            "source": f"action_type: {candidate_action_type or 'null (pre-decision scoring)'}",
            "note": None,
        }

        # ── Risk score: sum + clamp ─────────────────────────────────────────
        raw_risk = (
            env_contribution
            + prio_contribution
            + denial_contribution
            + warning_contribution
            + net_contribution
            + action_contribution
        )
        risk_score = max(0, min(100, raw_risk))

        # ── Trust penalties ─────────────────────────────────────────────────
        trust_penalties: list[dict[str, Any]] = []

        if priority == "critical":
            trust_penalties.append(
                {"reason": "priority: critical", "penalty": _TRUST_PENALTY_CRITICAL}
            )

        conflicts = policy_result.get("conflicts", [])
        has_unresolved = any(c.get("resolution_type") == "escalated" for c in conflicts)
        if has_unresolved:
            trust_penalties.append(
                {
                    "reason": "unresolved equal-precedence policy conflict",
                    "penalty": _TRUST_PENALTY_UNRESOLVED_CONFLICT,
                }
            )

        # ── Trust score: 100 - risk + penalties, clamp ─────────────────────
        trust_base = 100 - risk_score
        total_penalty = sum(p["penalty"] for p in trust_penalties)
        trust_score = max(0, min(100, trust_base + total_penalty))

        # ── Safety decision ─────────────────────────────────────────────────
        safety_decision = _safety_decision(risk_score, is_prod)

        return {
            "scoring_id": str(uuid.uuid4()),
            "risk_score": risk_score,
            "trust_score": trust_score,
            "safety_decision": safety_decision,
            "threshold_applied": "prod" if is_prod else "non_prod",
            "justification": [rf001, rf002, rf003, rf004, rf005, rf006],
            "trust_penalties": trust_penalties,
            "scored_at": datetime.now(UTC).isoformat(),
        }
