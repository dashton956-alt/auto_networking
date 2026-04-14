"""
GitWatcher — detects new intents committed to Git.

Supports polling and webhook modes. Controlled by:
  GIT_WATCHER_MODE=polling|webhook|both
  GIT_WATCHER_POLL_INTERVAL=60  (seconds)
  GIT_REPO_URL=https://github.com/org/intents
  GIT_INTENTS_PATH=intents/
  GIT_ACCESS_TOKEN=ghp_xxxxx
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx
import yaml

from anif_platform.intent.registry import IntentRegistry
from anif_platform.intent.schemas import GitIntentRef
from anif_platform.intent.validator import IntentValidator
from anif_platform.schemas.intent import Intent

log = logging.getLogger(__name__)


class GitWatcher:
    """
    Watches a Git repository for new intent YAML files.

    On detection: fetches file, validates, registers in DB.
    """

    def __init__(self, registry: IntentRegistry) -> None:
        self._registry = registry
        self._validator = IntentValidator()
        self._last_commit: str | None = None
        self._repo_url = os.environ.get("GIT_REPO_URL", "")
        self._intents_path = os.environ.get("GIT_INTENTS_PATH", "intents/")
        self._token = os.environ.get("GIT_ACCESS_TOKEN", "")
        self._poll_interval = int(os.environ.get("GIT_WATCHER_POLL_INTERVAL", "60"))
        self._mode = os.environ.get("GIT_WATCHER_MODE", "polling")

    async def start(self) -> None:
        """Start the watcher. Runs polling loop if mode includes polling."""
        if self._mode in ("polling", "both"):
            asyncio.create_task(self._poll_loop())

    async def _poll_loop(self) -> None:
        """Poll the Git repo for new commits on an interval."""
        while True:
            try:
                await self._check_for_new_intents()
            except Exception as exc:
                log.error("git_watcher_poll_error", extra={"error": str(exc)})
            await asyncio.sleep(self._poll_interval)

    async def _check_for_new_intents(self) -> None:
        """Fetch latest commit SHA and process any new intent files."""
        if not self._repo_url:
            return

        latest_sha = await self._get_latest_commit_sha()
        if latest_sha == self._last_commit:
            return

        files = await self._list_intent_files(latest_sha)
        for file_path in files:
            await self._process_intent_file(file_path, latest_sha)

        self._last_commit = latest_sha

    async def _get_latest_commit_sha(self) -> str:
        """Fetch the latest commit SHA from the Git API (GitHub format)."""
        # Converts https://github.com/org/repo → api.github.com/repos/org/repo/commits
        api_url = self._repo_url.replace(
            "https://github.com/", "https://api.github.com/repos/"
        ) + "/commits"
        headers = {"Accept": "application/vnd.github+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(api_url, headers=headers, params={"per_page": 1})
            resp.raise_for_status()
            data = resp.json()
            return str(data[0]["sha"])

    async def _list_intent_files(self, commit_sha: str) -> list[str]:
        """List all .yml files in the intents path at the given commit."""
        api_url = self._repo_url.replace(
            "https://github.com/", "https://api.github.com/repos/"
        ) + f"/contents/{self._intents_path}"
        headers = {"Accept": "application/vnd.github+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(api_url, headers=headers, params={"ref": commit_sha})
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            return [
                f["path"] for f in resp.json()
                if f["name"].endswith(".yml") or f["name"].endswith(".yaml")
            ]

    async def _process_intent_file(self, file_path: str, commit_sha: str) -> None:
        """Fetch, parse, validate, and register one intent file."""
        raw_url = self._repo_url.replace(
            "https://github.com/", "https://raw.githubusercontent.com/"
        ) + f"/{commit_sha}/{file_path}"
        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(raw_url, headers=headers)
            resp.raise_for_status()
            raw_yaml = resp.text

        try:
            data = yaml.safe_load(raw_yaml)
            intent = Intent(**data)
        except Exception as exc:
            log.warning("git_watcher_parse_error", extra={"file": file_path, "error": str(exc)})
            return

        result = self._validator.validate(intent)
        if not result.intent_id:
            log.warning(
                "git_watcher_validation_failed",
                extra={"file": file_path, "errors": result.errors},
            )
            return

        git_ref = GitIntentRef(
            repo_url=self._repo_url,
            path=file_path,
            commit_sha=commit_sha,
        )
        await self._registry.register(result, git_ref)
        log.info(
            "git_watcher_intent_registered",
            extra={
                "intent_id": str(result.intent_id),
                "file": file_path,
                "commit_sha": commit_sha,
            },
        )

    async def handle_webhook(self, payload: dict[str, Any]) -> None:
        """
        Process a push webhook payload (GitHub/GitLab format).

        Called from POST /webhooks/git endpoint when GIT_WATCHER_MODE
        includes 'webhook'.
        """
        # GitHub push event: payload["after"] = new commit SHA
        commit_sha = payload.get("after") or payload.get("checkout_sha", "")
        if not commit_sha or commit_sha == "0000000000000000000000000000000000000000":
            return  # Branch deletion — nothing to process

        files = await self._list_intent_files(commit_sha)
        for file_path in files:
            await self._process_intent_file(file_path, commit_sha)
