"""Shared pytest fixtures for the ANIF platform test suite."""

import os

import pytest


# ── Environment ───────────────────────────────────────────────────────────────

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


# ── Placeholder fixtures (uncomment when modules exist) ───────────────────────

# @pytest_asyncio.fixture
# async def db_session() -> AsyncGenerator:
#     """Provide a transactional database session that rolls back after each test."""
#     from anif_platform.database import async_session_factory
#     async with async_session_factory() as session:
#         async with session.begin():
#             yield session
#             await session.rollback()


# @pytest_asyncio.fixture
# async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
#     """Provide an async test client wired to the FastAPI app."""
#     from anif_platform.main import app
#     async with AsyncClient(app=app, base_url="http://test") as c:
#         yield c
