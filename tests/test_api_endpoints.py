"""FastAPI endpoint tests for network and web scans."""

import asyncio
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from src.api.dependencies import get_supervisor
from src.api.main import app


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
def client(monkeypatch):
    """Provide a TestClient with supervisor dependency overridden."""

    dummy = _DummySupervisor()
    app.dependency_overrides[get_supervisor] = lambda: dummy
    monkeypatch.delenv("KALI_AGENTS_API_KEY", raising=False)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_supervisor, None)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_network_scan_returns_payload(client):
    response = client.post(
        "/network/scan",
        json={"target": "192.168.1.1", "scan_type": "stealth"},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["scan_id"] == "task-test"
    assert data["target"] == "192.168.1.1"
    assert data["status"] == "completed"
    assert data["findings"]


def test_web_scan_returns_payload(client):
    response = client.post(
        "/web/scan",
        json={"url": "https://example.com", "deep_scan": True},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["scan_id"] == "task-test"
    assert data["url"] == "https://example.com"
    assert data["status"] == "completed"
    assert data["findings"]


def test_missing_api_key_when_required(monkeypatch):
    monkeypatch.setenv("KALI_AGENTS_API_KEY", "secret-token")
    app.dependency_overrides[get_supervisor] = lambda: _DummySupervisor()

    with TestClient(app) as test_client:
        response = test_client.post(
            "/network/scan",
            json={"target": "192.168.1.1", "scan_type": "stealth"},
        )

    assert response.status_code == 401
    assert response.json()["detail"].lower().startswith("invalid or missing")
    app.dependency_overrides.pop(get_supervisor, None)
    monkeypatch.delenv("KALI_AGENTS_API_KEY", raising=False)
