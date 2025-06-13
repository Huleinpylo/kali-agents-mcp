import pytest
from src.mcp_servers.web_server import _parse_gobuster_output


def test_parse_gobuster_output(sample_gobuster_output):
    results = _parse_gobuster_output(sample_gobuster_output)
    assert results == [
        {"path": "/admin", "status_code": 200, "size": 1234},
        {"path": "/backup", "status_code": 403, "size": 278},
        {"path": "/login", "status_code": 200, "size": 2156},
        {"path": "/uploads", "status_code": 301, "size": 234},
    ]
