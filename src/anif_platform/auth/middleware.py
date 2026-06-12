"""Simple API key authentication — placeholder until B6 X.509 auth.

All endpoints depend on `get_api_key`. In B6 this dependency is replaced
with the full X.509/JWT middleware without changing the endpoint signatures.
"""

from __future__ import annotations

import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key: str | None = Security(_API_KEY_HEADER)) -> str:
    """
    Validate the X-API-Key header against ANIF_API_KEY env var.

    Raises HTTP 401 if the key is missing or incorrect.
    Replace this dependency in B6 with X.509/JWT auth.
    """
    expected = os.environ.get("ANIF_API_KEY", "")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ANIF_API_KEY environment variable is not set",
        )
    if api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return api_key
