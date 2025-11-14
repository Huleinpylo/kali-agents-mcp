"""FastAPI dependencies shared across routers."""

from functools import lru_cache
from typing import Any

from fastapi import HTTPException, status

try:
    from src.agents.supervisor import create_supervisor_agent
except ImportError:  # pragma: no cover - fallback when supervisor not available
    create_supervisor_agent = None


@lru_cache(maxsize=1)
def get_supervisor() -> Any:
    """Return a singleton supervisor instance or raise 503."""
    if create_supervisor_agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supervisor agent is not available. Ensure the system is installed correctly.",
        )

    supervisor = create_supervisor_agent()
    if supervisor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to initialize supervisor agent.",
        )
    return supervisor
