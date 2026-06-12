"""Tests for Policy Pydantic model — ANIF-600 §4.3."""

import pytest
from pydantic import ValidationError

from anif_platform.schemas.policy import Policy, PolicyRule, RuleAction


class TestPolicyRule:
    def test_valid_deny_rule(self) -> None:
        rule = PolicyRule(condition="constraints.encryption:equals:false", action=RuleAction.deny)
        assert rule.action == RuleAction.deny

    def test_invalid_action_rejected(self) -> None:
        with pytest.raises(ValidationError):
            PolicyRule(condition="x:equals:y", action="reject")  # type: ignore[arg-type]

    def test_condition_optional(self) -> None:
        rule = PolicyRule(action=RuleAction.allow)
        assert rule.condition is None

    def test_all_three_actions_valid(self) -> None:
        for action in RuleAction:
            rule = PolicyRule(action=action)
            assert rule.action == action


class TestPolicy:
    def test_valid_policy(self) -> None:
        policy = Policy(
            name="pci_compliant",
            rules=[
                PolicyRule(condition="constraints.encryption:equals:false", action=RuleAction.deny),
                PolicyRule(condition="environment:equals:prod", action=RuleAction.allow),
            ],
        )
        assert policy.name == "pci_compliant"
        assert len(policy.rules) == 2

    def test_name_required(self) -> None:
        with pytest.raises(ValidationError):
            Policy(rules=[PolicyRule(action=RuleAction.allow)])  # type: ignore[call-arg]

    def test_rules_required(self) -> None:
        with pytest.raises(ValidationError):
            Policy(name="zero_trust")  # type: ignore[call-arg]

    def test_empty_rules_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Policy(name="zero_trust", rules=[])

    def test_single_rule_accepted(self) -> None:
        policy = Policy(name="zero_trust", rules=[PolicyRule(action=RuleAction.deny)])
        assert len(policy.rules) == 1
