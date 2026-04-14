"""Action Pydantic model — ANIF-600 §4.2."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class ActionType(str, Enum):
    reroute_traffic = "reroute_traffic"
    apply_qos = "apply_qos"
    scale_bandwidth = "scale_bandwidth"
    isolate_segment = "isolate_segment"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Action(BaseModel):
    """
    Discrete autonomous remediation or configuration action — ANIF-600 §4.2.

    Produced by the decision engine; consumed by the execution layer.
    Invalid action objects MUST NOT be forwarded to execution (ANIF-600 §5.2).
    """

    action_type: ActionType
    parameters: Optional[dict[str, Any]] = None
    risk_level: Optional[RiskLevel] = None
