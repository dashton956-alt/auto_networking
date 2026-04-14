"""Shared pytest fixtures for the ANIF platform test suite."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool


def _test_db_url() -> str:
    url = os.environ.get("DATABASE_URL", "postgresql://anif:anif_dev@localhost:5432/anif_test")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set environment variables for all tests."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv(
        "DATABASE_URL",
        os.environ.get("DATABASE_URL", "postgresql://anif:anif_dev@localhost:5432/anif_test"),
    )
    monkeypatch.setenv(
        "REDIS_URL",
        os.environ.get("REDIS_URL", "redis://localhost:6379"),
    )


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[Any, None]:
    """
    Provide a transactional database session that rolls back after each test.

    Uses NullPool (no connection pooling) to avoid async pool cleanup issues
    across tests. Uses a nested savepoint transaction for test isolation.
    """
    engine = create_async_engine(_test_db_url(), poolclass=NullPool)

    async with engine.connect() as conn:
        await conn.begin()
        session = AsyncSession(bind=conn, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            await session.close()
            await conn.rollback()

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: Any) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client wired to the FastAPI app with a test DB session."""
    from anif_platform.audit.query import AuditQueryService
    from anif_platform.audit.router import get_audit_query_service
    from anif_platform.main import app

    app.dependency_overrides[get_audit_query_service] = lambda: AuditQueryService(db_session)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()
