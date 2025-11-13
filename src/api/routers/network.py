"""Network scanning endpoints."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from src.api.dependencies import get_supervisor
from src.api.security import verify_api_key

router = APIRouter(prefix="/network", tags=["network"])


class NetworkScanRequest(BaseModel):
    """Request body for network scans."""

    target: str = Field(..., description="Target IP/hostname/CIDR to scan.", example="192.168.1.10")
    scan_type: str = Field(
        default="stealth",
        description="Scan profile (stealth, aggressive, full, quick).",
        examples=["stealth"],
    )
    ports: Optional[str] = Field(
        default=None,
        description="Port specification such as '80,443,8080' or '1-5000'.",
    )
    verbose: bool = Field(default=False, description="Enable verbose output.")
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional tool-specific options forwarded to the supervisor.",
    )


class StepResult(BaseModel):
    """Slim view of a supervisor step result."""

    model_config = ConfigDict(extra="allow")

    step: Optional[int] = Field(default=None, description="Execution step number.")
    name: Optional[str] = Field(default=None, description="Human readable step name.")
    status: Optional[str] = Field(default=None, description="Status reported by the agent.")
    execution_time: Optional[float] = Field(default=None, description="Duration in seconds.")
    findings: Optional[List[Dict[str, Any]]] = Field(default=None, description="Findings emitted by the step.")


class NetworkScanResponse(BaseModel):
    """Normalized response for network scans."""

    scan_id: str = Field(..., description="Supervisor task identifier.")
    target: str = Field(..., description="Target that was scanned.")
    status: str = Field(..., description="Overall task status.")
    elapsed_seconds: float = Field(..., description="Total execution time.")
    steps: List[StepResult] = Field(default_factory=list, description="Individual step outputs.")
    findings: List[Dict[str, Any]] = Field(default_factory=list, description="Aggregated findings.")
    raw: Dict[str, Any] = Field(..., description="Raw supervisor payload for advanced tooling.")


def _build_response(target: str, payload: Dict[str, Any]) -> NetworkScanResponse:
    results = payload.get("results") or {}
    steps_data = results.get("steps_completed") or []
    return NetworkScanResponse(
        scan_id=payload.get("task_id", "unknown"),
        target=target,
        status=payload.get("status", "unknown"),
        elapsed_seconds=float(results.get("execution_time", 0.0) or 0.0),
        steps=[StepResult(**step) for step in steps_data],
        findings=results.get("findings") or [],
        raw=payload,
    )


@router.post(
    "/scan",
    response_model=NetworkScanResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Perform a network scan",
    description="Trigger a supervisor-coordinated network scan using Kali toolchain (nmap, masscan, etc.).",
)
async def network_scan(
    request: NetworkScanRequest,
    _api_key: Optional[str] = Depends(verify_api_key),
    supervisor=Depends(get_supervisor),
) -> NetworkScanResponse:
    """Kick off a network scan task through the supervisor."""
    parameters = request.model_dump()

    try:
        result = await supervisor.process_user_request(
            f"Perform network reconnaissance on {request.target}",
            parameters,
        )
    except Exception as exc:  # pragma: no cover - pass supervisor errors upstream
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Supervisor error: {exc}",
        ) from exc

    return _build_response(request.target, result)
