"""Tests for AuditWriter — ANIF-107 §4.3, §4.7."""

from __future__ import annotations

import hashlib
import json
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.audit.models import AuditRecordRow
from anif_platform.audit.writer import GENESIS_HASH, AuditWriteError, AuditWriter
from anif_platform.schemas.audit_record import AuditOutcome, AuditRecord, AuditStage


def make_record(intent_id: uuid.UUID, stage: AuditStage = AuditStage.validate) -> AuditRecord:
    chain: list = []
    if stage in (AuditStage.decision, AuditStage.governance):
        from anif_platform.schemas.audit_record import ReasoningStep
        chain = [ReasoningStep(step=1, description="x", decision="y")]
    return AuditRecord(
        intent_id=intent_id,
        stage=stage,
        input_summary={"service": "payments"},
        output_summary={"result": "pass"},
        outcome=AuditOutcome.success,
        duration_ms=10,
        reasoning_chain=chain,
    )


@pytest.mark.asyncio
class TestAuditWriter:
    async def test_write_persists_record(self, db_session: AsyncSession) -> None:
        """Write-before-return: record must be durable after write() returns."""
        writer = AuditWriter(db_session)
        intent_id = uuid.uuid4()
        record = make_record(intent_id)

        await writer.write(record)

        result = await db_session.execute(
            select(AuditRecordRow).where(AuditRecordRow.record_id == record.record_id)
        )
        row = result.scalar_one_or_none()
        assert row is not None
        assert row.intent_id == intent_id
        assert row.stage == AuditStage.validate.value
        assert row.outcome == AuditOutcome.success.value

    async def test_write_sets_chain_id_to_intent_id(self, db_session: AsyncSession) -> None:
        """chain_id MUST be intent_id — ANIF-107 §4.7.2."""
        writer = AuditWriter(db_session)
        intent_id = uuid.uuid4()
        record = make_record(intent_id)

        await writer.write(record)

        result = await db_session.execute(
            select(AuditRecordRow).where(AuditRecordRow.record_id == record.record_id)
        )
        row = result.scalar_one()
        assert row.chain_id == intent_id

    async def test_first_record_prev_hash_is_genesis(self, db_session: AsyncSession) -> None:
        """First record in a chain MUST use genesis hash as prev_hash — ANIF-107 §4.7.2."""
        writer = AuditWriter(db_session)
        intent_id = uuid.uuid4()
        record = make_record(intent_id)

        await writer.write(record)

        result = await db_session.execute(
            select(AuditRecordRow).where(AuditRecordRow.record_id == record.record_id)
        )
        row = result.scalar_one()
        assert row.prev_hash == GENESIS_HASH

    async def test_second_record_prev_hash_is_first_record_hash(
        self, db_session: AsyncSession
    ) -> None:
        """Each record's prev_hash MUST be the preceding record's record_hash — ANIF-107 §4.7.2."""
        writer = AuditWriter(db_session)
        intent_id = uuid.uuid4()

        r1 = make_record(intent_id, AuditStage.validate)
        await writer.write(r1)

        r2 = make_record(intent_id, AuditStage.policy)
        await writer.write(r2)

        result = await db_session.execute(
            select(AuditRecordRow).where(AuditRecordRow.record_id == r2.record_id)
        )
        row2 = result.scalar_one()

        result1 = await db_session.execute(
            select(AuditRecordRow).where(AuditRecordRow.record_id == r1.record_id)
        )
        row1 = result1.scalar_one()

        assert row2.prev_hash == row1.record_hash

    async def test_record_hash_is_sha256_of_canonical_json(
        self, db_session: AsyncSession
    ) -> None:
        """record_hash MUST be SHA-256 of canonical JSON excluding hash fields — ANIF-107 §4.7.2."""
        writer = AuditWriter(db_session)
        intent_id = uuid.uuid4()
        record = make_record(intent_id)

        await writer.write(record)

        result = await db_session.execute(
            select(AuditRecordRow).where(AuditRecordRow.record_id == record.record_id)
        )
        row = result.scalar_one()

        # Recompute expected hash from stored data
        data = dict(row.data)
        data.pop("record_hash", None)
        data.pop("prev_hash", None)
        canonical = json.dumps(data, sort_keys=True, default=str)
        expected = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
        assert row.record_hash == expected

    async def test_duplicate_record_id_raises_audit_write_error(
        self, db_session: AsyncSession
    ) -> None:
        """Duplicate record_id MUST be rejected — ANIF-107 §4.2.2."""
        writer = AuditWriter(db_session)
        intent_id = uuid.uuid4()
        record = make_record(intent_id)

        await writer.write(record)

        with pytest.raises(AuditWriteError):
            await writer.write(record)  # same record_id

    async def test_different_intents_have_independent_chains(
        self, db_session: AsyncSession
    ) -> None:
        """Each intent has its own hash chain (chain_id = intent_id)."""
        writer = AuditWriter(db_session)
        intent_a = uuid.uuid4()
        intent_b = uuid.uuid4()

        ra = make_record(intent_a)
        rb = make_record(intent_b)
        await writer.write(ra)
        await writer.write(rb)

        result_a = await db_session.execute(
            select(AuditRecordRow).where(AuditRecordRow.record_id == ra.record_id)
        )
        result_b = await db_session.execute(
            select(AuditRecordRow).where(AuditRecordRow.record_id == rb.record_id)
        )
        row_a = result_a.scalar_one()
        row_b = result_b.scalar_one()

        # Both should have genesis as prev_hash (first records in their chains)
        assert row_a.prev_hash == GENESIS_HASH
        assert row_b.prev_hash == GENESIS_HASH
        assert row_a.chain_id != row_b.chain_id
