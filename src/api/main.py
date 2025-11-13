"""FastAPI application entrypoint."""

from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from src.api.routers import network, web

app = FastAPI(
    title="Kali Agents MCP API",
    description=(
        "REST interface for the Kali Agents multi-agent system. "
        "Supports network reconnaissance, web application testing, and future MCP workflows."
    ),
    version="0.1.0",
    contact={"name": "Kali Agents Team", "url": "https://github.com/Huleinpylo/kali-agents-mcp"},
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(network.router)
app.include_router(web.router)


@lru_cache(maxsize=1)
def _secure_openapi_schema():
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema.setdefault("components", {}).setdefault("securitySchemes", {})["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "API Key",
        "description": "Set `Authorization: Bearer <KALI_AGENTS_API_KEY>`.",
    }
    return schema


@app.get("/health", tags=["health"])
async def health_check():
    """Basic readiness probe."""
    return {"status": "ok"}


@app.get("/", tags=["meta"])
async def root():
    """Simple welcome route."""
    return {
        "message": "Kali Agents MCP API is live.",
        "docs": "/docs",
        "health": "/health",
    }


@app.on_event("startup")
async def register_openapi_override():
    """Attach custom OpenAPI schema once the app starts."""
    app.openapi_schema = _secure_openapi_schema()
