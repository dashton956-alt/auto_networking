# tests/unit/test_agent_certificate.py
"""Unit tests for MockCertificateAuthority, CertificateVerifier, RevocationList — ANIF-843."""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from anif_platform.agents.certificate import (
    CertVerificationResult,
    CertificateVerifier,
    MockCertificateAuthority,
    RevocationList,
)
from anif_platform.agents.tier_boundary import TierBoundaryChecker


@pytest.fixture
def ca() -> MockCertificateAuthority:
    return MockCertificateAuthority()


@pytest.fixture
def checker() -> TierBoundaryChecker:
    return TierBoundaryChecker()


def make_capabilities_hash(manifest: dict) -> str:
    return hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()


class TestMockCertificateAuthority:
    def test_ca_cert_pem_is_valid_x509(self, ca: MockCertificateAuthority) -> None:
        from cryptography import x509

        cert = x509.load_pem_x509_certificate(ca.ca_cert_pem.encode())
        assert cert.subject is not None

    def test_issue_cert_returns_pem_and_expiry(self, ca: MockCertificateAuthority) -> None:
        caps_hash = make_capabilities_hash({"caps": ["read"]})
        pem, expires_at = ca.issue_cert(
            agent_id="agent-001",
            agent_type="NetworkObserver",
            tier=1,
            capabilities_hash=caps_hash,
        )
        assert pem.startswith("-----BEGIN CERTIFICATE-----")
        assert expires_at > datetime.now(UTC)

    def test_issued_cert_expires_within_90_days(self, ca: MockCertificateAuthority) -> None:
        """ANIF-843 §4.1: valid_to MUST NOT exceed 90 days from issue."""
        caps_hash = make_capabilities_hash({"caps": ["read"]})
        _, expires_at = ca.issue_cert(
            agent_id="agent-001",
            agent_type="NetworkObserver",
            tier=1,
            capabilities_hash=caps_hash,
        )
        max_expiry = datetime.now(UTC) + timedelta(days=91)
        assert expires_at < max_expiry

    def test_issued_cert_contains_agent_id(self, ca: MockCertificateAuthority) -> None:
        from cryptography import x509
        from cryptography.x509.oid import NameOID

        caps_hash = make_capabilities_hash({"caps": ["read"]})
        pem, _ = ca.issue_cert(
            agent_id="agent-001",
            agent_type="NetworkObserver",
            tier=2,
            capabilities_hash=caps_hash,
        )
        cert = x509.load_pem_x509_certificate(pem.encode())
        cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        assert cn == "agent-001"

    def test_issued_cert_encodes_tier(self, ca: MockCertificateAuthority) -> None:
        from cryptography import x509
        from cryptography.x509.oid import NameOID

        caps_hash = make_capabilities_hash({"caps": ["execute"]})
        pem, _ = ca.issue_cert(
            agent_id="agent-002",
            agent_type="ActionSelector",
            tier=3,
            capabilities_hash=caps_hash,
        )
        cert = x509.load_pem_x509_certificate(pem.encode())
        ou = cert.subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value
        assert ou == "3"


class TestCertificateVerifier:
    def make_verifier(
        self, ca: MockCertificateAuthority, revoked_ids: set[str] | None = None
    ) -> CertificateVerifier:
        revocation_list = MagicMock(spec=RevocationList)
        revocation_list.is_revoked_sync = MagicMock(
            side_effect=lambda agent_id: agent_id in (revoked_ids or set())
        )
        return CertificateVerifier(
            ca_cert_pem=ca.ca_cert_pem,
            revocation_list=revocation_list,
        )

    def test_valid_cert_passes_all_five_steps(
        self, ca: MockCertificateAuthority, checker: TierBoundaryChecker
    ) -> None:
        caps_hash = make_capabilities_hash({"caps": ["execute"]})
        pem, _ = ca.issue_cert(
            agent_id="agent-001",
            agent_type="ActionSelector",
            tier=3,
            capabilities_hash=caps_hash,
        )
        verifier = self.make_verifier(ca)
        result = verifier.verify(
            cert_pem=pem,
            expected_capabilities_hash=caps_hash,
            endpoint_category="execution_api",
            checker=checker,
        )
        assert result.valid is True
        assert result.agent_id == "agent-001"
        assert result.tier == 3

    def test_revoked_cert_fails_step_3(
        self, ca: MockCertificateAuthority, checker: TierBoundaryChecker
    ) -> None:
        caps_hash = make_capabilities_hash({"caps": ["read"]})
        pem, _ = ca.issue_cert(
            agent_id="agent-revoked",
            agent_type="NetworkObserver",
            tier=1,
            capabilities_hash=caps_hash,
        )
        verifier = self.make_verifier(ca, revoked_ids={"agent-revoked"})
        result = verifier.verify(
            cert_pem=pem,
            expected_capabilities_hash=caps_hash,
            endpoint_category="canonical_state_read",
            checker=checker,
        )
        assert result.valid is False
        assert result.failure_reason == "revoked"

    def test_wrong_capabilities_hash_fails_step_4(
        self, ca: MockCertificateAuthority, checker: TierBoundaryChecker
    ) -> None:
        caps_hash = make_capabilities_hash({"caps": ["read"]})
        pem, _ = ca.issue_cert(
            agent_id="agent-001",
            agent_type="NetworkObserver",
            tier=1,
            capabilities_hash=caps_hash,
        )
        verifier = self.make_verifier(ca)
        result = verifier.verify(
            cert_pem=pem,
            expected_capabilities_hash="wrong_hash_value",
            endpoint_category="canonical_state_read",
            checker=checker,
        )
        assert result.valid is False
        assert result.failure_reason == "capabilities_hash_mismatch"

    def test_tier_boundary_violation_fails_step_5(
        self, ca: MockCertificateAuthority, checker: TierBoundaryChecker
    ) -> None:
        caps_hash = make_capabilities_hash({"caps": ["read"]})
        # Tier 1 cert trying to call execution_api (requires Tier 3)
        pem, _ = ca.issue_cert(
            agent_id="agent-001",
            agent_type="NetworkObserver",
            tier=1,
            capabilities_hash=caps_hash,
        )
        verifier = self.make_verifier(ca)
        result = verifier.verify(
            cert_pem=pem,
            expected_capabilities_hash=caps_hash,
            endpoint_category="execution_api",
            checker=checker,
        )
        assert result.valid is False
        assert result.failure_reason == "tier_boundary_violation"


class TestRevocationList:
    @pytest.mark.asyncio
    async def test_revoke_adds_row(self) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        rl = RevocationList(session=session)
        await rl.revoke(agent_id="agent-001", reason="Compromise detected")
        session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_revoked_returns_true_for_revoked_agent(self) -> None:
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()  # row exists
        session.execute = AsyncMock(return_value=mock_result)
        rl = RevocationList(session=session)
        assert await rl.is_revoked("agent-001") is True

    @pytest.mark.asyncio
    async def test_is_revoked_returns_false_for_clean_agent(self) -> None:
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_result)
        rl = RevocationList(session=session)
        assert await rl.is_revoked("agent-clean") is False
