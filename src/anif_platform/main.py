"""FastAPI application entry point for the ANIF platform."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from anif_platform.audit.router import router as audit_router
from anif_platform.database import engine

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    log.info("anif_platform_starting")
    yield
    await engine.dispose()
    log.info("anif_platform_stopped")


app = FastAPI(
    title="ANIF Platform",
    description="Autonomous Networking & Infrastructure Framework — reference platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(audit_router)
