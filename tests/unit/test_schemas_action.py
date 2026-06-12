"""Tests for Action Pydantic model — ANIF-600 §4.2."""

import pytest
from pydantic import ValidationError

from anif_platform.schemas.action import Action, ActionType, RiskLevel


class TestAction:
    def test_valid_reroute_traffic(self) -> None:
        action = Action(
            action_type=ActionType.reroute_traffic,
            parameters={"target_path": "path-b", "source_segment": "eu-west-1"},
            risk_level=RiskLevel.medium,
        )
        assert action.action_type == ActionType.reroute_traffic

    def test_action_type_required(self) -> None:
        with pytest.raises(ValidationError):
            Action()  # type: ignore[call-arg]

    def test_invalid_action_type_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Action(action_type="delete_route")  # type: ignore[arg-type]

    def test_all_four_action_types_valid(self) -> None:
        for action_type in ActionType:
            action = Action(action_type=action_type)
            assert action.action_type == action_type

    def test_parameters_optional(self) -> None:
        action = Action(action_type=ActionType.apply_qos)
        assert action.parameters is None

    def test_risk_level_optional(self) -> None:
        action = Action(action_type=ActionType.scale_bandwidth)
        assert action.risk_level is None

    def test_invalid_risk_level_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Action(action_type=ActionType.reroute_traffic, risk_level="critical")  # type: ignore[arg-type]
