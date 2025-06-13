import types
import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Provide stub modules for optional dependencies
if 'dotenv' not in sys.modules:
    dotenv = types.ModuleType('dotenv')
    def load_dotenv(*args, **kwargs):
        pass
    dotenv.load_dotenv = load_dotenv
    sys.modules['dotenv'] = dotenv

import pytest


# Ensure the web_server module can be imported without optional dependencies
if 'fastmcp' not in sys.modules:
    fastmcp = types.ModuleType('fastmcp')
    class DummyFastMCP:
        def __init__(self, *a, **k):
            pass
        def tool(self, func=None):
            def decorator(f):
                return f
            return decorator(func) if func else decorator
    fastmcp.FastMCP = DummyFastMCP
    class DummyContext:
        pass
    fastmcp.Context = DummyContext
    sys.modules['fastmcp'] = fastmcp

from src.mcp_servers.web_server import _parse_gobuster_output, _parse_sqlmap_output


def test_parse_gobuster_output(sample_gobuster_output):
    raw_paths = _parse_gobuster_output(sample_gobuster_output)
    paths = [p for p in raw_paths if p["path"].startswith("/")]
    assert len(paths) == 4
    assert paths[0]["path"] == "/admin"
    assert paths[0]["status_code"] == 200
    assert paths[0]["size"] == 1234


def test_parse_sqlmap_output(sample_sqlmap_output):
    results = _parse_sqlmap_output(sample_sqlmap_output)
    assert any(r.get('technique') == 'boolean' for r in results)
    # Ensure we captured at least one injection point
    assert len(results) >= 1
