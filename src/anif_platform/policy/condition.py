"""Policy condition evaluator — ANIF-302 §6."""

from __future__ import annotations

from typing import Any


class ConditionParseError(Exception):
    """Raised when a condition expression cannot be parsed."""


def _get_field(path: str, intent: dict[str, Any]) -> Any:
    """Resolve a dot-separated field path in an intent dict. Returns None if missing."""
    parts = path.split(".")
    value: Any = intent
    for part in parts:
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _field_missing(path: str, intent: dict[str, Any]) -> bool:
    """Return True if the field path is not present in the intent."""
    parts = path.split(".")
    value: Any = intent
    for part in parts:
        if not isinstance(value, dict) or part not in value:
            return True
        value = value[part]
    return False


def _parse_list_literal(raw: str) -> list[str]:
    """Parse [EU,US,APAC] → ['EU', 'US', 'APAC']."""
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1]
        if not inner:
            return []
        return [v.strip() for v in inner.split(",")]
    return [v.strip() for v in raw.split(",")]


def _parse_bool_or_string(raw: str) -> Any:
    """Parse 'true'/'false' to bool, numeric strings to int/float, otherwise string."""
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    try:
        as_float = float(raw)
        return int(as_float) if as_float == int(as_float) else as_float
    except ValueError:
        return raw


class ConditionEvaluator:
    """
    Evaluates ANIF policy condition expressions — ANIF-302 §6.

    Condition syntax: field_path:operator:value
    All 8 operators are supported. Missing field behaviour per ANIF-302 §6.3.
    """

    _VALID_OPERATORS = {
        "equals", "not_equals", "greater_than", "less_than",
        "contains", "not_contains", "in_list", "not_in_list",
    }

    @classmethod
    def evaluate(cls, condition: str, intent: dict[str, Any]) -> bool:
        """
        Evaluate a condition expression against an intent dict.

        Returns True if the condition matches, False otherwise.
        Raises ConditionParseError if the expression is malformed.
        """
        parts = condition.split(":", 2)
        if len(parts) != 3:
            raise ConditionParseError(
                f"Invalid condition expression '{condition}': "
                "expected 'field_path:operator:value'"
            )
        field_path, operator, raw_value = parts

        if operator not in cls._VALID_OPERATORS:
            raise ConditionParseError(
                f"Unknown operator '{operator}' in condition '{condition}'"
            )

        missing = _field_missing(field_path, intent)
        field_value = _get_field(field_path, intent)

        # Missing field behaviour — ANIF-302 §6.3
        if missing:
            if operator in ("equals", "in_list", "contains", "greater_than", "less_than"):
                return False
            if operator in ("not_equals", "not_in_list", "not_contains"):
                return True
            return False

        if operator == "equals":
            return field_value == _parse_bool_or_string(raw_value)

        if operator == "not_equals":
            return field_value != _parse_bool_or_string(raw_value)

        if operator == "greater_than":
            try:
                return float(field_value) > float(raw_value)
            except (TypeError, ValueError):
                return False

        if operator == "less_than":
            try:
                return float(field_value) < float(raw_value)
            except (TypeError, ValueError):
                return False

        if operator == "contains":
            if isinstance(field_value, list):
                return raw_value in field_value
            if isinstance(field_value, str):
                return raw_value in field_value
            return False

        if operator == "not_contains":
            if isinstance(field_value, list):
                return raw_value not in field_value
            if isinstance(field_value, str):
                return raw_value not in field_value
            return True

        if operator == "in_list":
            allowed = _parse_list_literal(raw_value)
            return str(field_value) in allowed

        if operator == "not_in_list":
            allowed = _parse_list_literal(raw_value)
            return str(field_value) not in allowed

        return False  # unreachable
