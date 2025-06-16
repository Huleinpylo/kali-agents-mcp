import asyncio
import sys
import types
from importlib import reload

import pytest


@pytest.fixture
def data_server(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DB_PATH", str(db_path))

    class DummyMCP:
        def __init__(self, *args, **kwargs):
            pass

        def tool(self, func):
            return func

        def run(self):
            pass

    dummy_module = types.ModuleType("fastmcp")
    dummy_module.FastMCP = DummyMCP  # type: ignore
    dummy_module.Context = object  # type: ignore
    monkeypatch.setitem(sys.modules, "fastmcp", dummy_module)

    dotenv_mod = types.ModuleType("dotenv")
    dotenv_mod.load_dotenv = lambda: None  # type: ignore
    monkeypatch.setitem(sys.modules, "dotenv", dotenv_mod)

    if "mcp_servers.data_server" in sys.modules:
        module = reload(sys.modules["mcp_servers.data_server"])
    else:
        module = __import__("mcp_servers.data_server", fromlist=["*"])
    return module


def test_create_and_read_record(data_server):
    data = {
        "agent": "agent1",
        "target": "example.com",
        "scan_type": "nmap",
        "result": "{}",
    }
    asyncio.run(data_server.create_record("scan_results", data))
    records = asyncio.run(data_server.read_records("scan_results", {"agent": "agent1"}))
    assert len(records) == 1
    assert records[0]["target"] == "example.com"


def test_update_and_delete_record(data_server):
    data = {
        "agent": "agent1",
        "target": "example.com",
        "scan_type": "nmap",
        "result": "{}",
    }
    res = asyncio.run(data_server.create_record("scan_results", data))
    record_id = res["id"]

    asyncio.run(
        data_server.update_record("scan_results", record_id, {"target": "updated"})
    )
    recs = asyncio.run(data_server.read_records("scan_results", {"id": record_id}))
    assert recs[0]["target"] == "updated"

    asyncio.run(data_server.delete_record("scan_results", record_id))
    after = asyncio.run(data_server.read_records("scan_results", {"id": record_id}))
    assert after == []


def test_store_scan_result_and_history(data_server):
    result_data = {"ports": [80]}
    asyncio.run(data_server.store_scan_result("agent1", "host", "nmap", result_data))
    history = asyncio.run(data_server.get_scan_history("host"))
    assert len(history) == 1
    assert history[0]["result"] == result_data
