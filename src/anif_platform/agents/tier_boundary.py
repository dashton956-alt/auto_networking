"""Tier boundary enforcement — ANIF-802 §4, ANIF-843 §6."""

from __future__ import annotations

import structlog

log = structlog.get_logger(__name__)

# Minimum tier required per endpoint category — ANIF-843 §6.2
_ENDPOINT_TIER_REQUIREMENTS: dict[str, int] = {
    "canonical_state_read": 0,
    "policy_evaluation": 1,
    "risk_scoring": 2,
    "execution_api": 3,
    "council_vote": 0,
}

_DEFAULT_REQUIRED_TIER: int = 0
_TIER_VIOLATION_SEVERITY: int = 2  # ANIF-843 §6.3


class TierBoundaryChecker:
    """Enforces tier-based access control per ANIF-802 and ANIF-843 §6."""

    def check(self, agent_tier: int, endpoint_category: str) -> bool:
        """Return True if agent_tier meets the minimum required for endpoint_category."""
        required = _ENDPOINT_TIER_REQUIREMENTS.get(endpoint_category, _DEFAULT_REQUIRED_TIER)
        return agent_tier >= required

    def log_violation(
        self,
        agent_id: str,
        agent_tier: int,
        endpoint_category: str,
    ) -> None:
        """Log a Severity 2 tier boundary violation — ANIF-843 §6.3."""
        log.warning(
            "tier_boundary_violation",
            severity=_TIER_VIOLATION_SEVERITY,
            agent_id=agent_id,
            agent_tier=agent_tier,
            endpoint_category=endpoint_category,
        )
