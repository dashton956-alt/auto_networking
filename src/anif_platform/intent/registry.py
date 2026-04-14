"""IntentRegistry — persists and retrieves validated intents."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from anif_platform.intent.models import IntentRow
from anif_platform.intent.schemas import GitIntentRef, ValidatedIntent, ValidationResult


class IntentRegistry:
    """Stores and retrieves validated intent records."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def register(
        self,
        result: ValidationResult,
        git_ref: Optional[GitIntentRef] = None,
    ) -> ValidatedIntent:
        """
        Persist a validated intent.

        result.intent_id MUST be set (call only after successful validation).
        Returns the registered ValidatedIntent.
        """
        assert result.intent_id is not None
        assert result.validated_intent is not None

        change_number = await self._next_change_number()

        row = IntentRow(
            intent_id=result.intent_id,
            change_number=change_number,
            version="0.1.0",
            service=result.validated_intent["service"],
            status="validated",
            git_repo_url=git_ref.repo_url if git_ref else None,
            git_path=git_ref.path if git_ref else None,
            git_commit_sha=git_ref.commit_sha if git_ref else None,
            resolved_intent=result.validated_intent,
            warnings=result.warnings,
            created_at=datetime.now(UTC),
        )
        self._session.add(row)
        await self._session.flush()

        return self._row_to_schema(row, git_ref)

    async def get(self, intent_id: UUID) -> Optional[ValidatedIntent]:
        """Return a registered intent by ID, or None if not found."""
        result = await self._session.execute(
            select(IntentRow).where(IntentRow.intent_id == intent_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        git_ref = None
        if row.git_repo_url:
            git_ref = GitIntentRef(
                repo_url=row.git_repo_url,
                path=row.git_path or "",
                commit_sha=row.git_commit_sha or "",
            )
        return self._row_to_schema(row, git_ref)

    async def _next_change_number(self) -> int:
        result = await self._session.execute(select(func.max(IntentRow.change_number)))
        current_max = result.scalar_one_or_none()
        return (current_max or 0) + 1

    @staticmethod
    def _row_to_schema(
        row: IntentRow, git_ref: Optional[GitIntentRef]
    ) -> ValidatedIntent:
        return ValidatedIntent(
            intent_id=row.intent_id,
            change_number=row.change_number,
            version=row.version,
            service=row.service,
            status=row.status,
            git_ref=git_ref,
            resolved_intent=row.resolved_intent,
            warnings=row.warnings,
            created_at=row.created_at,
        )
