"""FastAPI endpoint tests (router-level)."""

import asyncio
from typing import Any, Dict

import pytest
from fastapi import HTTPException

from src.api.main import health_check
from src.api.routers.network import NetworkScanRequest, network_scan
from src.api.routers.web import WebScanRequest, web_scan
from src.api.security import verify_api_key


class _DummySupervisor:
    async def process_user_request(self, request: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Return a predictable payload for tests."""

        await asyncio.sleep(0)  # exercise async path
        return {
            "task_id": "task-test",
            "status": "completed",
            "results": {
                "execution_time": 1.23,
                "steps_completed": [
                    {
                        "step": 1,
                        "name": "Simulated Step",
                        "status": "ok",
                        "execution_time": 1.23,
                        "findings": [{"detail": "sample"}],
                    }
                ],
                "findings": [{"detail": "sample"}],
            },
        }


@pytest.fixture()
def dummy_supervisor() -> _DummySupervisor:
    return _DummySupervisor()


@pytest.mark.asyncio
async def test_health_endpoint():
    response = await health_check()
    assert response == {"status": "ok"}


@pytest.mark.asyncio
async def test_network_scan_returns_payload(dummy_supervisor):
    request = NetworkScanRequest(target="192.168.1.1", scan_type="stealth")
    response = await network_scan(request, _api_key=None, supervisor=dummy_supervisor)

    assert response.scan_id == "task-test"
    assert response.target == "192.168.1.1"
    assert response.status == "completed"
    assert response.findings


@pytest.mark.asyncio
async def test_web_scan_returns_payload(dummy_supervisor):
    request = WebScanRequest(url="https://example.com", deep_scan=True)
    response = await web_scan(request, _api_key=None, supervisor=dummy_supervisor)

    assert response.scan_id == "task-test"
    assert str(response.url) == "https://example.com/"
    assert response.status == "completed"
    assert response.findings


@pytest.mark.asyncio
async def test_missing_api_key_when_required(monkeypatch):
    monkeypatch.setenv("KALI_AGENTS_API_KEY", "secret-token")

    with pytest.raises(HTTPException) as exc:
        await verify_api_key(api_key=None)

    assert exc.value.status_code == 401
    assert str(exc.value.detail).lower().startswith("invalid or missing")
    monkeypatch.delenv("KALI_AGENTS_API_KEY", raising=False)
