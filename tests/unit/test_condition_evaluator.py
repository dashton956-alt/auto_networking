"""Tests for ConditionEvaluator — ANIF-302 §6."""

import pytest

from anif_platform.policy.condition import ConditionEvaluator, ConditionParseError


class TestEquals:
    def test_string_equals_match(self) -> None:
        assert (
            ConditionEvaluator.evaluate("environment:equals:prod", {"environment": "prod"}) is True
        )

    def test_string_equals_no_match(self) -> None:
        assert (
            ConditionEvaluator.evaluate("environment:equals:prod", {"environment": "staging"})
            is False
        )

    def test_boolean_equals_false(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "constraints.encryption:equals:false",
                {"constraints": {"encryption": False}},
            )
            is True
        )

    def test_boolean_equals_true(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "constraints.encryption:equals:true",
                {"constraints": {"encryption": True}},
            )
            is True
        )

    def test_no_type_coercion(self) -> None:
        """ANIF-302 §6.2: type coercion MUST NOT be performed."""
        # string "false" != boolean False
        assert (
            ConditionEvaluator.evaluate(
                "constraints.encryption:equals:false",
                {"constraints": {"encryption": "false"}},
            )
            is False
        )

    def test_number_equals(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "objectives.latency_ms:equals:50",
                {"objectives": {"latency_ms": 50}},
            )
            is True
        )


class TestNotEquals:
    def test_not_equals_match(self) -> None:
        assert (
            ConditionEvaluator.evaluate("environment:not_equals:prod", {"environment": "staging"})
            is True
        )

    def test_not_equals_no_match(self) -> None:
        assert (
            ConditionEvaluator.evaluate("environment:not_equals:prod", {"environment": "prod"})
            is False
        )


class TestGreaterThan:
    def test_greater_than_match(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "objectives.availability_percent:greater_than:99.98",
                {"objectives": {"availability_percent": 99.99}},
            )
            is True
        )

    def test_greater_than_equal_is_false(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "objectives.latency_ms:greater_than:50",
                {"objectives": {"latency_ms": 50}},
            )
            is False
        )


class TestLessThan:
    def test_less_than_match(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "objectives.latency_ms:less_than:10",
                {"objectives": {"latency_ms": 5}},
            )
            is True
        )

    def test_less_than_equal_is_false(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "objectives.latency_ms:less_than:10",
                {"objectives": {"latency_ms": 10}},
            )
            is False
        )


class TestContains:
    def test_array_contains_value(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "policies:contains:pci_compliant",
                {"policies": ["zero_trust", "pci_compliant"]},
            )
            is True
        )

    def test_array_does_not_contain(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "policies:contains:pci_compliant",
                {"policies": ["zero_trust"]},
            )
            is False
        )

    def test_string_contains_substring(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "service:contains:payments",
                {"service": "payments-gateway"},
            )
            is True
        )


class TestNotContains:
    def test_array_not_contains(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "policies:not_contains:pci_compliant",
                {"policies": ["zero_trust"]},
            )
            is True
        )


class TestInList:
    def test_value_in_list(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "constraints.region:in_list:[EU,US,APAC]",
                {"constraints": {"region": "EU"}},
            )
            is True
        )

    def test_value_not_in_list(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "constraints.region:in_list:[EU,US]",
                {"constraints": {"region": "APAC"}},
            )
            is False
        )


class TestNotInList:
    def test_value_not_in_list(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "constraints.region:not_in_list:[EU,US,APAC]",
                {"constraints": {"region": "INVALID"}},
            )
            is True
        )

    def test_value_in_list_returns_false(self) -> None:
        assert (
            ConditionEvaluator.evaluate(
                "constraints.region:not_in_list:[EU,US,APAC]",
                {"constraints": {"region": "EU"}},
            )
            is False
        )


class TestMissingFieldBehaviour:
    """ANIF-302 §6.3: missing field behaviour."""

    def test_equals_missing_field_is_false(self) -> None:
        assert ConditionEvaluator.evaluate("constraints.encryption:equals:false", {}) is False

    def test_not_equals_missing_field_is_true(self) -> None:
        assert ConditionEvaluator.evaluate("constraints.encryption:not_equals:true", {}) is True

    def test_contains_missing_array_is_false(self) -> None:
        assert ConditionEvaluator.evaluate("constraints.allowed_zones:contains:eu-a", {}) is False

    def test_not_contains_missing_array_is_true(self) -> None:
        assert (
            ConditionEvaluator.evaluate("constraints.allowed_zones:not_contains:eu-a", {}) is True
        )

    def test_greater_than_missing_field_is_false(self) -> None:
        assert ConditionEvaluator.evaluate("objectives.latency_ms:greater_than:10", {}) is False

    def test_less_than_missing_field_is_false(self) -> None:
        assert ConditionEvaluator.evaluate("objectives.latency_ms:less_than:10", {}) is False

    def test_in_list_missing_field_is_false(self) -> None:
        assert ConditionEvaluator.evaluate("constraints.region:in_list:[EU,US]", {}) is False

    def test_not_in_list_missing_field_is_true(self) -> None:
        assert ConditionEvaluator.evaluate("constraints.region:not_in_list:[EU,US]", {}) is True


class TestParseErrors:
    def test_malformed_expression_raises(self) -> None:
        with pytest.raises(ConditionParseError):
            ConditionEvaluator.evaluate("not_a_valid_condition", {})

    def test_unknown_operator_raises(self) -> None:
        with pytest.raises(ConditionParseError):
            ConditionEvaluator.evaluate("field:unknown_op:value", {})
