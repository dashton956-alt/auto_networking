"""Intent Pydantic model — ANIF-300, ANIF-600 §4.1."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class Environment(str, Enum):
    prod = "prod"
    staging = "staging"
    dev = "dev"


class Region(str, Enum):
    EU = "EU"
    US = "US"
    APAC = "APAC"


class PolicyName(str, Enum):
    zero_trust = "zero_trust"
    no_public_ingress = "no_public_ingress"
    pci_compliant = "pci_compliant"
    data_residency = "data_residency"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Objectives(BaseModel):
    """Measurable outcome targets the service must meet."""

    latency_ms: Optional[Annotated[float, Field(ge=1)]] = None
    availability_percent: Optional[Annotated[float, Field(ge=90, le=100)]] = None
    throughput_mbps: Optional[float] = None


class Constraints(BaseModel):
    """Hard constraints the implementation must respect."""

    region: Optional[Region] = None
    encryption: Optional[bool] = None
    allowed_zones: Optional[list[str]] = None


class Intent(BaseModel):
    """
    Network service intent — ANIF-300 §4.1.

    Represents a declarative statement of what a service MUST achieve.
    `intent_id` is assigned by the framework after validation;
    authors MUST NOT supply it (ANIF-300 §4.4).
    """

    model_config = {"frozen": True}

    service: str
    objectives: Objectives
    constraints: Constraints
    environment: Optional[Environment] = None
    policies: Optional[list[PolicyName]] = None
    priority: Optional[Priority] = None

    @model_validator(mode="before")
    @classmethod
    def reject_author_supplied_intent_id(cls, values: dict) -> dict:
        """ANIF-300 §4.4: author-supplied intent_id MUST be rejected."""
        if "intent_id" in values:
            raise ValueError(
                "intent_id is assigned by the framework; authors MUST NOT supply it (ANIF-300 §4.4)"
            )
        return values

    @property
    def intent_id(self) -> None:
        """
        intent_id is not stored on the Intent model.
        It is assigned by the framework at validation time and stored
        on the ValidatedIntent record (see intent module, B2).
        """
        return None
