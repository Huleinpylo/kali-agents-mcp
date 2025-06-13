import pytest
from src.mcp_servers.web_server import (
    _parse_gobuster_output,
    _parse_nikto_output,
    _parse_sqlmap_output,
    _parse_whatweb_output,
)


def test_parse_gobuster_output(sample_gobuster_output):
    results = _parse_gobuster_output(sample_gobuster_output)
    assert results == [
        {"path": "/admin", "status_code": 200, "size": 1234},
        {"path": "/backup", "status_code": 403, "size": 278},
        {"path": "/login", "status_code": 200, "size": 2156},
        {"path": "/uploads", "status_code": 301, "size": 234},
    ]


def test_parse_nikto_output(sample_nikto_output):
    results = _parse_nikto_output(sample_nikto_output)
    assert results == [
        {
            "id": "1",
            "msg": "Possible SQL injection",
            "uri": "/index.php",
            "method": "GET",
            "OSVDB": "12345",
            "severity": "high",
        }
    ]


def test_parse_sqlmap_output(sample_sqlmap_output):
    results = _parse_sqlmap_output(sample_sqlmap_output)
    assert {
        "type": "Boolean-based blind SQL injection",
        "severity": "high",
        "technique": "boolean",
    } in results


def test_parse_whatweb_output(sample_whatweb_output):
    results = _parse_whatweb_output(sample_whatweb_output)
    assert results == [
        {"name": "Apache", "confidence": "Medium", "version": "2.4.52", "details": "Apache httpd"}
    ]
