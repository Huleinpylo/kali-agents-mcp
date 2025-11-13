"""FastAPI surface for Kali Agents MCP."""

from .main import app  # re-export for `uvicorn src.api.main:app`

__all__ = ["app"]
