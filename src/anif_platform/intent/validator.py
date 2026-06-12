"""IntentValidator — ANIF-301 §7, VAL-001 through VAL-007."""

from __future__ import annotations

from uuid import uuid4

from anif_platform.intent.schemas import ValidationResult
from anif_platform.schemas.intent import Environment, Intent, PolicyName, Priority


class IntentValidator:
    """
    Validates an intent document against all ANIF-301 rules.

    All rules are evaluated — validation MUST NOT short-circuit on the first
    error (ANIF-301 §10.4). Multiple errors MAY be returned in a single result.
    """

    def validate(self, intent: Intent) -> ValidationResult:
        """
        Validate an intent and apply defaults.

        Returns ValidationResult with:
        - intent_id set and status="validated" if no blocking errors
        - intent_id=None and status="validation_failed" if any blocking error
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Apply defaults before validation (ANIF-301 §6)
        resolved = intent.model_dump(mode="json")
        if resolved.get("environment") is None:
            resolved["environment"] = Environment.dev.value
        if resolved.get("priority") is None:
            resolved["priority"] = Priority.medium.value
        if resolved.get("policies") is None:
            resolved["policies"] = []

        environment = resolved["environment"]
        priority = resolved["priority"]
        policies = resolved["policies"]
        objectives = resolved.get("objectives") or {}
        constraints = resolved.get("constraints") or {}

        # VAL-001 — latency warning (non-blocking)
        latency = objectives.get("latency_ms")
        if latency is not None and latency < 10:
            warnings.append(
                "objectives.latency_ms: value below 10 ms is unlikely to be achievable "
                "in most environments; proceeding with intent submission"
            )

        # VAL-003 — prod requires high or critical priority (blocking)
        if environment == Environment.prod.value and priority not in (
            Priority.high.value,
            Priority.critical.value,
        ):
            errors.append(
                f"priority: production environment requires priority to be "
                f"'high' or 'critical'; received '{priority}'"
            )

        # VAL-004 — pci_compliant requires encryption=true (blocking)
        if PolicyName.pci_compliant.value in policies:
            encryption = constraints.get("encryption")
            if encryption is not True:
                errors.append(
                    "constraints.encryption: pci_compliant policy requires encryption to be true"
                )

        # VAL-005 — availability >= 99.99 requires >= 2 allowed_zones (blocking)
        availability = objectives.get("availability_percent")
        if availability is not None and availability >= 99.99:
            allowed_zones = constraints.get("allowed_zones") or []
            n = len(allowed_zones)
            if n < 2:
                errors.append(
                    f"constraints.allowed_zones: availability_percent >= 99.99 requires "
                    f"at least 2 allowed zones; {n} provided"
                )

        if errors:
            return ValidationResult(
                status="validation_failed",
                errors=errors,
                warnings=warnings,
            )

        return ValidationResult(
            intent_id=uuid4(),
            status="validated",
            warnings=warnings,
            validated_intent=resolved,
        )
