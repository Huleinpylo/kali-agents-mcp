import sys
import types
import pytest

# Provide a minimal fastmcp stub so SupervisorAgent can be imported without the
# real dependency.
fastmcp_stub = types.ModuleType("fastmcp")
fastmcp_stub.Client = object  # type: ignore

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
numpy_stub.array = lambda *a, **k: None  # minimal stub
sys.modules.setdefault("numpy", numpy_stub)

from src.agents.supervisor import SupervisorAgent

@pytest.mark.asyncio
async def test_create_network_plan():
    sup = SupervisorAgent(agent_id="sup1")
    task = await sup._analyze_and_create_task("network scan", {"target": "example.com"})
    plan = await sup._create_execution_plan(task)
    assert plan.task_id == task.id
    assert plan.assigned_agents == ["network_agent"]
    assert any(step["name"] == "Network Discovery" for step in plan.steps)

@pytest.mark.asyncio
async def test_extract_findings():
    sup = SupervisorAgent(agent_id="sup2")
    step_results = [
        {
            "tool": "nmap_scan",
            "result": {
                "hosts": {
                    "example.com": {
                        "status": "up",
                        "ports": [
                            {"port": 22, "protocol": "tcp", "service": "ssh", "state": "open"}
                        ]
                    }
                }
            },
        },
        {
            "tool": "nikto_scan",
            "result": {
                "vulnerabilities": [
                    {"id": "OSVDB-1", "msg": "Server header", "severity": "info"}
                ]
            },
        },
        {
            "tool": "gobuster_directory",
            "result": {
                "discovered_paths": [
                    {"path": "/admin", "status_code": 200, "size": 123}
                ]
            },
        },
    ]
    findings = sup._extract_findings_from_results(step_results)
    types = {f["type"] for f in findings}
    assert {"open_port", "web_vulnerability", "interesting_path"} <= types
