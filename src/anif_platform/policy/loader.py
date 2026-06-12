"""PolicyLoader — loads policy YAML files from the policies/ directory."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from anif_platform.schemas.policy import RuleAction


class PolicyLoadError(Exception):
    """Raised when a policy file cannot be loaded or is invalid."""


class PolicyLoader:
    """
    Loads policy definitions from YAML files.

    All .yml files in the policies directory are loaded at startup.
    Drop in new .yml files to add policies — no code changes required.
    The data_residency policy has its approved region list rewritten
    from DATA_RESIDENCY_APPROVED_REGIONS env var before evaluation.
    """

    def __init__(self, policies_dir: str | Path | None = None) -> None:
        if policies_dir is None:
            # Default to policies/ at project root
            self._dir = Path(__file__).parent.parent.parent.parent / "policies"
        else:
            self._dir = Path(policies_dir)

    def load_all(self) -> dict[str, dict[str, Any]]:
        """
        Load all policy YAML files from the policies directory.

        Returns a dict mapping policy name → raw policy dict.
        Raises PolicyLoadError if any file is invalid.
        """
        if not self._dir.exists():
            raise PolicyLoadError(f"Policies directory not found: {self._dir}")

        policies: dict[str, dict[str, Any]] = {}
        for path in sorted(self._dir.glob("*.yml")):
            policy = self._load_file(path)
            name = policy.get("name")
            if not name:
                raise PolicyLoadError(f"Policy file {path} is missing 'name' field")
            policies[name] = policy

        return self._apply_env_overrides(policies)

    def _load_file(self, path: Path) -> dict[str, Any]:
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                raise PolicyLoadError(f"Policy file {path} must be a YAML object")
            # Validate against Policy schema (ANIF-302 §5 / ANIF-600 §5.3)
            self._validate_policy_schema(data, path)
            return data
        except yaml.YAMLError as exc:
            raise PolicyLoadError(f"Failed to parse {path}: {exc}") from exc

    @staticmethod
    def _validate_policy_schema(data: dict[str, Any], path: Path) -> None:
        """Policies that fail schema validation MUST be rejected — ANIF-600 §5.3."""
        if "name" not in data:
            raise PolicyLoadError(f"{path}: missing required field 'name'")
        if "rules" not in data or not isinstance(data["rules"], list) or len(data["rules"]) == 0:
            raise PolicyLoadError(f"{path}: 'rules' must be a non-empty list")
        valid_actions = {a.value for a in RuleAction}
        for i, rule in enumerate(data["rules"]):
            if "condition" not in rule:
                raise PolicyLoadError(f"{path}: rule {i} missing 'condition'")
            if "action" not in rule:
                raise PolicyLoadError(f"{path}: rule {i} missing 'action'")
            if rule["action"] not in valid_actions:
                raise PolicyLoadError(f"{path}: rule {i} has invalid action '{rule['action']}'")

    @staticmethod
    def _apply_env_overrides(policies: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """
        Apply environment variable overrides to parameterised policies.

        data_residency: rewrites the approved region list from
        DATA_RESIDENCY_APPROVED_REGIONS env var (comma-separated).
        """
        approved = os.environ.get("DATA_RESIDENCY_APPROVED_REGIONS", "EU,US,APAC")
        region_list = "[" + ",".join(r.strip() for r in approved.split(",")) + "]"

        if "data_residency" in policies:
            for rule in policies["data_residency"]["rules"]:
                if "{approved_regions}" in rule.get("condition", ""):
                    rule["condition"] = rule["condition"].replace("{approved_regions}", approved)
                if "not_in_list:" in rule.get("condition", ""):
                    # Rewrite the list literal with current approved regions
                    parts = rule["condition"].split(":", 2)
                    if len(parts) == 3:
                        rule["condition"] = f"{parts[0]}:{parts[1]}:{region_list}"

        return policies
