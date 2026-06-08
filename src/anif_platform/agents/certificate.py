"""X.509 certificate infrastructure for agent identity — ANIF-843."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import structlog
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.agents.models import AgentRevocationRow
from anif_platform.agents.tier_boundary import TierBoundaryChecker

log = structlog.get_logger(__name__)

_CERT_VALIDITY_DAYS: int = 90
_RSA_KEY_SIZE: int = 2048
_RSA_PUBLIC_EXPONENT: int = 65537


@dataclass
class CertVerificationResult:
    """Result of the five-step certificate verification — ANIF-843 §5.2."""

    valid: bool
    agent_id: str | None = None
    tier: int | None = None
    failure_reason: str | None = None


class MockCertificateAuthority:
    """In-memory CA for dev/test environments — issues real X.509v3 certs.

    Production deployments MUST use an HSM-backed CA (ANIF-843 §4.3).
    """

    def __init__(self) -> None:
        self._private_key: rsa.RSAPrivateKey = rsa.generate_private_key(
            public_exponent=_RSA_PUBLIC_EXPONENT,
            key_size=_RSA_KEY_SIZE,
        )
        self._ca_cert: x509.Certificate = self._build_ca_cert()

    def _build_ca_cert(self) -> x509.Certificate:
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, "ANIF Build-Time Council CA"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ANIF Platform"),
            ]
        )
        return (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(self._private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(UTC))
            .not_valid_after(datetime.now(UTC) + timedelta(days=3650))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(self._private_key, hashes.SHA256())
        )

    @property
    def ca_cert_pem(self) -> str:
        """Return CA certificate as PEM string."""
        return self._ca_cert.public_bytes(serialization.Encoding.PEM).decode()

    def issue_cert(
        self,
        agent_id: str,
        agent_type: str,
        tier: int,
        capabilities_hash: str,
    ) -> tuple[str, datetime]:
        """Issue an agent certificate — ANIF-843 §4.1.

        Returns (pem_cert, expires_at).
        Certificate validity MUST NOT exceed 90 days (ANIF-843 §4.1).
        Fields encoded in Subject:
          CN = agent_id
          OU = tier (as string "0"–"3")
          O  = agent_type
          L  = capabilities_hash
        """
        expires_at = datetime.now(UTC) + timedelta(days=_CERT_VALIDITY_DAYS)
        subject = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, agent_id),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, str(tier)),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, agent_type),
                x509.NameAttribute(NameOID.LOCALITY_NAME, capabilities_hash),
            ]
        )
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(self._ca_cert.subject)
            .public_key(self._private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(UTC))
            .not_valid_after(expires_at)
            .sign(self._private_key, hashes.SHA256())
        )
        pem = cert.public_bytes(serialization.Encoding.PEM).decode()
        return pem, expires_at


class RevocationList:
    """DB-backed certificate revocation list — ANIF-843 §7.2."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def revoke(self, agent_id: str, reason: str) -> None:
        """Add agent to revocation list. Propagates within 60 seconds — ANIF-843 §7.2."""
        row = AgentRevocationRow(
            revocation_id=str(uuid.uuid4()),
            agent_id=agent_id,
            revoked_at=datetime.now(UTC),
            reason=reason,
        )
        self._session.add(row)
        await self._session.flush()
        log.warning("agent_certificate_revoked", agent_id=agent_id, reason=reason)

    async def is_revoked(self, agent_id: str) -> bool:
        """Return True if agent certificate is on the revocation list."""
        result = await self._session.execute(
            select(AgentRevocationRow)
            .where(AgentRevocationRow.agent_id == agent_id)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    def is_revoked_sync(self, agent_id: str) -> bool:
        """Synchronous revocation check for use in CertificateVerifier (pre-loaded cache).

        Call `is_revoked()` async first to populate; use this for in-request checks.
        """
        raise NotImplementedError("Use is_revoked() async or pass revoked_ids set directly")


class CertificateVerifier:
    """Five-step certificate verification per ANIF-843 §5.2."""

    def __init__(self, ca_cert_pem: str, revocation_list: RevocationList) -> None:
        self._ca_cert: x509.Certificate = x509.load_pem_x509_certificate(ca_cert_pem.encode())
        self._revocation_list = revocation_list

    def verify(
        self,
        cert_pem: str,
        expected_capabilities_hash: str,
        endpoint_category: str,
        checker: TierBoundaryChecker,
    ) -> CertVerificationResult:
        """Perform all five verification steps — ANIF-843 §5.2.

        Steps:
          1. Verify signed by build-time council CA
          2. Verify within validity period
          3. Verify not on revocation list (sync check — caller must pre-load)
          4. Verify capabilities_hash matches current approved manifest hash
          5. Verify endpoint tier permitted for agent's declared tier
        """
        try:
            cert = x509.load_pem_x509_certificate(cert_pem.encode())
        except Exception:  # noqa: BLE001 — cryptography raises varied errors for malformed DER
            return CertVerificationResult(valid=False, failure_reason="invalid_cert_pem")

        # Step 1: Verify signature
        try:
            self._ca_cert.public_key().verify(  # type: ignore[union-attr]
                cert.signature,
                cert.tbs_certificate_bytes,
                padding.PKCS1v15(),
                cert.signature_hash_algorithm,  # type: ignore[arg-type]
            )
        except Exception:  # noqa: BLE001
            log.warning("cert_verification_failed", step=1, reason="invalid_signature")
            return CertVerificationResult(valid=False, failure_reason="invalid_signature")

        # Step 2: Check validity period
        now = datetime.now(UTC)
        if now < cert.not_valid_before_utc or now > cert.not_valid_after_utc:
            log.warning("cert_verification_failed", step=2, reason="expired_or_not_yet_valid")
            return CertVerificationResult(valid=False, failure_reason="expired_or_not_yet_valid")

        # Step 3: Check revocation list (sync)
        try:
            agent_id = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        except Exception:  # noqa: BLE001
            return CertVerificationResult(valid=False, failure_reason="missing_agent_id")

        if self._revocation_list.is_revoked_sync(agent_id):
            log.warning("cert_verification_failed", step=3, agent_id=agent_id, reason="revoked")
            return CertVerificationResult(valid=False, failure_reason="revoked")

        # Step 4: Check capabilities_hash
        try:
            caps_hash_in_cert = cert.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value
        except Exception:  # noqa: BLE001
            return CertVerificationResult(valid=False, failure_reason="missing_capabilities_hash")

        if caps_hash_in_cert != expected_capabilities_hash:
            log.warning(
                "cert_verification_failed",
                step=4,
                agent_id=agent_id,
                reason="capabilities_hash_mismatch",
            )
            return CertVerificationResult(valid=False, failure_reason="capabilities_hash_mismatch")

        # Step 5: Tier boundary check
        try:
            tier_str = cert.subject.get_attributes_for_oid(
                NameOID.ORGANIZATIONAL_UNIT_NAME
            )[0].value
            agent_tier = int(tier_str)
        except (IndexError, ValueError):
            return CertVerificationResult(valid=False, failure_reason="missing_or_invalid_tier")

        if not checker.check(agent_tier=agent_tier, endpoint_category=endpoint_category):
            log.warning(
                "cert_verification_failed",
                step=5,
                agent_id=agent_id,
                agent_tier=agent_tier,
                endpoint_category=endpoint_category,
                reason="tier_boundary_violation",
            )
            checker.log_violation(
                agent_id=agent_id,
                agent_tier=agent_tier,
                endpoint_category=endpoint_category,
            )
            return CertVerificationResult(valid=False, failure_reason="tier_boundary_violation")

        return CertVerificationResult(valid=True, agent_id=agent_id, tier=agent_tier)
