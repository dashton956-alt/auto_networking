"""Unit tests for MockNetworkAdapter — ANIF-306 §10."""

from __future__ import annotations

import uuid

import pytest

from anif_platform.execution.mock_adapter import MockNetworkAdapter

ACTION_TYPES = ["reroute_traffic", "apply_qos", "scale_bandwidth", "isolate_segment"]


def make_params(action_type: str) -> dict:
    extras = {
        "reroute_traffic": {"source_segment": "seg-001", "target_segment": "seg-002", "routing_protocol": "BGP"},
        "apply_qos": {"policy_name": "latency-prio", "traffic_class": "DSCP_EF", "bandwidth_guarantee_mbps": 100},
        "scale_bandwidth": {"segment_id": "seg-001", "target_bandwidth_mbps": 500, "direction": "up"},
        "isolate_segment": {"segment_id": "seg-001", "isolation_reason": "fault", "blast_radius_assessment": "low"},
    }
    return extras.get(action_type, {"segment_id": "seg-001"})


class TestMockAdapterSuccessPath:
    def test_success_response_has_required_fields(self) -> None:
        """ANIF-306 §10.2: success response MUST have all required fields."""
        adapter = MockNetworkAdapter(seed=42, force_success=True)
        exec_id = str(uuid.uuid4())
        response = adapter.execute("apply_qos", make_params("apply_qos"), exec_id)
        assert response.success is True
        assert response.adapter_status_code == 200
        assert "apply_qos" in response.adapter_message
        assert len(response.applied_changes) > 0
        assert response.rollback_reference is not None
        assert exec_id in response.rollback_reference

    def test_success_rollback_reference_contains_execution_id(self) -> None:
        adapter = MockNetworkAdapter(seed=42, force_success=True)
        exec_id = str(uuid.uuid4())
        response = adapter.execute("reroute_traffic", make_params("reroute_traffic"), exec_id)
        assert response.rollback_reference == f"mock-rollback-{exec_id}"

    def test_success_applied_changes_mentions_action_type(self) -> None:
        adapter = MockNetworkAdapter(seed=42, force_success=True)
        exec_id = str(uuid.uuid4())
        response = adapter.execute("scale_bandwidth", make_params("scale_bandwidth"), exec_id)
        assert any("scale_bandwidth" in c for c in response.applied_changes)


class TestMockAdapterFailurePath:
    def test_failure_response_has_required_fields(self) -> None:
        """ANIF-306 §10.3: failure response MUST have required fields with success=false."""
        adapter = MockNetworkAdapter(seed=42, force_failure=True)
        exec_id = str(uuid.uuid4())
        response = adapter.execute("reroute_traffic", make_params("reroute_traffic"), exec_id)
        assert response.success is False
        assert response.applied_changes == []
        assert response.rollback_reference is None

    def test_failure_status_code_is_non_200(self) -> None:
        adapter = MockNetworkAdapter(seed=42, force_failure=True)
        response = adapter.execute("apply_qos", make_params("apply_qos"), str(uuid.uuid4()))
        assert response.adapter_status_code != 200

    def test_failure_message_mentions_action_type(self) -> None:
        adapter = MockNetworkAdapter(seed=42, force_failure=True)
        response = adapter.execute("isolate_segment", make_params("isolate_segment"), str(uuid.uuid4()))
        assert "isolate_segment" in response.adapter_message


class TestMockAdapterRollback:
    def test_rollback_with_non_null_reference_succeeds(self) -> None:
        """ANIF-306 §10.4: rollback succeeds 100% if rollback_reference is non-null."""
        adapter = MockNetworkAdapter(seed=42)
        response = adapter.rollback("apply_qos", "mock-rollback-abc123", str(uuid.uuid4()))
        assert response.success is True

    def test_rollback_with_null_reference_also_succeeds(self) -> None:
        """ANIF-306 §10.4: null reference means nothing to reverse — still success."""
        adapter = MockNetworkAdapter(seed=42)
        response = adapter.rollback("reroute_traffic", None, str(uuid.uuid4()))
        assert response.success is True
        assert response.applied_changes == []


class TestMockAdapterSuccessRates:
    def test_apply_qos_has_highest_success_rate(self) -> None:
        """ANIF-306 §10.1: apply_qos has 95% success rate — highest of four."""
        total = 200
        successes = sum(
            1
            for i in range(total)
            if MockNetworkAdapter(seed=i).execute("apply_qos", make_params("apply_qos"), str(uuid.uuid4())).success
        )
        assert successes / total >= 0.85

    def test_isolate_segment_has_lowest_success_rate(self) -> None:
        """ANIF-306 §10.1: isolate_segment has 80% success rate — lowest of four."""
        total = 200
        qos_successes = sum(
            1
            for i in range(total)
            if MockNetworkAdapter(seed=i).execute("apply_qos", make_params("apply_qos"), str(uuid.uuid4())).success
        )
        iso_successes = sum(
            1
            for i in range(total)
            if MockNetworkAdapter(seed=i).execute("isolate_segment", make_params("isolate_segment"), str(uuid.uuid4())).success
        )
        assert iso_successes <= qos_successes


class TestMockAdapterHealthCheck:
    def test_health_check_returns_healthy(self) -> None:
        adapter = MockNetworkAdapter(seed=42)
        status = adapter.health_check()
        assert status.healthy is True
        assert status.adapter_name == "mock"
        assert status.error is None
