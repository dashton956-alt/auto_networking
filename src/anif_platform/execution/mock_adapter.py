"""
MockNetworkAdapter — deterministic simulated execution — ANIF-306 §10.

Uses a seeded random number generator so behaviour is reproducible in tests.
Pass force_success=True or force_failure=True to override probability.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime
from typing import Any

import structlog

from anif_platform.execution.adapter import AdapterHealthStatus, AdapterResponse

log = structlog.get_logger(__name__)

# Mock success probabilities — ANIF-306 §10.1
_SUCCESS_RATES: dict[str, float] = {
    "reroute_traffic": 0.90,
    "apply_qos": 0.95,
    "scale_bandwidth": 0.85,
    "isolate_segment": 0.80,
}

# Failure status codes — ANIF-306 §10.1
_FAILURE_CODES: dict[str, int] = {
    "reroute_traffic": 503,
    "apply_qos": 422,
    "scale_bandwidth": 503,
    "isolate_segment": 500,
}

_DEFAULT_SUCCESS_RATE: float = 0.90
_DEFAULT_FAILURE_CODE: int = 503


class MockNetworkAdapter:
    """
    Simulates action execution without making real network changes — ANIF-306 §10.

    Parameters
    ----------
    seed:
        Seed for the random number generator. Use a fixed seed in tests.
    force_success:
        If True, always return a success response regardless of probability.
    force_failure:
        If True, always return a failure response regardless of probability.
    """

    def __init__(
        self,
        seed: int | None = None,
        force_success: bool = False,
        force_failure: bool = False,
    ) -> None:
        self._rng = random.Random(seed)
        self._force_success = force_success
        self._force_failure = force_failure

    def execute(
        self,
        action_type: str,
        parameters: dict[str, Any],
        execution_id: str,
    ) -> AdapterResponse:
        """Simulate executing an action — ANIF-306 §10.2 / §10.3."""
        success_rate = _SUCCESS_RATES.get(action_type, _DEFAULT_SUCCESS_RATE)

        if self._force_success:
            success = True
        elif self._force_failure:
            success = False
        else:
            success = self._rng.random() < success_rate

        if success:
            segment_id = parameters.get("segment_id") or parameters.get("source_segment", "unknown")
            log.debug(
                "mock_adapter_execute",
                action_type=action_type,
                execution_id=execution_id,
                success=True,
            )
            return AdapterResponse(
                success=True,
                adapter_status_code=200,
                adapter_message=f"Mock action applied: {action_type}",
                applied_changes=[f"Simulated change: {action_type} on segment {segment_id}"],
                rollback_reference=f"mock-rollback-{execution_id}",
            )

        log.debug(
            "mock_adapter_execute",
            action_type=action_type,
            execution_id=execution_id,
            success=False,
        )
        return AdapterResponse(
            success=False,
            adapter_status_code=_FAILURE_CODES.get(action_type, _DEFAULT_FAILURE_CODE),
            adapter_message=f"Mock adapter simulated failure for action: {action_type}",
            applied_changes=[],
            rollback_reference=None,
        )

    def rollback(
        self,
        action_type: str,
        rollback_reference: str | None,
        execution_id: str,
    ) -> AdapterResponse:
        """
        Simulate rollback — ANIF-306 §10.4.

        Succeeds 100% of the time. If rollback_reference is None,
        no changes were applied so there is nothing to reverse.
        """
        log.debug(
            "mock_adapter_rollback",
            action_type=action_type,
            execution_id=execution_id,
            success=True,
        )
        if rollback_reference is None:
            return AdapterResponse(
                success=True,
                adapter_status_code=200,
                adapter_message="No changes to reverse; original action did not apply.",
                applied_changes=[],
                rollback_reference=None,
            )

        return AdapterResponse(
            success=True,
            adapter_status_code=200,
            adapter_message=f"Mock rollback applied for: {action_type}",
            applied_changes=[f"Reversed: {action_type} (ref={rollback_reference})"],
            rollback_reference=None,
        )

    def health_check(self) -> AdapterHealthStatus:
        """Return healthy status — mock adapter is always healthy."""
        return AdapterHealthStatus(
            healthy=True,
            adapter_name="mock",
            last_checked=datetime.now(UTC),
            error=None,
        )
