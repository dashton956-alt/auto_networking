"""FastAPI application — ANIF Platform."""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import APIRouter, Depends, FastAPI, Request

from anif_platform.audit.query import AuditQueryService
from anif_platform.audit.router import get_audit_query_service
from anif_platform.audit.router import router as audit_router
from anif_platform.audit.writer import AuditWriter
from anif_platform.auth import get_api_key
from anif_platform.database import async_session_factory, engine
from anif_platform.governance.router import get_approval_queue as gov_get_queue
from anif_platform.governance.router import get_audit_writer as gov_get_writer
from anif_platform.governance.router import router as governance_router
from anif_platform.human_loop.expiry import expiry_loop
from anif_platform.human_loop.queue import ApprovalQueue
from anif_platform.human_loop.router import get_audit_writer as halt_get_writer
from anif_platform.human_loop.router import router as human_loop_router
from anif_platform.intent.git_watcher import GitWatcher
from anif_platform.intent.registry import IntentRegistry
from anif_platform.intent.router import get_audit_writer as intent_get_writer
from anif_platform.intent.router import get_intent_registry as intent_get_registry
from anif_platform.intent.router import router as intent_router
from anif_platform.pipeline.router import get_approval_queue as pipeline_get_queue
from anif_platform.pipeline.router import get_audit_writer as pipeline_get_writer
from anif_platform.pipeline.router import get_intent_registry as pipeline_get_registry
from anif_platform.pipeline.router import get_policy_engine as pipeline_get_engine
from anif_platform.pipeline.router import router as pipeline_router
from anif_platform.policy.engine import PolicyEngine
from anif_platform.policy.loader import PolicyLoader
from anif_platform.policy.router import get_audit_writer as policy_get_writer
from anif_platform.policy.router import get_intent_registry as policy_get_registry
from anif_platform.policy.router import get_policy_engine as policy_get_engine
from anif_platform.policy.router import router as policy_router

log = structlog.get_logger(__name__)

# Module-level singletons are acceptable here as this is the app entry point.
# All other modules use dependency injection.
_policy_engine: PolicyEngine | None = None


def _get_policy_engine() -> PolicyEngine:
    global _policy_engine
    if _policy_engine is None:
        policies_dir = os.environ.get("POLICIES_DIR", "policies")
        _policy_engine = PolicyEngine(PolicyLoader(policies_dir))
    return _policy_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    log.info("anif_platform_starting")

    # Start GitWatcher if configured
    mode = os.environ.get("GIT_WATCHER_MODE", "")
    if mode:
        async with async_session_factory() as session:
            registry = IntentRegistry(session)
            watcher = GitWatcher(registry)
            await watcher.start()
            log.info("git_watcher_started", mode=mode)

    expiry_task = asyncio.create_task(expiry_loop(async_session_factory))
    log.info("ticket_expiry_task_started")

    yield

    expiry_task.cancel()
    await engine.dispose()
    log.info("anif_platform_stopped")


app = FastAPI(
    title="ANIF Platform",
    description="Autonomous Networking & Infrastructure Framework",
    version="0.1.0",
    lifespan=lifespan,
)


# ── Per-request dependency factories ─────────────────────────────────────


async def _get_session_writer(request: Request) -> AsyncGenerator[AuditWriter, None]:
    async with async_session_factory() as session:
        yield AuditWriter(session)  # type: ignore[misc]


async def _get_session_registry(request: Request) -> AsyncGenerator[IntentRegistry, None]:
    async with async_session_factory() as session:
        yield IntentRegistry(session)  # type: ignore[misc]


async def _get_session_query(request: Request) -> AsyncGenerator[AuditQueryService, None]:
    async with async_session_factory() as session:
        yield AuditQueryService(session)  # type: ignore[misc]


async def _get_session_approval_queue(request: Request) -> AsyncGenerator[ApprovalQueue, None]:
    async with async_session_factory() as session:
        writer = AuditWriter(session)
        yield ApprovalQueue(session=session, writer=writer)


# ── Dependency overrides ──────────────────────────────────────────────────

app.dependency_overrides[get_audit_query_service] = _get_session_query
app.dependency_overrides[intent_get_writer] = _get_session_writer
app.dependency_overrides[intent_get_registry] = _get_session_registry
app.dependency_overrides[policy_get_writer] = _get_session_writer
app.dependency_overrides[policy_get_registry] = _get_session_registry
app.dependency_overrides[policy_get_engine] = _get_policy_engine
app.dependency_overrides[pipeline_get_writer] = _get_session_writer
app.dependency_overrides[pipeline_get_registry] = _get_session_registry
app.dependency_overrides[pipeline_get_engine] = _get_policy_engine
app.dependency_overrides[gov_get_writer] = _get_session_writer
app.dependency_overrides[gov_get_queue] = _get_session_approval_queue
app.dependency_overrides[halt_get_writer] = _get_session_writer
app.dependency_overrides[pipeline_get_queue] = _get_session_approval_queue


# ── Webhook endpoint (when GIT_WATCHER_MODE includes webhook) ────────────

webhook_router = APIRouter(tags=["webhooks"])


@webhook_router.post("/webhooks/git")
async def git_webhook(
    request: Request,
    _: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Receive Git push webhooks and trigger intent detection."""
    payload = await request.json()
    async with async_session_factory() as session:
        registry = IntentRegistry(session)
        watcher = GitWatcher(registry)
        await watcher.handle_webhook(payload)
    return {"status": "accepted"}


# ── Mount routers ─────────────────────────────────────────────────────────

app.include_router(audit_router)
app.include_router(intent_router)
app.include_router(policy_router)
app.include_router(pipeline_router)
app.include_router(webhook_router)
app.include_router(governance_router)
app.include_router(human_loop_router)
