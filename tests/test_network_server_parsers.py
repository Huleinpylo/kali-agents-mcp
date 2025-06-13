import pytest
from src.mcp_servers.network_server import _parse_nmap_xml, _parse_discovery_output


def test_parse_nmap_xml(sample_nmap_xml):
    results = _parse_nmap_xml(sample_nmap_xml)
    assert results["status"] == "completed"
    assert "127.0.0.1" in results["hosts"]
    host = results["hosts"]["127.0.0.1"]
    assert host["status"] == "up"
    assert any(p["port"] == 22 for p in host["ports"])
    assert host["os"]["name"] == "Linux"


def test_parse_discovery_output(sample_discovery_output):
    results = _parse_discovery_output(sample_discovery_output)
    assert results == [
        {"ip": "192.168.1.10", "hostname": "host1", "status": "up"},
        {"ip": "192.168.1.11", "hostname": "192.168.1.11", "status": "up"},
    ]

