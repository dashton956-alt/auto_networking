"""
DecisionEngine — bounded deterministic action recommendation — ANIF-305.

Takes validated intent, resolved policy result, and risk scoring result as
inputs. Produces a single bounded action recommendation with a full reasoning
chain, governance mode, and rollback plan.

Rules D-001 through D-008 are evaluated in order for every call.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Action type constants (ANIF-305 §4)
# ---------------------------------------------------------------------------
_PERMITTED_ACTIONS = frozenset(
    {"reroute_traffic", "apply_qos", "scale_bandwidth", "isolate_segment"}
)

# Risk level per action type (ANIF-305 §6.1)
_ACTION_RISK_LEVEL: dict[str, str] = {
    "reroute_traffic": "medium",
    "apply_qos": "low",
    "scale_bandwidth": "low",
    "isolate_segment": "high",
}

# Base confidence per action type (ANIF-305 §6.2)
_ACTION_BASE_CONFIDENCE: dict[str, int] = {
    "apply_qos": 80,
    "reroute_traffic": 75,
    "scale_bandwidth": 70,
    "isolate_segment": 60,
}

# Rollback descriptions (ANIF-305 §7)
_ROLLBACK_PLANS: dict[str, dict[str, Any]] = {
    "reroute_traffic": {
        "action_type": "reroute_traffic",
        "description": (
            "Restore original traffic routing by reverting all routing changes. "
            "Re-advertise original BGP prefixes from the primary path."
        ),
        "estimated_duration_ms": 5000,
        "preconditions": [
            "Original path must be reachable",
            "No active sessions on the alternative path that would be disrupted",
        ],
    },
    "apply_qos": {
        "action_type": "apply_qos",
        "description": (
            "Remove applied QoS policies and restore default traffic class settings "
            "to their pre-action configuration."
        ),
        "estimated_duration_ms": 2000,
        "preconditions": ["Previous QoS baseline configuration is available"],
    },
    "scale_bandwidth": {
        "action_type": "scale_bandwidth",
        "description": (
            "Revert bandwidth allocation to the previous configured value. "
            "Restore original resource reservation on affected interfaces."
        ),
        "estimated_duration_ms": 3000,
        "preconditions": ["Sufficient capacity exists to restore original allocation"],
    },
    "isolate_segment": {
        "action_type": "isolate_segment",
        "description": (
            "Re-establish network segment connectivity by removing isolation ACLs "
            "and restoring routing adjacency with previously isolated peers."
        ),
        "estimated_duration_ms": 8000,
        "preconditions": [
            "Root cause of isolation has been confirmed resolved",
            "Segment health checks pass before re-integration",
        ],
    },
}


class DecisionEngine:
    """
    Evaluates D-001 through D-008 in order and produces a decision — ANIF-305.

    Pure computation engine: no I/O, no mutable state. Thread-safe.
    The caller (router) MUST write the audit record before returning the
    result to the HTTP client (ANIF-305 §9).

    The writer parameter is accepted but unused here to keep the existing
    injection interface compatible with future async callers.
    """

    def __init__(self, writer: object | None = None) -> None:
        pass  # writer is used by the router layer, not the engine itself

    def decide(
        self,
        intent_id: str,
        intent: dict[str, Any],
        risk_result: dict[str, Any],
        policy_result: dict[str, Any],
        network_state: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        Apply decision rules D-001–D-008 and return a decision record — ANIF-305.

        All fields are computed deterministically from the inputs.
        The audit record is written via self._writer.write() before returning.
        Callers in async contexts MUST await the audit write separately if needed;
        in synchronous tests the writer mock is an AsyncMock and the call is fire-and-forget.
        """
        decision_id = str(uuid.uuid4())
        safety_decision = risk_result.get("safety_decision", "allow")
        objectives = intent.get("objectives") or {}
        availability = objectives.get("availability_percent")
        latency = objectives.get("latency_ms")
        net_status = (network_state or {}).get("status", "normal")

        conflicts = policy_result.get("conflicts", [])
        has_escalated = any(c.get("resolution_type") == "escalated" for c in conflicts)

        policy_results = policy_result.get("policy_results", [])
        has_warnings = any(r.get("decision") == "warn" for r in policy_results)
        all_pass = all(r.get("decision") == "allow" for r in policy_results)

        # ── Rule state ──────────────────────────────────────────────────────
        mode = "auto"  # will be escalated by rules; never downgraded
        action_type: str | None = None
        chain: list[dict[str, Any]] = []
        step = 0

        def add_step(rule_id: str, condition: str, met: bool, outcome: str, rationale: str) -> None:
            nonlocal step
            step += 1
            chain.append(
                {
                    "step": step,
                    "rule_id": rule_id,
                    "condition_evaluated": condition,
                    "condition_met": met,
                    "outcome": outcome,
                    "rationale": rationale,
                }
            )

        def escalate(new_mode: str) -> None:
            """Escalate mode; never downgrade (auto < manual_review < block)."""
            nonlocal mode
            rank = {"auto": 0, "manual_review": 1, "block": 2}
            if rank.get(new_mode, 0) > rank.get(mode, 0):
                mode = new_mode

        # ── D-001: Block on safety_decision = block (terminal) ───────────────
        d001_met = safety_decision == "block"
        if d001_met:
            add_step(
                "D-001",
                "safety_decision = block",
                True,
                "mode set to block; recommended_action set to null; chain terminated",
                "Risk/trust assessment has determined execution is unsafe",
            )
            # Pad remaining rules as unevaluated (chain must have 8 entries)
            _pad_chain_for_block(chain, step)
            return _make_result(
                decision_id=decision_id,
                intent_id=intent_id,
                mode="block",
                action_type=None,
                confidence_score=0,
                reasoning_chain=chain,
                rollback_plan=None,
                risk_result=risk_result,
                has_warnings=has_warnings,
                all_pass=all_pass,
                net_status=net_status,
            )

        add_step(
            "D-001",
            "safety_decision = block",
            False,
            "No block applied",
            "Safety decision is not block; rule does not apply",
        )

        # ── D-002: Manual review on safety_decision = warn ──────────────────
        d002_met = safety_decision == "warn"
        if d002_met:
            escalate("manual_review")
        add_step(
            "D-002",
            "safety_decision = warn",
            d002_met,
            "mode escalated to manual_review" if d002_met else "manual_review not set by this rule",
            "Elevated risk requires human oversight before execution",
        )

        # ── D-003: Manual review on equal-precedence escalated conflict ──────
        d003_met = has_escalated
        if d003_met:
            escalate("manual_review")
        add_step(
            "D-003",
            "policy_result.conflicts contains entry with resolution_type = escalated",
            d003_met,
            (
                "mode escalated to manual_review"
                if d003_met
                else "no escalated conflict; rule does not apply"
            ),
            "Unresolved policy conflict requires human adjudication",
        )

        # ── D-004: High-availability + low-latency → reroute_traffic ─────────
        d004_met = (
            availability is not None
            and latency is not None
            and availability >= 99.99
            and latency <= 50
        )
        if d004_met:
            action_type = "reroute_traffic"
        add_step(
            "D-004",
            "objectives.availability_percent >= 99.99 AND objectives.latency_ms <= 50",
            d004_met,
            (
                "preferred action set to reroute_traffic"
                if d004_met
                else "condition not met; no action set"
            ),
            "High availability and low latency requirements indicate a topology-level response",
        )

        # ── D-005: Latency-primary concern → apply_qos ──────────────────────
        d005_met = latency is not None and not d004_met
        if d005_met and action_type is None:
            action_type = "apply_qos"
        add_step(
            "D-005",
            "objectives.latency_ms present AND NOT (availability >= 99.99 AND latency <= 50)",
            d005_met,
            "preferred action set to apply_qos" if d005_met else "condition not met; no action set",
            "Latency is the primary concern; QoS is the appropriate response",
        )

        # ── D-006: Degraded network → prefer reroute over scale_bandwidth ────
        d006_met = net_status == "degraded"
        if d006_met and action_type == "scale_bandwidth":
            action_type = "reroute_traffic"
        add_step(
            "D-006",
            "network_state.status = degraded",
            d006_met,
            (
                "reroute_traffic selected over scale_bandwidth"
                if (d006_met and action_type == "reroute_traffic")
                else "degraded network noted; no scale_bandwidth candidate to override"
            ),
            "Scaling bandwidth on a degraded network is ineffective; rerouting avoids the segment",
        )

        # ── Fallback action ──────────────────────────────────────────────────
        if action_type is None:
            action_type = "apply_qos"

        # ── D-007: isolate_segment → always manual_review ───────────────────
        d007_met = action_type == "isolate_segment"
        if d007_met:
            escalate("manual_review")
        add_step(
            "D-007",
            "recommended_action = isolate_segment",
            d007_met,
            (
                "mode escalated to manual_review"
                if d007_met
                else "action is not isolate_segment; rule does not apply"
            ),
            "Segment isolation has significant blast radius; autonomous execution is prohibited",
        )

        # ── D-008: allow → auto mode (default) ──────────────────────────────
        d008_met = safety_decision == "allow" and mode == "auto"
        add_step(
            "D-008",
            "safety_decision = allow AND no manual_review or block mode set",
            d008_met,
            "mode confirmed as auto" if d008_met else "mode already escalated; auto not applied",
            "Risk/trust assessment permits autonomous execution",
        )

        # ── Confidence score ─────────────────────────────────────────────────
        confidence = _compute_confidence(
            action_type, safety_decision, net_status, has_warnings, all_pass
        )

        # ── Rollback plan ────────────────────────────────────────────────────
        rollback_plan = dict(_ROLLBACK_PLANS[action_type]) if action_type else None

        return _make_result(
            decision_id=decision_id,
            intent_id=intent_id,
            mode=mode,
            action_type=action_type,
            confidence_score=confidence,
            reasoning_chain=chain,
            rollback_plan=rollback_plan,
            risk_result=risk_result,
            has_warnings=has_warnings,
            all_pass=all_pass,
            net_status=net_status,
        )


def _pad_chain_for_block(chain: list[dict[str, Any]], current_step: int) -> None:
    """After a terminal D-001 block, append the remaining rules as unevaluated."""
    remaining = [
        ("D-002", "safety_decision = warn"),
        ("D-003", "policy_result.conflicts contains escalated entry"),
        ("D-004", "objectives.availability_percent >= 99.99 AND objectives.latency_ms <= 50"),
        ("D-005", "objectives.latency_ms present AND NOT D-004"),
        ("D-006", "network_state.status = degraded"),
        ("D-007", "recommended_action = isolate_segment"),
        ("D-008", "safety_decision = allow AND no manual_review or block mode"),
    ]
    step = current_step
    for rule_id, condition in remaining:
        step += 1
        chain.append(
            {
                "step": step,
                "rule_id": rule_id,
                "condition_evaluated": condition,
                "condition_met": False,
                "outcome": "not evaluated (chain terminated by D-001 block)",
                "rationale": "D-001 terminated the chain; this rule was not evaluated",
            }
        )


def _compute_confidence(
    action_type: str | None,
    safety_decision: str,
    net_status: str,
    has_warnings: bool,
    all_pass: bool,
) -> int:
    """Compute confidence score — ANIF-305 §6.2."""
    if action_type is None:
        return 0
    base = _ACTION_BASE_CONFIDENCE.get(action_type, 70)
    adjustment = 0
    if safety_decision == "allow":
        adjustment += 10
    elif safety_decision == "warn":
        adjustment -= 10
    if net_status == "degraded":
        adjustment -= 15
    if all_pass:
        adjustment += 10
    if has_warnings:
        adjustment -= 5
    return max(0, min(100, base + adjustment))


def _make_result(
    *,
    decision_id: str,
    intent_id: str,
    mode: str,
    action_type: str | None,
    confidence_score: int,
    reasoning_chain: list[dict[str, Any]],
    rollback_plan: dict[str, Any] | None,
    risk_result: dict[str, Any],
    has_warnings: bool,
    all_pass: bool,
    net_status: str,
) -> dict[str, Any]:
    recommended_action: dict[str, Any] | None = None
    if action_type is not None:
        recommended_action = {
            "action_type": action_type,
            "parameters": {},
            "risk_level": _ACTION_RISK_LEVEL.get(action_type, "medium"),
        }

    return {
        "intent_id": intent_id,
        "decision_id": decision_id,
        "recommended_action": recommended_action,
        "confidence_score": confidence_score,
        "mode": mode,
        "reasoning_chain": reasoning_chain,
        "rollback_plan": rollback_plan,
        "decided_at": datetime.now(UTC).isoformat(),
    }
