"""
Background ticket expiry task — ANIF-406 §4.4.3.

Runs every 60 seconds; transitions overdue pending tickets to expired.
Started in the FastAPI lifespan.
"""

from __future__ import annotations

import asyncio

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from anif_platform.audit.writer import AuditWriter
from anif_platform.human_loop.queue import ApprovalQueue
from anif_platform.monitoring.metrics import TICKET_EXPIRED

log = structlog.get_logger(__name__)

_EXPIRY_INTERVAL_SECONDS = 60  # ANIF-406 §4.4.3: MUST run at least every 60 seconds


async def expiry_loop(session_factory: async_sessionmaker[AsyncSession]) -> None:
    """Infinite loop: check for overdue tickets every 60 seconds."""
    while True:
        await asyncio.sleep(_EXPIRY_INTERVAL_SECONDS)
        try:
            async with session_factory() as session:
                writer = AuditWriter(session)
                queue = ApprovalQueue(session=session, writer=writer)
                expired = await queue.expire_pending()
                await session.commit()
                if expired:
                    log.info(
                        "tickets_expired_by_background_task",
                        count=len(expired),
                        ticket_ids=expired,
                    )
                    for _ in expired:
                        TICKET_EXPIRED.labels(environment="unknown").inc()
        except Exception:
            log.exception("expiry_loop_error")
