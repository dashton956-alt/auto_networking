"""Intent Pydantic model — ANIF-300, ANIF-600 §4.1."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any

from pydantic import BaseModel, Field, model_validator


class Environment(StrEnum):
    prod = "prod"
    staging = "staging"
    dev = "dev"


class Region(StrEnum):
    EU = "EU"
    US = "US"
    APAC = "APAC"


class PolicyName(StrEnum):
    zero_trust = "zero_trust"
    no_public_ingress = "no_public_ingress"
    pci_compliant = "pci_compliant"
    data_residency = "data_residency"


class Priority(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Objectives(BaseModel):
    """Measurable outcome targets the service must meet."""

    latency_ms: Annotated[float, Field(ge=1)] | None = None
    availability_percent: Annotated[float, Field(ge=90, le=100)] | None = None
    throughput_mbps: float | None = None


class Constraints(BaseModel):
    """Hard constraints the implementation must respect."""

    region: Region | None = None
    encryption: bool | None = None
    allowed_zones: list[str] | None = None


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
    environment: Environment | None = None
    policies: list[PolicyName] | None = None
    priority: Priority | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_author_supplied_intent_id(cls, values: dict[str, Any]) -> dict[str, Any]:
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
