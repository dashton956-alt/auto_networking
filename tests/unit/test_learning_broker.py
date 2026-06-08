"""Unit tests for KnowledgeBroker — ANIF-812."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from anif_platform.learning.broker import KnowledgeBroker, KnowledgeBrokerError
from anif_platform.learning.schemas import (
    KnowledgeItemInput,
    KnowledgePackageInput,
    NegativeExampleSource,
)


def make_item(evidence: str | None = "intent-abc123") -> KnowledgeItemInput:
    return KnowledgeItemInput(
        type="positive_example",
        description="Traffic reroute succeeds after BGP convergence",
        source="noc_manager",
        confidence=0.85,
        evidence=evidence,
        applicable_conditions="BGP convergence delay > 30s",
    )


def make_package(
    target_roles: list[str] | None = None,
    items: list[KnowledgeItemInput] | None = None,
) -> KnowledgePackageInput:
    return KnowledgePackageInput(
        category="network_pattern",
        target_roles=target_roles or ["network_observer"],
        submitted_by="noc_manager",
        knowledge_items=items or [make_item()],
    )


def make_broker() -> tuple[KnowledgeBroker, AsyncMock]:
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    broker = KnowledgeBroker(session=session)
    return broker, session


class TestApprovalGate:
    @pytest.mark.asyncio
    async def test_new_package_has_pending_status(self) -> None:
        """CR-812-01: Packages start as pending — not yet approved."""
        broker, _ = make_broker()
        result = await broker.submit_package(make_package())
        assert result["approval_status"] == "pending"

    @pytest.mark.asyncio
    async def test_pending_package_cannot_be_distributed(self) -> None:
        """CR-812-01: pending package MUST NOT be distributed."""
        broker, _ = make_broker()
        pkg = await broker.submit_package(make_package())
        with pytest.raises(KnowledgeBrokerError, match="not approved"):
            await broker.distribute(package_id=pkg["package_id"])

    @pytest.mark.asyncio
    async def test_approved_package_can_be_distributed(self) -> None:
        """CR-812-01: approved package MAY be distributed."""
        broker, session = make_broker()
        pkg = await broker.submit_package(make_package())
        pkg_id = pkg["package_id"]

        approved = await broker.approve_package(package_id=pkg_id, approver_id="governance-officer")
        assert approved["approval_status"] == "approved"

    @pytest.mark.asyncio
    async def test_rejected_package_cannot_be_distributed(self) -> None:
        """CR-812-01: rejected package MUST NOT be distributed."""
        broker, _ = make_broker()
        pkg = await broker.submit_package(make_package())
        pkg_id = pkg["package_id"]

        await broker.reject_package(package_id=pkg_id, approver_id="governance-officer", reason="Evidence unverifiable")
        with pytest.raises(KnowledgeBrokerError, match="not approved"):
            await broker.distribute(package_id=pkg_id)


class TestEvidenceRequirement:
    @pytest.mark.asyncio
    async def test_item_without_evidence_raises(self) -> None:
        """CR-812-02: knowledge items MUST reference verifiable evidence."""
        broker, _ = make_broker()
        item_no_evidence = make_item(evidence=None)
        with pytest.raises(KnowledgeBrokerError, match="evidence"):
            await broker.submit_package(make_package(items=[item_no_evidence]))

    @pytest.mark.asyncio
    async def test_item_with_empty_evidence_raises(self) -> None:
        """CR-812-02: empty evidence string is not verifiable."""
        broker, _ = make_broker()
        with pytest.raises(KnowledgeBrokerError, match="evidence"):
            await broker.submit_package(make_package(items=[make_item(evidence="")]))


class TestRoleScopedDistribution:
    @pytest.mark.asyncio
    async def test_distribution_checks_role_match(self) -> None:
        """CR-812-03: packages delivered only to matching agent roles."""
        broker, _ = make_broker()
        pkg = await broker.submit_package(make_package(target_roles=["network_observer"]))
        pkg_id = pkg["package_id"]
        await broker.approve_package(package_id=pkg_id, approver_id="officer")

        # role match
        match = broker.role_matches(package_id=pkg_id, agent_role="network_observer")
        assert match is True

        # role mismatch
        no_match = broker.role_matches(package_id=pkg_id, agent_role="decision_engine")
        assert no_match is False


class TestSourceQuality:
    @pytest.mark.asyncio
    async def test_low_quality_source_flagged(self) -> None:
        """CR-812-05: sources with quality < 0.60 MUST be flagged."""
        broker, _ = make_broker()
        broker.update_source_quality(source="noc_manager", quality_score=0.55)
        assert broker.is_source_flagged("noc_manager") is True

    @pytest.mark.asyncio
    async def test_source_unflagged_above_recovery_threshold(self) -> None:
        """CR-812-05: flagged source cleared when quality recovers above 0.70."""
        broker, _ = make_broker()
        broker.update_source_quality(source="noc_manager", quality_score=0.55)
        broker.update_source_quality(source="noc_manager", quality_score=0.72)
        assert broker.is_source_flagged("noc_manager") is False

    @pytest.mark.asyncio
    async def test_flagged_source_package_withheld_without_enhanced_review(self) -> None:
        """CR-812-05: flagged source items withheld from distribution pending enhanced review."""
        broker, _ = make_broker()
        broker.update_source_quality(source="noc_manager", quality_score=0.50)
        pkg = await broker.submit_package(make_package())
        pkg_id = pkg["package_id"]
        await broker.approve_package(package_id=pkg_id, approver_id="officer")

        with pytest.raises(KnowledgeBrokerError, match="flagged source"):
            await broker.distribute(package_id=pkg_id)


class TestNegativeExamples:
    @pytest.mark.asyncio
    async def test_capture_negative_example_from_failed_intent(self) -> None:
        """CR-812-06: negative examples captured from failed intents."""
        broker, _ = make_broker()
        result = await broker.capture_negative_example(
            source=NegativeExampleSource.failed_intent,
            description="apply_qos failed due to missing DSCP mapping",
            evidence="intent-xyz-001",
            agent_roles=["decision_engine"],
        )
        assert result["type"] == "negative_example"
        assert result["source"] == "failed_intent"

    @pytest.mark.asyncio
    async def test_capture_negative_example_from_ethics_violation(self) -> None:
        """CR-812-06: negative examples captured from ethics violations."""
        broker, _ = make_broker()
        result = await broker.capture_negative_example(
            source=NegativeExampleSource.ethics_violation,
            description="ContainmentViolationError raised — missing rollback_plan",
            evidence="audit-record-abc",
            agent_roles=["pipeline"],
        )
        assert result["source"] == "ethics_violation"

    @pytest.mark.asyncio
    async def test_negative_example_requires_approval(self) -> None:
        """CR-812-07: negative examples require same approval process."""
        broker, _ = make_broker()
        result = await broker.capture_negative_example(
            source=NegativeExampleSource.rollback,
            description="Rollback triggered after scale_bandwidth failure",
            evidence="execution-record-456",
            agent_roles=["network_observer"],
        )
        # Captured example creates a pending package
        pkg_id = result["package_id"]
        with pytest.raises(KnowledgeBrokerError, match="not approved"):
            await broker.distribute(package_id=pkg_id)
