"""
Prometheus governance metrics — ANIF-406 §4.5.

All counters and histograms defined here. Import and call .inc()/.observe()
at the point of the event.
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram

GOVERNANCE_AUTO = Counter(
    "anif_governance_auto_total",
    "Total executions routed as auto",
    ["environment"],
)

GOVERNANCE_MANUAL_REVIEW = Counter(
    "anif_governance_manual_review_total",
    "Total executions routed to manual_review",
    ["environment"],
)

GOVERNANCE_BLOCK = Counter(
    "anif_governance_block_total",
    "Total executions blocked, by triggering rule",
    ["environment", "triggered_rule"],
)

TICKET_APPROVED = Counter(
    "anif_ticket_approved_total",
    "Total tickets approved, by approver role",
    ["environment", "approver_role"],
)

TICKET_REJECTED = Counter(
    "anif_ticket_rejected_total",
    "Total tickets rejected",
    ["environment"],
)

TICKET_EXPIRED = Counter(
    "anif_ticket_expired_total",
    "Total tickets that expired without action",
    ["environment"],
)

RULE_TRIGGERS = Counter(
    "anif_governance_rule_triggers_total",
    "Total times each governance rule was triggered",
    ["rule_id", "environment"],
)

TICKET_PENDING_AGE = Histogram(
    "anif_ticket_pending_age_seconds",
    "Age of pending tickets at time of action or expiry",
    ["environment"],
    buckets=[30, 60, 120, 300, 600, 900],
)
