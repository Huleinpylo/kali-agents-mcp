"""API key security helpers."""

import os
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY_ENV_VAR = "KALI_AGENTS_API_KEY"
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def _extract_token(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return value.replace("Bearer ", "").strip()


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """Validate Bearer token against environment configuration."""
    expected = os.getenv(API_KEY_ENV_VAR)

    token = _extract_token(api_key)
    if expected:
        if token is None or token != expected:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key.",
            )
    return token
