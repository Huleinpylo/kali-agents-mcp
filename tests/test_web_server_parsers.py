import importlib
import sys
import types
from pathlib import Path

import pytest

# Ensure the src package is importable when running tests directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def stub_external_modules(monkeypatch):
    """Provide lightweight stubs for external dependencies."""
    fake_fastmcp = types.ModuleType("fastmcp")

    class FakeMCP:
        def __init__(self, *_, **__):
            pass

        def tool(self, func=None):
            def decorator(fn):
                return fn

            return decorator if func is None else decorator(func)

        def run(self):
            pass

    fake_fastmcp.FastMCP = FakeMCP
    fake_fastmcp.Context = object
    monkeypatch.setitem(sys.modules, "fastmcp", fake_fastmcp)

    fake_dotenv = types.ModuleType("dotenv")
    fake_dotenv.load_dotenv = lambda *a, **k: None
    monkeypatch.setitem(sys.modules, "dotenv", fake_dotenv)

    yield


def test_parse_gobuster_output(sample_gobuster_output):
    web_server = importlib.import_module("src.mcp_servers.web_server")
    results = web_server._parse_gobuster_output(sample_gobuster_output)
    assert any(r["path"] == "/admin" and r["status_code"] == 200 for r in results)
    assert any(r["path"] == "/backup" and r["status_code"] == 403 for r in results)


def test_parse_sqlmap_output(sample_sqlmap_output):
    web_server = importlib.import_module("src.mcp_servers.web_server")
    results = web_server._parse_sqlmap_output(sample_sqlmap_output)
    assert any(item.get("type") == "Boolean-based blind SQL injection" for item in results)
