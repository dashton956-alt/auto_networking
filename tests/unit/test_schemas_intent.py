"""Tests for Intent Pydantic model — ANIF-300, ANIF-600 §4.1."""

import pytest
from pydantic import ValidationError

from anif_platform.schemas.intent import (
    Constraints,
    Environment,
    Intent,
    Objectives,
    PolicyName,
    Priority,
    Region,
)


class TestObjectives:
    def test_valid_objectives(self) -> None:
        obj = Objectives(latency_ms=50, availability_percent=99.9, throughput_mbps=500)
        assert obj.latency_ms == 50
        assert obj.availability_percent == 99.9

    def test_availability_below_minimum_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Objectives(availability_percent=89.9)

    def test_availability_at_minimum_accepted(self) -> None:
        obj = Objectives(availability_percent=90.0)
        assert obj.availability_percent == 90.0

    def test_availability_above_maximum_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Objectives(availability_percent=100.1)

    def test_latency_below_minimum_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Objectives(latency_ms=0)

    def test_latency_at_minimum_accepted(self) -> None:
        obj = Objectives(latency_ms=1)
        assert obj.latency_ms == 1

    def test_all_fields_optional(self) -> None:
        obj = Objectives()
        assert obj.latency_ms is None
        assert obj.availability_percent is None
        assert obj.throughput_mbps is None


class TestConstraints:
    def test_valid_region(self) -> None:
        c = Constraints(region=Region.EU)
        assert c.region == Region.EU

    def test_invalid_region_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Constraints(region="INVALID")  # type: ignore[arg-type]

    def test_all_fields_optional(self) -> None:
        c = Constraints()
        assert c.region is None
        assert c.encryption is None
        assert c.allowed_zones is None


class TestIntent:
    def test_minimal_valid_intent(self) -> None:
        intent = Intent(service="payments", objectives=Objectives(), constraints=Constraints())
        assert intent.service == "payments"
        assert intent.intent_id is None

    def test_service_required(self) -> None:
        with pytest.raises(ValidationError):
            Intent(objectives=Objectives(), constraints=Constraints())  # type: ignore[call-arg]

    def test_objectives_required(self) -> None:
        with pytest.raises(ValidationError):
            Intent(service="payments", constraints=Constraints())  # type: ignore[call-arg]

    def test_constraints_required(self) -> None:
        with pytest.raises(ValidationError):
            Intent(service="payments", objectives=Objectives())  # type: ignore[call-arg]

    def test_invalid_environment_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Intent(
                service="payments",
                objectives=Objectives(),
                constraints=Constraints(),
                environment="production",  # type: ignore[arg-type]
            )

    def test_valid_environment_accepted(self) -> None:
        intent = Intent(
            service="payments",
            objectives=Objectives(),
            constraints=Constraints(),
            environment=Environment.prod,
        )
        assert intent.environment == Environment.prod

    def test_invalid_priority_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Intent(
                service="payments",
                objectives=Objectives(),
                constraints=Constraints(),
                priority="urgent",  # type: ignore[arg-type]
            )

    def test_valid_policies_accepted(self) -> None:
        intent = Intent(
            service="payments",
            objectives=Objectives(),
            constraints=Constraints(),
            policies=[PolicyName.zero_trust, PolicyName.pci_compliant],
        )
        assert len(intent.policies) == 2  # type: ignore[arg-type]

    def test_invalid_policy_name_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Intent(
                service="payments",
                objectives=Objectives(),
                constraints=Constraints(),
                policies=["custom_policy"],  # type: ignore[list-item]
            )

    def test_intent_id_field_is_none_by_default(self) -> None:
        """Author-supplied intent_id MUST be rejected per ANIF-300 §4.4."""
        intent = Intent(service="payments", objectives=Objectives(), constraints=Constraints())
        assert intent.intent_id is None

    def test_intent_id_cannot_be_set_by_author(self) -> None:
        """ANIF-300 §4.4: author-supplied IDs MUST be rejected."""
        import uuid

        with pytest.raises(ValidationError):
            Intent(
                service="payments",
                objectives=Objectives(),
                constraints=Constraints(),
                intent_id=uuid.uuid4(),  # type: ignore[call-arg]
            )

    def test_full_production_intent(self) -> None:
        intent = Intent(
            service="payments-gateway",
            environment=Environment.prod,
            objectives=Objectives(latency_ms=45, availability_percent=99.99, throughput_mbps=500),
            constraints=Constraints(
                region=Region.EU,
                encryption=True,
                allowed_zones=["eu-west-1a", "eu-west-1b"],
            ),
            policies=[PolicyName.zero_trust, PolicyName.pci_compliant, PolicyName.data_residency],
            priority=Priority.critical,
        )
        assert intent.service == "payments-gateway"
        assert intent.environment == Environment.prod
        assert intent.priority == Priority.critical
