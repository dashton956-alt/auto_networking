"""Tests for IntentValidator — ANIF-301 §7 (VAL-001–VAL-007)."""

import pytest

from anif_platform.intent.validator import IntentValidator
from anif_platform.schemas.intent import (
    Constraints,
    Environment,
    Intent,
    Objectives,
    PolicyName,
    Priority,
    Region,
)


def make_valid_prod_intent(**kwargs) -> Intent:
    defaults = dict(
        service="payments",
        environment=Environment.prod,
        objectives=Objectives(availability_percent=99.5, latency_ms=50),
        constraints=Constraints(region=Region.EU, encryption=True, allowed_zones=["eu-a"]),
        priority=Priority.high,
    )
    defaults.update(kwargs)
    return Intent(**defaults)


class TestDefaultsApplied:
    def test_environment_defaults_to_dev(self) -> None:
        intent = Intent(
            service="svc",
            objectives=Objectives(latency_ms=50),
            constraints=Constraints(region=Region.EU),
        )
        validator = IntentValidator()
        result = validator.validate(intent)
        assert result.validated_intent["environment"] == "dev"

    def test_priority_defaults_to_medium(self) -> None:
        intent = Intent(
            service="svc",
            objectives=Objectives(latency_ms=50),
            constraints=Constraints(region=Region.EU),
        )
        validator = IntentValidator()
        result = validator.validate(intent)
        assert result.validated_intent["priority"] == "medium"

    def test_policies_defaults_to_empty_list(self) -> None:
        intent = Intent(
            service="svc",
            objectives=Objectives(latency_ms=50),
            constraints=Constraints(region=Region.EU),
        )
        validator = IntentValidator()
        result = validator.validate(intent)
        assert result.validated_intent["policies"] == []


class TestVAL001LatencyWarning:
    def test_latency_below_10_produces_warning(self) -> None:
        intent = make_valid_prod_intent(
            objectives=Objectives(latency_ms=5, availability_percent=99.5)
        )
        validator = IntentValidator()
        result = validator.validate(intent)
        assert result.intent_id is not None  # warning does not block
        assert any("latency_ms" in w and "10 ms" in w for w in result.warnings)

    def test_latency_at_10_no_warning(self) -> None:
        intent = make_valid_prod_intent(
            objectives=Objectives(latency_ms=10, availability_percent=99.5)
        )
        result = IntentValidator().validate(intent)
        assert not any("latency_ms" in w for w in result.warnings)


class TestVAL003ProdPriority:
    def test_prod_without_high_priority_fails(self) -> None:
        intent = make_valid_prod_intent(priority=Priority.low)
        result = IntentValidator().validate(intent)
        assert result.intent_id is None
        assert any("priority" in e and "prod" in e for e in result.errors)

    def test_prod_with_medium_priority_fails(self) -> None:
        intent = make_valid_prod_intent(priority=Priority.medium)
        result = IntentValidator().validate(intent)
        assert result.intent_id is None

    def test_prod_with_high_priority_passes(self) -> None:
        result = IntentValidator().validate(make_valid_prod_intent(priority=Priority.high))
        assert result.intent_id is not None

    def test_prod_with_critical_priority_passes(self) -> None:
        result = IntentValidator().validate(make_valid_prod_intent(priority=Priority.critical))
        assert result.intent_id is not None

    def test_staging_with_low_priority_passes(self) -> None:
        intent = Intent(
            service="svc",
            environment=Environment.staging,
            objectives=Objectives(latency_ms=50),
            constraints=Constraints(region=Region.EU, encryption=True),
            priority=Priority.low,
        )
        result = IntentValidator().validate(intent)
        assert result.intent_id is not None


class TestVAL004PCIEncryption:
    def test_pci_without_encryption_fails(self) -> None:
        intent = make_valid_prod_intent(
            constraints=Constraints(region=Region.EU, encryption=False, allowed_zones=["eu-a"]),
            policies=[PolicyName.pci_compliant],
        )
        result = IntentValidator().validate(intent)
        assert result.intent_id is None
        assert any("encryption" in e and "pci_compliant" in e for e in result.errors)

    def test_pci_with_encryption_passes(self) -> None:
        intent = make_valid_prod_intent(
            constraints=Constraints(region=Region.EU, encryption=True, allowed_zones=["eu-a"]),
            policies=[PolicyName.pci_compliant],
        )
        result = IntentValidator().validate(intent)
        assert result.intent_id is not None


class TestVAL005HighAvailabilityZones:
    def test_99_99_availability_requires_2_zones(self) -> None:
        intent = make_valid_prod_intent(
            objectives=Objectives(availability_percent=99.99),
            constraints=Constraints(
                region=Region.EU, encryption=True, allowed_zones=["eu-a"]
            ),
        )
        result = IntentValidator().validate(intent)
        assert result.intent_id is None
        assert any("allowed_zones" in e and "2" in e for e in result.errors)

    def test_99_99_availability_with_2_zones_passes(self) -> None:
        intent = make_valid_prod_intent(
            objectives=Objectives(availability_percent=99.99),
            constraints=Constraints(
                region=Region.EU, encryption=True, allowed_zones=["eu-a", "eu-b"]
            ),
        )
        result = IntentValidator().validate(intent)
        assert result.intent_id is not None

    def test_99_9_availability_with_1_zone_passes(self) -> None:
        intent = make_valid_prod_intent(
            objectives=Objectives(availability_percent=99.9),
            constraints=Constraints(
                region=Region.EU, encryption=True, allowed_zones=["eu-a"]
            ),
        )
        result = IntentValidator().validate(intent)
        assert result.intent_id is not None


class TestMultipleErrors:
    def test_all_errors_returned_without_short_circuit(self) -> None:
        """ANIF-301 §10.4: MUST NOT short-circuit on first error."""
        intent = Intent(
            service="billing",
            environment=Environment.prod,
            objectives=Objectives(availability_percent=99.99),
            constraints=Constraints(
                region=Region.EU,
                encryption=False,
                allowed_zones=["eu-a"],
            ),
            policies=[PolicyName.pci_compliant],
            priority=Priority.medium,
        )
        result = IntentValidator().validate(intent)
        assert result.intent_id is None
        # Should have: VAL-003 (prod+medium), VAL-004 (pci+no-encryption), VAL-005 (99.99+1zone)
        assert len(result.errors) >= 3

    def test_intent_id_not_assigned_when_any_blocking_error(self) -> None:
        """ANIF-301 §10.5: intent_id MUST NOT be assigned when any blocking rule violated."""
        intent = make_valid_prod_intent(priority=Priority.low)
        result = IntentValidator().validate(intent)
        assert result.intent_id is None
        assert result.status == "validation_failed"

    def test_status_is_validated_on_success(self) -> None:
        result = IntentValidator().validate(make_valid_prod_intent())
        assert result.status == "validated"
        assert result.intent_id is not None
