"""
AuditQueryService — read-side audit queries.

Implements the query interface required by ANIF-107 §4.5 and the hash chain
verification endpoint required by §4.7.3.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.audit.models import AuditRecordRow
from anif_platform.audit.writer import GENESIS_HASH, _canonical_json

_MAX_PAGE_SIZE = 1000
_DEFAULT_PAGE_SIZE = 50


class AuditQueryService:
    """
    Read-side audit queries.

    Inject per-request via FastAPI dependency injection.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_intent(self, intent_id: uuid.UUID) -> list[dict[str, Any]]:
        """
        Return all audit records for the given intent, ordered by timestamp ascending.

        Returns an empty list (not an error) if no records exist — ANIF-107 §4.5.3.
        """
        result = await self._session.execute(
            select(AuditRecordRow)
            .where(AuditRecordRow.intent_id == intent_id)
            .order_by(AuditRecordRow.timestamp.asc())
        )
        rows = result.scalars().all()
        return [row.data for row in rows]

    async def get_why(self, intent_id: uuid.UUID) -> str:
        """
        Synthesise a human-readable explanation of the pipeline decision — ANIF-107 §4.5.6.

        Must include: action proposed, policies evaluated, risk score, governance mode,
        and final outcome.
        """
        records = await self.get_by_intent(intent_id)
        if not records:
            return f"No audit records found for intent {intent_id}."

        lines: list[str] = [f"Intent {intent_id} — pipeline summary\n"]

        for rec in records:
            stage = rec.get("stage", "unknown")
            outcome = rec.get("outcome", "unknown")
            lines.append(f"Stage: {stage} → {outcome}")

            chain = rec.get("reasoning_chain", [])
            for step in chain:
                if isinstance(step, dict):
                    desc = step.get("description", "")
                    decision = step.get("decision", "")
                    rationale = step.get("rationale", "")
                    entry = f"  • {desc}: {decision}"
                    if rationale:
                        entry += f" ({rationale})"
                    lines.append(entry)
                else:
                    lines.append(f"  • {step}")

        return "\n".join(lines)

    async def list_records(
        self,
        stage: str | None = None,
        outcome: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        operator_id: str | None = None,
        action_type: str | None = None,
        environment: str | None = None,
        limit: int = _DEFAULT_PAGE_SIZE,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Return audit records with optional filters and pagination — ANIF-107 §4.5.2.

        Default page size: 50. Maximum page size: 1000.
        """
        effective_limit = min(limit, _MAX_PAGE_SIZE)

        query = select(AuditRecordRow).order_by(AuditRecordRow.timestamp.desc())

        if stage is not None:
            query = query.where(AuditRecordRow.stage == stage)
        if outcome is not None:
            query = query.where(AuditRecordRow.outcome == outcome)
        if date_from is not None:
            query = query.where(AuditRecordRow.timestamp >= date_from)
        if date_to is not None:
            query = query.where(AuditRecordRow.timestamp <= date_to)
        if operator_id is not None:
            query = query.where(AuditRecordRow.operator_id == operator_id)
        if action_type is not None:
            query = query.where(AuditRecordRow.data["action_type"].astext == action_type)
        if environment is not None:
            query = query.where(AuditRecordRow.data["input_summary"]["environment"].astext == environment)

        query = query.limit(effective_limit).offset(offset)

        result = await self._session.execute(query)
        rows = result.scalars().all()
        return [row.data for row in rows]

    async def verify_chain(self, intent_id: uuid.UUID) -> dict[str, Any]:
        """
        Recompute hash chain and return verification result — ANIF-107 §4.7.3.

        Returns: {"valid": bool, "broken_at": record_id or null, "record_count": int}
        """
        result = await self._session.execute(
            select(AuditRecordRow)
            .where(AuditRecordRow.chain_id == intent_id)
            .order_by(AuditRecordRow.timestamp.asc())
        )
        rows = result.scalars().all()

        if not rows:
            return {"valid": True, "broken_at": None, "record_count": 0}

        expected_prev = GENESIS_HASH
        for row in rows:
            if row.prev_hash != expected_prev:
                return {
                    "valid": False,
                    "broken_at": str(row.record_id),
                    "record_count": len(rows),
                }
            recomputed = "sha256:" + hashlib.sha256(
                _canonical_json(row.data).encode()
            ).hexdigest()
            if row.record_hash != recomputed:
                return {
                    "valid": False,
                    "broken_at": str(row.record_id),
                    "record_count": len(rows),
                }
            expected_prev = row.record_hash

        return {"valid": True, "broken_at": None, "record_count": len(rows)}
