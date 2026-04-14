"""Policy Pydantic model — ANIF-600 §4.3."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class RuleAction(str, Enum):
    allow = "allow"
    deny = "deny"
    warn = "warn"


class PolicyRule(BaseModel):
    """A single conditional rule within a policy."""

    condition: Optional[str] = None
    action: Optional[RuleAction] = None


class Policy(BaseModel):
    """
    Named policy consisting of one or more conditional rules — ANIF-600 §4.3.

    Policies that fail schema validation at load time MUST be rejected
    and the engine MUST NOT start (ANIF-600 §5.3).
    """

    name: str
    rules: Annotated[list[PolicyRule], Field(min_length=1)]
