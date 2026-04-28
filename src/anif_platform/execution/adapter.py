"""
NetworkAdapter Protocol and response schemas — ANIF-306 §7.

All adapters MUST implement NetworkAdapter.
The executor calls only this interface, never adapter internals.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from pydantic import BaseModel


class AdapterResponse(BaseModel):
    """Response from any adapter execute or rollback call — ANIF-306 §7.2."""

    success: bool
    adapter_status_code: int
    adapter_message: str
    applied_changes: list[str]
    rollback_reference: str | None


class AdapterHealthStatus(BaseModel):
    """Health status returned by adapter.health_check() — ANIF-306 §7.2."""

    healthy: bool
    adapter_name: str
    last_checked: datetime
    error: str | None


class NetworkAdapter(Protocol):
    """
    Abstract adapter interface — ANIF-306 §7.2.

    Every adapter MUST implement these three methods.
    The executor MUST call only this interface.
    """

    def execute(
        self,
        action_type: str,
        parameters: dict[str, Any],
        execution_id: str,
    ) -> AdapterResponse:
        """Execute an action and return the adapter response."""
        ...

    def rollback(
        self,
        action_type: str,
        rollback_reference: str | None,
        execution_id: str,
    ) -> AdapterResponse:
        """Reverse a previously applied action."""
        ...

    def health_check(self) -> AdapterHealthStatus:
        """Return the current health status of this adapter."""
        ...
