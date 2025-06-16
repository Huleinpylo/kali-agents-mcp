import sys
import types

# Stub fastmcp so that web_server can be imported without the real package.
fastmcp_stub = types.ModuleType("fastmcp")
class DummyMCP:
    def __init__(self, *args, **kwargs):
        pass

    def tool(self, func):
        return func

    def run(self):
        pass

fastmcp_stub.FastMCP = DummyMCP  # type: ignore
fastmcp_stub.Context = object  # type: ignore
sys.modules.setdefault("fastmcp", fastmcp_stub)

numpy_stub = types.ModuleType("numpy")
sys.modules.setdefault("numpy", numpy_stub)

# The server imports dotenv for configuration loading. Provide a stub to avoid
# missing dependency errors during import.
dotenv_stub = types.ModuleType("dotenv")
dotenv_stub.load_dotenv = lambda *a, **k: None
sys.modules.setdefault("dotenv", dotenv_stub)

from src.mcp_servers.web_server import _parse_nikto_text_output, _classify_nikto_severity


def test_parse_nikto_text_output():
    text = """
+ OSVDB-3092: SQL injection risk found
+ OSVDB-4123: header disclosure
"""
    vulns = _parse_nikto_text_output(text)
    assert vulns == [
        {"id": "NIKTO-TEXT", "msg": "OSVDB-3092: SQL injection risk found", "severity": "high"},
        {"id": "NIKTO-TEXT", "msg": "OSVDB-4123: header disclosure", "severity": "medium"},
    ]


def test_classify_nikto_severity():
    assert _classify_nikto_severity("Possible SQL injection") == "high"
    assert _classify_nikto_severity("password disclosure") == "medium"
    assert _classify_nikto_severity("Server header exposed") == "medium"
    assert _classify_nikto_severity("other info") == "info"
