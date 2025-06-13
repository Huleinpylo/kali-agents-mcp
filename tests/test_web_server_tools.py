import pytest
from unittest.mock import patch, AsyncMock

from src.mcp_servers.web_server import _manual_tech_detection


class MockResponse:
    def __init__(self, headers, body):
        self.headers = headers
        self._body = body

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def text(self):
        return self._body


class MockSession:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    def get(self, url, timeout):
        return self._response


@pytest.mark.asyncio
async def test_manual_tech_detection_success():
    headers = {"Server": "Apache"}
    body = "<html>wp-content example</html>"
    response = MockResponse(headers, body)
    session = MockSession(response)

    with patch("aiohttp.ClientSession", return_value=session):
        result = await _manual_tech_detection("http://example.com")

    assert result["status"] == "completed"
    assert result["method"] == "manual_detection"
    assert {"name": "Web Server", "value": "Apache", "confidence": "High"} in result["technologies"]
    assert {"name": "WordPress", "confidence": "Medium"} in result["technologies"]


@pytest.mark.asyncio
async def test_manual_tech_detection_error():
    async def failing_aenter(*args, **kwargs):
        raise RuntimeError("boom")

    mock_session = AsyncMock()
    mock_session.__aenter__.side_effect = failing_aenter

    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await _manual_tech_detection("http://example.com")

    assert result["status"] == "error"
    assert "boom" in result["error"]

