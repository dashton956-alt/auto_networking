"""
AuditWriter — write-before-return audit persistence with SHA-256 hash chaining.

ANIF-107 §4.3 (write-before-return), §4.7 (hash chaining).
ANIF-724 §5 (ethics write-before-return extension).
"""

from __future__ import annotations

import hashlib
import json
import uuid

from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.audit.models import AuditRecordRow
from anif_platform.schemas.audit_record import AuditRecord

log = structlog.get_logger(__name__)

# SHA-256 of the well-known genesis value for the first record in any chain.
# (ANIF-107 §4.7.2)
GENESIS_HASH: str = "sha256:" + hashlib.sha256(b"ANIF-GENESIS").hexdigest()


class AuditWriteError(Exception):
    """
    Raised when the audit write fails.

    Per ANIF-107 §4.3.3, if the audit write fails the pipeline stage MUST NOT
    proceed and MUST return failure to the caller.
    """


def _canonical_json(data: dict[str, Any]) -> str:
    """Return the canonical JSON representation of a record for hashing.

    Excludes `record_hash` and `prev_hash` fields as required by ANIF-107 §4.7.2.
    Uses sort_keys=True for determinism.
    """
    clean = {k: v for k, v in data.items() if k not in ("record_hash", "prev_hash")}
    return json.dumps(clean, sort_keys=True, default=str)


def _compute_record_hash(data: dict[str, Any]) -> str:
    """Compute SHA-256 hash of canonical record data — ANIF-107 §4.7.2."""
    return "sha256:" + hashlib.sha256(_canonical_json(data).encode()).hexdigest()


class AuditWriter:
    """
    Writes audit records to the audit store with write-before-return semantics.

    One AuditWriter instance per request/session. Inject via FastAPI dependency.

    Usage:
        writer = AuditWriter(session)
        await writer.write(record)  # raises AuditWriteError on failure
        # caller MUST NOT proceed past this point if AuditWriteError is raised
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def write(self, record: AuditRecord) -> None:
        """
        Durably write an audit record to the audit store.

        This method MUST be called — and MUST complete successfully — before
        the calling pipeline stage returns its result (ANIF-107 §4.3.1).

        Raises:
            AuditWriteError: if the write fails for any reason.
                The caller MUST propagate this as a failure response.
        """
        prev_hash = await self._get_prev_hash(record.intent_id)
        data = self._record_to_dict(record, prev_hash)
        record_hash = _compute_record_hash(data)
        data["record_hash"] = record_hash
        data["prev_hash"] = prev_hash

        row = AuditRecordRow(
            record_id=record.record_id,
            intent_id=record.intent_id,
            timestamp=record.timestamp,
            stage=record.stage.value,
            outcome=record.outcome.value,
            operator_id=record.operator_id,
            record_hash=record_hash,
            prev_hash=prev_hash,
            chain_id=record.intent_id,
            duration_ms=record.duration_ms,
            data=data,
        )

        self._session.add(row)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            await self._session.rollback()
            log.error(
                "audit_write_failed",
                record_id=str(record.record_id),
                intent_id=str(record.intent_id),
                stage=record.stage.value,
                error=str(exc),
            )
            raise AuditWriteError(
                f"Failed to write audit record {record.record_id}: {exc}"
            ) from exc

        log.info(
            "audit_record_written",
            record_id=str(record.record_id),
            intent_id=str(record.intent_id),
            stage=record.stage.value,
            outcome=record.outcome.value,
        )

    async def _get_prev_hash(self, intent_id: uuid.UUID) -> str:
        """
        Retrieve the record_hash of the most recent record in this intent's chain.

        Returns GENESIS_HASH if this is the first record for this intent.
        """
        result = await self._session.execute(
            select(AuditRecordRow.record_hash)
            .where(AuditRecordRow.chain_id == intent_id)
            .order_by(AuditRecordRow.timestamp.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return row if row is not None else GENESIS_HASH

    @staticmethod
    def _record_to_dict(record: AuditRecord, prev_hash: str) -> dict[str, Any]:
        """
        Serialise AuditRecord to a dict suitable for JSONB storage.

        Excludes hash chain fields from the record itself — they are computed
        and injected by the writer.
        """
        data = record.model_dump(mode="json", exclude={"record_hash", "prev_hash", "chain_id"})
        return data
