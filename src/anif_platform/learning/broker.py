"""Knowledge Broker (Learning Agent) — ANIF-812.

Implements:
- Human approval gate before any distribution (CR-812-01)
- Evidence reference requirement (CR-812-02)
- Role-scoped distribution enforcement (CR-812-03)
- Source quality tracking and flagging (CR-812-05)
- Negative example capture from all four mandatory sources (CR-812-06)
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.learning.schemas import (
    KnowledgeItemInput,
    KnowledgePackageInput,
    NegativeExampleSource,
)

log = structlog.get_logger(__name__)

# Source quality thresholds — CR-812-05
_FLAG_THRESHOLD: float = 0.60
_RECOVERY_THRESHOLD: float = 0.70


class KnowledgeBrokerError(Exception):
    """Raised when broker policy is violated."""


class KnowledgeBroker:
    """Network Knowledge Broker — aggregates, approves, and distributes knowledge packages.

    In production this would use the DB. Unit tests use in-memory stores for isolation.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        # package_id → package dict
        self._packages: dict[str, dict[str, Any]] = {}
        # source_id → quality score
        self._source_quality: dict[str, float] = {}
        # source_id → flagged bool
        self._flagged_sources: set[str] = set()

    # ── Package submission ────────────────────────────────────────────────

    async def submit_package(self, pkg: KnowledgePackageInput) -> dict[str, Any]:
        """Validate and submit a knowledge package for human approval — CR-812-01/02."""
        for item in pkg.knowledge_items:
            if not item.evidence:
                raise KnowledgeBrokerError(
                    f"knowledge item from source '{item.source}' is missing evidence — "
                    "items without verifiable evidence MUST NOT be submitted (CR-812-02)."
                )

        package_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        record: dict[str, Any] = {
            "package_id": package_id,
            "category": pkg.category,
            "target_roles": pkg.target_roles,
            "submitted_by": pkg.submitted_by,
            "approval_status": "pending",
            "submitted_at": now,
            "knowledge_items": [i.model_dump() for i in pkg.knowledge_items],
            "approver_id": None,
            "approval_timestamp": None,
            "reject_reason": None,
        }
        self._packages[package_id] = record
        log.info("knowledge_package_submitted", package_id=package_id, category=pkg.category)
        return record

    # ── Approval gate ─────────────────────────────────────────────────────

    async def approve_package(self, package_id: str, approver_id: str) -> dict[str, Any]:
        """Human approves a pending package — CR-812-01."""
        pkg = self._get_package(package_id)
        pkg["approval_status"] = "approved"
        pkg["approver_id"] = approver_id
        pkg["approval_timestamp"] = datetime.now(UTC).isoformat()
        log.info("knowledge_package_approved", package_id=package_id, approver=approver_id)
        return pkg

    async def reject_package(
        self, package_id: str, approver_id: str, reason: str
    ) -> dict[str, Any]:
        """Human rejects a pending package — CR-812-01."""
        pkg = self._get_package(package_id)
        pkg["approval_status"] = "rejected"
        pkg["approver_id"] = approver_id
        pkg["approval_timestamp"] = datetime.now(UTC).isoformat()
        pkg["reject_reason"] = reason
        log.info("knowledge_package_rejected", package_id=package_id, reason=reason)
        return pkg

    # ── Distribution ──────────────────────────────────────────────────────

    async def distribute(self, package_id: str) -> dict[str, Any]:
        """Distribute an approved package — enforces approval gate and source quality (CR-812-01/03/05)."""
        pkg = self._get_package(package_id)

        if pkg["approval_status"] != "approved":
            raise KnowledgeBrokerError(
                f"Package {package_id} is not approved for distribution (status: {pkg['approval_status']}) "
                "— CR-812-01."
            )

        # CR-812-05: block distribution from flagged sources without enhanced review
        sources_in_pkg = {item["source"] for item in pkg["knowledge_items"]}
        flagged = sources_in_pkg & self._flagged_sources
        if flagged:
            raise KnowledgeBrokerError(
                f"Package {package_id} contains items from flagged source(s) {flagged} "
                "— distribution withheld pending enhanced human review (CR-812-05)."
            )

        log.info("knowledge_package_distributed", package_id=package_id)
        return {"package_id": package_id, "distributed": True}

    def role_matches(self, package_id: str, agent_role: str) -> bool:
        """Check whether an agent role is in the package's target_roles — CR-812-03."""
        pkg = self._get_package(package_id)
        return agent_role in pkg["target_roles"]

    # ── Source quality ────────────────────────────────────────────────────

    def update_source_quality(self, source: str, quality_score: float) -> None:
        """Update source quality score; flag/unflag as required — CR-812-05."""
        self._source_quality[source] = quality_score
        if quality_score < _FLAG_THRESHOLD:
            self._flagged_sources.add(source)
            log.warning("knowledge_source_flagged", source=source, quality=quality_score)
        elif quality_score >= _RECOVERY_THRESHOLD and source in self._flagged_sources:
            self._flagged_sources.discard(source)
            log.info("knowledge_source_unflagged", source=source, quality=quality_score)

    def is_source_flagged(self, source: str) -> bool:
        return source in self._flagged_sources

    # ── Negative example capture ──────────────────────────────────────────

    async def capture_negative_example(
        self,
        source: NegativeExampleSource,
        description: str,
        evidence: str,
        agent_roles: list[str],
    ) -> dict[str, Any]:
        """Capture a negative example and create a pending package — CR-812-06/07."""
        item = KnowledgeItemInput(
            type="negative_example",
            description=description,
            source=source.value,
            confidence=1.0,
            evidence=evidence,
            applicable_conditions="",
        )
        pkg_input = KnowledgePackageInput(
            category="resolution",
            target_roles=agent_roles,
            submitted_by="platform-auto",
            knowledge_items=[item],
        )
        pkg = await self.submit_package(pkg_input)
        return {
            "package_id": pkg["package_id"],
            "type": "negative_example",
            "source": source.value,
            "approval_status": "pending",
        }

    # ── Helpers ───────────────────────────────────────────────────────────

    def _get_package(self, package_id: str) -> dict[str, Any]:
        pkg = self._packages.get(package_id)
        if pkg is None:
            raise KnowledgeBrokerError(f"Unknown package_id: {package_id}")
        return pkg
