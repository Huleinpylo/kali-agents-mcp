"""Web scanning endpoints."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.api.dependencies import get_supervisor
from src.api.security import verify_api_key

router = APIRouter(prefix="/web", tags=["web"])


class WebScanRequest(BaseModel):
    """Input payload for web assessments."""

    url: HttpUrl = Field(..., description="Target URL to assess.")
    deep_scan: bool = Field(default=False, description="Enable deep crawling/fuzzing.")
    wordlist: str = Field(default="common", description="Wordlist name for directory brute forcing.")
    verbose: bool = Field(default=False, description="Return verbose agent output.")
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extra parameters forwarded to the supervisor/web agent.",
    )


class WebStepResult(BaseModel):
    """Normalized step output for web scans."""

    model_config = ConfigDict(extra="allow")

    step: Optional[int] = Field(default=None, description="Execution step number.")
    name: Optional[str] = Field(default=None, description="Step description.")
    status: Optional[str] = Field(default=None, description="Agent status.")
    execution_time: Optional[float] = Field(default=None, description="Duration in seconds.")
    findings: Optional[List[Dict[str, Any]]] = Field(default=None, description="Findings list.")


class WebScanResponse(BaseModel):
    """Response model for web assessments."""

    scan_id: str = Field(..., description="Supervisor task identifier.")
    url: HttpUrl = Field(..., description="URL that was assessed.")
    status: str = Field(..., description="Overall task status.")
    elapsed_seconds: float = Field(..., description="Total execution time.")
    steps: List[WebStepResult] = Field(default_factory=list, description="Step-level outputs.")
    findings: List[Dict[str, Any]] = Field(default_factory=list, description="Aggregated findings.")
    raw: Dict[str, Any] = Field(..., description="Raw supervisor payload.")


def _build_response(target_url: HttpUrl, payload: Dict[str, Any]) -> WebScanResponse:
    results = payload.get("results") or {}
    steps_data = results.get("steps_completed") or []
    return WebScanResponse(
        scan_id=payload.get("task_id", "unknown"),
        url=target_url,
        status=payload.get("status", "unknown"),
        elapsed_seconds=float(results.get("execution_time", 0.0) or 0.0),
        steps=[WebStepResult(**step) for step in steps_data],
        findings=results.get("findings") or [],
        raw=payload,
    )


@router.post(
    "/scan",
    response_model=WebScanResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Perform a web application assessment",
    description="Trigger a web assessment using the supervisor's web agent (e.g., Gobuster, Nikto, SQLMap).",
)
async def web_scan(
    request: WebScanRequest,
    _api_key: Optional[str] = Depends(verify_api_key),
    supervisor=Depends(get_supervisor),
) -> WebScanResponse:
    """Kick off a web assessment task through the supervisor."""
    parameters = request.model_dump()

    try:
        result = await supervisor.process_user_request(
            f"Perform web application security assessment on {request.url}",
            parameters,
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Supervisor error: {exc}",
        ) from exc

    return _build_response(request.url, result)
