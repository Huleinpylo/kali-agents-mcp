
# tests/test_supervisor_agent.py
"""
Comprehensive tests for SupervisorAgent to achieve 100% coverage.
Critical Priority: 0% -> 80%+ coverage (139 untested statements)
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import uuid

from src.agents.supervisor import SupervisorAgent, create_supervisor_agent
from src.models.core import (
    AgentType, TaskStatus, Priority, AgentState, Task, SystemState,
    PerformanceMetrics, LearningContext, TaskExecutionPlan
)


class TestSupervisorAgent:
    """Test SupervisorAgent initialization and basic functionality."""
    
    def test_supervisor_agent_initialization(self):
        """Test supervisor agent initialization with default parameters."""
        supervisor = SupervisorAgent()
        
        assert supervisor.agent_id.startswith("supervisor_")
        assert isinstance(supervisor.system_state, SystemState)
        assert isinstance(supervisor.mcp_clients, dict)
        assert len(supervisor.adaptation_algorithms) == 3
        assert "fuzzy_logic" in supervisor.adaptation_algorithms
        assert "genetic_algorithm" in supervisor.adaptation_algorithms
        assert "q_learning" in supervisor.adaptation_algorithms
    
    def test_supervisor_agent_custom_id(self):
        """Test supervisor agent initialization with custom ID."""
        custom_id = "test_supervisor_123"
        supervisor = SupervisorAgent(agent_id=custom_id)
        
        assert supervisor.agent_id == custom_id
    
    def test_initialize_agents(self):
        """Test agent initialization creates all expected agent types."""
        supervisor = SupervisorAgent()
        
        # Verify all expected agents are created
        expected_agents = [
            "network_agent", "web_agent", "vulnerability_agent",
            "forensic_agent", "social_agent", "report_agent"
        ]
        
        for agent_id in expected_agents:
            assert agent_id in supervisor.system_state.agents
            agent_state = supervisor.system_state.agents[agent_id]
            assert isinstance(agent_state, AgentState)
    
    def test_network_agent_special_initialization(self):
        """Test that network agent gets special initialization."""
        supervisor = SupervisorAgent()
        network_agent = supervisor.system_state.agents["network_agent"]
        
        # Network agent should have specialized state
        assert network_agent.agent_type == AgentType.NETWORK
    
    def test_get_system_status(self):
        """Test system status retrieval."""
        supervisor = SupervisorAgent()
        status = supervisor.get_system_status()
        
        assert "supervisor_id" in status
        assert "agents" in status
        assert "active_tasks" in status
        assert "completed_tasks" in status
        assert "learning_algorithms" in status
        assert "total_decisions" in status
        
        assert status["supervisor_id"] == supervisor.agent_id
        assert len(status["agents"]) == 6  # All initialized agents
        assert status["learning_algorithms"] == ["fuzzy_logic", "genetic_algorithm", "q_learning"]


class TestRequestProcessing:
    """Test user request processing and task creation."""
    
    @pytest.mark.asyncio
    async def test_process_user_request_penetration_test(self):
        """Test processing a penetration test request."""
        supervisor = SupervisorAgent()
        
        with patch.object(supervisor, '_create_execution_plan') as mock_plan, \
             patch.object(supervisor, '_execute_plan') as mock_execute, \
             patch.object(supervisor, '_learn_from_execution') as mock_learn:
            
            mock_plan.return_value = TaskExecutionPlan(
                task_id="test_task",
                steps=[{"step": 1, "name": "Test Step"}],
                assigned_agents=["network_agent"],
                estimated_duration=300
            )
            mock_execute.return_value = {"status": "completed", "findings": []}
            mock_learn.return_value = None
            
            result = await supervisor.process_user_request(
                "Perform a penetration test on target.com",
                {"target": "target.com"}
            )
            
            assert "task_id" in result
            assert result["status"] == TaskStatus.COMPLETED.value
            assert "results" in result
            assert "performance" in result
    
    @pytest.mark.asyncio
    async def test_analyze_and_create_task_pentest(self):
        """Test task analysis for penetration test keywords."""
        supervisor = SupervisorAgent()
        
        task = await supervisor._analyze_and_create_task(
            "Perform a penetration test on example.com",
            {"target": "example.com", "scope": "full"}
        )
        
        assert task.task_type == "penetration_test"
        assert task.priority == Priority.HIGH
        assert task.parameters["target"] == "example.com"
        assert "penetration test" in task.name.lower()
    
    @pytest.mark.asyncio
    async def test_analyze_and_create_task_network_scan(self):
        """Test task analysis for network scan keywords."""
        supervisor = SupervisorAgent()
        
        task = await supervisor._analyze_and_create_task(
            "Run a network scan on 192.168.1.0/24",
            {"target": "192.168.1.0/24"}
        )
        
        assert task.task_type == "network_scan"
        assert task.priority == Priority.MEDIUM
        assert task.parameters["target"] == "192.168.1.0/24"
    
    @pytest.mark.asyncio
    async def test_analyze_and_create_task_web_assessment(self):
        """Test task analysis for web assessment keywords."""
        supervisor = SupervisorAgent()
        
        task = await supervisor._analyze_and_create_task(
            "Test the web application at https://example.com",
            {"target": "https://example.com"}
        )
        
        assert task.task_type == "web_assessment"
        assert task.priority == Priority.MEDIUM
    
    @pytest.mark.asyncio
    async def test_analyze_and_create_task_general(self):
        """Test task analysis for general assessment."""
        supervisor = SupervisorAgent()
        
        task = await supervisor._analyze_and_create_task(
            "Check security of example.com",
            {"target": "example.com"}
        )
        
        assert task.task_type == "general_assessment"
        assert task.priority == Priority.MEDIUM
        assert task.learning_context is not None
        assert task.learning_context.algorithm_type == "genetic_algorithm"


class TestExecutionPlanning:
    """Test execution plan creation for different task types."""
    
    @pytest.mark.asyncio
    async def test_create_execution_plan_penetration_test(self):
        """Test execution plan creation for penetration test."""
        supervisor = SupervisorAgent()
        task = Task(
            name="Pentest - target.com",
            description="Full penetration test",
            task_type="penetration_test",
            priority=Priority.HIGH,
            parameters={"target": "target.com"}
        )
        
        plan = await supervisor._create_execution_plan(task)
        
        assert isinstance(plan, TaskExecutionPlan)
        assert plan.task_id == task.id
        assert len(plan.steps) == 4  # Network, Web, Vuln, Report
        assert plan.assigned_agents == ["network_agent", "web_agent", "vulnerability_agent", "report_agent"]
        assert plan.estimated_duration == 1800  # Sum of step times
    
    @pytest.mark.asyncio
    async def test_create_execution_plan_network_scan(self):
        """Test execution plan creation for network scan."""
        supervisor = SupervisorAgent()
        task = Task(
            name="Network Scan",
            description="Network discovery",
            task_type="network_scan",
            priority=Priority.MEDIUM,
            parameters={"target": "192.168.1.0/24"}
        )
        
        plan = await supervisor._create_execution_plan(task)
        
        assert len(plan.steps) == 1
        assert plan.steps[0]["agent"] == "network_agent"
        assert "network_discovery" in plan.steps[0]["tools"]
    
    @pytest.mark.asyncio
    async def test_create_execution_plan_web_assessment(self):
        """Test execution plan creation for web assessment."""
        supervisor = SupervisorAgent()
        task = Task(
            name="Web Assessment",
            description="Web application security test",
            task_type="web_assessment",
            priority=Priority.MEDIUM,
            parameters={"target": "https://example.com"}
        )
        
        plan = await supervisor._create_execution_plan(task)
        
        assert len(plan.steps) == 2
        assert all(step["agent"] == "web_agent" for step in plan.steps)


class TestPlanExecution:
    """Test plan execution and step processing."""
    
    @pytest.mark.asyncio
    async def test_execute_plan_success(self):
        """Test successful plan execution."""
        supervisor = SupervisorAgent()
        
        task = Task(
            name="Test Task",
            description="Test execution",
            task_type="network_scan",
            priority=Priority.MEDIUM,
            parameters={"target": "localhost"}
        )
        
        # Create a simple execution plan
        task.execution_plan = TaskExecutionPlan(
            task_id=task.id,
            steps=[{
                "step": 1,
                "name": "Network Discovery",
                "agent": "network_agent",
                "tools": ["network_discovery"],
                "estimated_time": 240
            }],
            assigned_agents=["network_agent"],
            estimated_duration=240
        )
        
        with patch.object(supervisor, '_execute_step') as mock_step:
            mock_step.return_value = {
                "status": "completed",
                "agent": "network_agent",
                "tools_executed": [{"tool": "network_discovery", "result": {"status": "completed"}}],
                "findings": [{"type": "info", "message": "Test finding"}],
                "execution_time": 2.5
            }
            
            results = await supervisor._execute_plan(task)
            
            assert results["execution_time"] > 0
            assert len(results["steps_completed"]) == 1
            assert len(results["findings"]) == 1
            assert len(results["errors"]) == 0
            assert task.status == TaskStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_execute_plan_no_plan(self):
        """Test execution with no plan available."""
        supervisor = SupervisorAgent()
        task = Task(
            name="Test Task",
            description="Test execution",
            task_type="network_scan",
            priority=Priority.MEDIUM,
            parameters={"target": "localhost"}
        )
        
        results = await supervisor._execute_plan(task)
        
        assert "error" in results
        assert results["error"] == "No execution plan available"
    
    @pytest.mark.asyncio
    async def test_execute_plan_with_errors(self):
        """Test execution plan with errors."""
        supervisor = SupervisorAgent()
        
        task = Task(
            name="Test Task",
            description="Test execution",
            task_type="network_scan",
            priority=Priority.MEDIUM,
            parameters={"target": "localhost"}
        )
        
        task.execution_plan = TaskExecutionPlan(
            task_id=task.id,
            steps=[{
                "step": 1,
                "name": "Failing Step",
                "agent": "network_agent",
                "tools": ["failing_tool"],
                "estimated_time": 60
            }],
            assigned_agents=["network_agent"],
            estimated_duration=60
        )
        
        with patch.object(supervisor, '_execute_step') as mock_step:
            mock_step.return_value = {
                "status": "error",
                "agent": "network_agent",
                "error": "Tool execution failed"
            }
            
            results = await supervisor._execute_plan(task)
            
            assert len(results["errors"]) == 1
            assert results["errors"][0]["error"] == "Tool execution failed"
    
    @pytest.mark.asyncio
    async def test_execute_plan_exception_handling(self):
        """Test execution plan exception handling."""
        supervisor = SupervisorAgent()
        
        task = Task(
            name="Test Task",
            description="Test execution",
            task_type="network_scan",
            priority=Priority.MEDIUM,
            parameters={"target": "localhost"}
        )
        
        task.execution_plan = TaskExecutionPlan(
            task_id=task.id,
            steps=[{"step": 1, "name": "Test", "agent": "test", "tools": [], "estimated_time": 60}],
            assigned_agents=["test"],
            estimated_duration=60
        )
        
        with patch.object(supervisor, '_execute_step') as mock_step:
            mock_step.side_effect = Exception("Unexpected error")
            
            results = await supervisor._execute_plan(task)
            
            assert len(results["errors"]) == 1
            assert "Execution failed: Unexpected error" in results["errors"][0]["error"]
            assert task.status == TaskStatus.FAILED


class TestStepExecution:
    """Test individual step execution."""
    
    @pytest.mark.asyncio
    async def test_execute_step_success(self):
        """Test successful step execution."""
        supervisor = SupervisorAgent()
        
        step = {
            "step": 1,
            "name": "Network Discovery",
            "agent": "network_agent",
            "tools": ["network_discovery", "nmap_scan"]
        }
        
        with patch.object(supervisor, '_simulate_tool_execution') as mock_tool:
            mock_tool.side_effect = [
                {"status": "completed", "network": "192.168.1.0/24", "live_hosts": [{"ip": "192.168.1.1"}]},
                {"status": "completed", "target": "192.168.1.1", "hosts": {"192.168.1.1": {"status": "up", "ports": []}}}
            ]
            
            result = await supervisor._execute_step(step, {"target": "192.168.1.1"})
            
            assert result["status"] == "completed"
            assert result["agent"] == "network_agent"
            assert len(result["tools_executed"]) == 2
            assert "findings" in result
    
    @pytest.mark.asyncio
    async def test_execute_step_exception(self):
        """Test step execution with exception."""
        supervisor = SupervisorAgent()
        
        step = {
            "step": 1,
            "name": "Failing Step",
            "agent": "network_agent",
            "tools": ["failing_tool"]
        }
        
        with patch.object(supervisor, '_simulate_tool_execution') as mock_tool:
            mock_tool.side_effect = Exception("Tool execution failed")
            
            result = await supervisor._execute_step(step, {"target": "localhost"})
            
            assert result["status"] == "error"
            assert result["agent"] == "network_agent"
            assert "Tool execution failed" in result["error"]


class TestToolSimulation:
    """Test tool execution simulation."""
    
    @pytest.mark.asyncio
    async def test_simulate_nmap_scan(self):
        """Test nmap scan simulation."""
        supervisor = SupervisorAgent()
        
        result = await supervisor._simulate_tool_execution("nmap_scan", {"target": "example.com"})
        
        assert result["status"] == "completed"
        assert result["target"] == "example.com"
        assert "hosts" in result
        assert "example.com" in result["hosts"]
        assert result["hosts"]["example.com"]["status"] == "up"
        assert len(result["hosts"]["example.com"]["ports"]) == 3
    
    @pytest.mark.asyncio
    async def test_simulate_network_discovery(self):
        """Test network discovery simulation."""
        supervisor = SupervisorAgent()
        
        result = await supervisor._simulate_tool_execution("network_discovery", {"target": "192.168.1.1"})
        
        assert result["status"] == "completed"
        assert result["network"] == "192.168.1.1/24"
        assert len(result["live_hosts"]) == 1
        assert result["total_hosts"] == 1
    
    @pytest.mark.asyncio
    async def test_simulate_gobuster_directory(self):
        """Test gobuster directory simulation."""
        supervisor = SupervisorAgent()
        
        result = await supervisor._simulate_tool_execution("gobuster_directory", {"target": "example.com"})
        
        assert result["status"] == "completed"
        assert result["url"] == "http://example.com"
        assert len(result["discovered_paths"]) == 2
        assert result["total_found"] == 2
    
    @pytest.mark.asyncio
    async def test_simulate_nikto_scan(self):
        """Test nikto scan simulation."""
        supervisor = SupervisorAgent()
        
        result = await supervisor._simulate_tool_execution("nikto_scan", {"target": "example.com"})
        
        assert result["status"] == "completed"
        assert result["url"] == "http://example.com"
        assert len(result["vulnerabilities"]) == 1
        assert result["total_vulnerabilities"] == 1
    
    @pytest.mark.asyncio
    async def test_simulate_sqlmap_test(self):
        """Test sqlmap test simulation."""
        supervisor = SupervisorAgent()
        
        result = await supervisor._simulate_tool_execution("sqlmap_test", {"target": "example.com"})
        
        assert result["status"] == "completed"
        assert result["url"] == "http://example.com/login.php"
        assert result["vulnerable"] is False
        assert result["injection_points"] == []
    
    @pytest.mark.asyncio
    async def test_simulate_unknown_tool(self):
        """Test unknown tool simulation."""
        supervisor = SupervisorAgent()
        
        result = await supervisor._simulate_tool_execution("unknown_tool", {"target": "example.com"})
        
        assert result["status"] == "completed"
        assert "unknown_tool executed successfully" in result["message"]


class TestFindingsExtraction:
    """Test security findings extraction from tool results."""
    
    def test_extract_findings_open_ports(self):
        """Test extraction of open ports as findings."""
        supervisor = SupervisorAgent()
        
        step_results = [{
=======
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
                            {"port": 22, "protocol": "tcp", "service": "ssh", "state": "open"},
                            {"port": 80, "protocol": "tcp", "service": "http", "state": "open"}
                        ]
                    }
                }
            }
        }]
        
        findings = supervisor._extract_findings_from_results(step_results)
        
        assert len(findings) == 2
        assert all(f["type"] == "open_port" for f in findings)
        assert findings[0]["port"] == 22
        assert findings[1]["port"] == 80
    
    def test_extract_findings_web_vulnerabilities(self):
        """Test extraction of web vulnerabilities as findings."""
        supervisor = SupervisorAgent()
        
        step_results = [{
            "tool": "nikto_scan",
            "result": {
                "vulnerabilities": [
                    {"id": "OSVDB-3092", "msg": "Server header found", "severity": "info"},
                    {"id": "CVE-2021-1234", "msg": "SQL injection", "severity": "high"}
                ]
            }
        }]
        
        findings = supervisor._extract_findings_from_results(step_results)
        
        assert len(findings) == 2
        assert all(f["type"] == "web_vulnerability" for f in findings)
        assert findings[0]["reference"] == "OSVDB-3092"
        assert findings[1]["severity"] == "high"
    
    def test_extract_findings_discovered_paths(self):
        """Test extraction of discovered paths as findings."""
        supervisor = SupervisorAgent()
        
        step_results = [{
            "tool": "gobuster_directory",
            "result": {
                "discovered_paths": [
                    {"path": "/admin", "status_code": 200, "size": 1234},
                    {"path": "/backup", "status_code": 403, "size": 278}
                ]
            }
        }]
        
        findings = supervisor._extract_findings_from_results(step_results)
        
        assert len(findings) == 1  # Only 200 status codes are considered interesting
        assert findings[0]["type"] == "interesting_path"
        assert findings[0]["path"] == "/admin"
    
    def test_extract_findings_empty_results(self):
        """Test findings extraction with empty results."""
        supervisor = SupervisorAgent()
        
        findings = supervisor._extract_findings_from_results([])
        
        assert findings == []


class TestLearningAndAdaptation:
    """Test learning and adaptation functionality."""
    
    @pytest.mark.asyncio
    async def test_learn_from_execution_success(self):
        """Test learning from successful execution."""
        supervisor = SupervisorAgent()
        
        task = Task(
            name="Test Task",
            description="Test learning",
            task_type="network_scan",
            priority=Priority.MEDIUM,
            parameters={"target": "localhost"},
            learning_context=LearningContext(
                algorithm_type="fuzzy_logic",
                parameters={"proficiency": 0.7}
            )
        )
        
        task.performance_metrics = PerformanceMetrics(
            execution_time=30.0,
            success_rate=1.0,
            accuracy=0.95,
            error_count=0,
            confidence_score=0.9
        )
        
        results = {
            "execution_time": 30.0,
            "success": True,
            "findings_count": 5,
            "steps_count": 2,
            "errors": []
        }
        
        with patch.object(supervisor.adaptation_algorithms["fuzzy_logic"], 'adapt') as mock_adapt:
            mock_adapt.return_value = {"algorithm": "fuzzy_logic", "adjustments": {"rules_updated": True}}
            
            await supervisor._learn_from_execution(task, results)
            
            mock_adapt.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_learn_from_execution_no_context(self):
        """Test learning with no learning context."""
        supervisor = SupervisorAgent()
        
        task = Task(
            name="Test Task",
            description="Test learning",
            task_type="network_scan",
            priority=Priority.MEDIUM,
            parameters={"target": "localhost"}
        )
        
        task.performance_metrics = PerformanceMetrics(
            execution_time=30.0,
            success_rate=1.0,
            accuracy=0.95,
            error_count=0,
            confidence_score=0.9
        )
        
        results = {"execution_time": 30.0, "errors": []}
        
        # Should not raise exception
        await supervisor._learn_from_execution(task, results)
    
    @pytest.mark.asyncio
    async def test_learn_from_execution_performance_history(self):
        """Test that learning updates agent performance history."""
        supervisor = SupervisorAgent()
        
        task = Task(
            name="Test Task",
            description="Test learning",
            task_type="network_scan",
            priority=Priority.MEDIUM,
            parameters={"target": "localhost"}
        )
        
        task.performance_metrics = PerformanceMetrics(
            execution_time=30.0,
            success_rate=1.0,
            accuracy=0.95,
            error_count=0,
            confidence_score=0.9
        )
        
        results = {"execution_time": 30.0, "errors": []}
        
        # Check initial state
        initial_history_length = len(supervisor.system_state.agents["network_agent"].performance_history)
        
        await supervisor._learn_from_execution(task, results)
        
        # Verify performance history was updated for all agents
        for agent_state in supervisor.system_state.agents.values():
            assert len(agent_state.performance_history) == initial_history_length + 1
    
    @pytest.mark.asyncio
    async def test_learn_from_execution_history_limit(self):
        """Test that performance history is limited to 50 records."""
        supervisor = SupervisorAgent()
        
        task = Task(
            name="Test Task",
            description="Test learning",
            task_type="network_scan",
            priority=Priority.MEDIUM,
            parameters={"target": "localhost"}
        )
        
        task.performance_metrics = PerformanceMetrics(
            execution_time=30.0,
            success_rate=1.0,
            accuracy=0.95,
            error_count=0,
            confidence_score=0.9
        )
        
        # Add 55 performance records to exceed limit
        agent_state = supervisor.system_state.agents["network_agent"]
        for i in range(55):
            agent_state.performance_history.append(task.performance_metrics)
        
        results = {"execution_time": 30.0, "errors": []}
        
        await supervisor._learn_from_execution(task, results)
        
        # Verify history is limited to 50 records
        assert len(agent_state.performance_history) == 50


class TestFactoryFunction:
    """Test factory function for creating supervisor agents."""
    
    def test_create_supervisor_agent_default(self):
        """Test creating supervisor agent with default parameters."""
        supervisor = create_supervisor_agent()
        
        assert isinstance(supervisor, SupervisorAgent)
        assert supervisor.agent_id.startswith("supervisor_")
    
    def test_create_supervisor_agent_custom_id(self):
        """Test creating supervisor agent with custom ID."""
        custom_id = "custom_supervisor_456"
        supervisor = create_supervisor_agent(custom_id)
        
        assert supervisor.agent_id == custom_id


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_process_request_empty_string(self):
        """Test processing empty request string."""
        supervisor = SupervisorAgent()
        
        with patch.object(supervisor, '_create_execution_plan') as mock_plan, \
             patch.object(supervisor, '_execute_plan') as mock_execute, \
             patch.object(supervisor, '_learn_from_execution') as mock_learn:
            
            mock_plan.return_value = TaskExecutionPlan(
                task_id="test_task",
                steps=[],
                assigned_agents=[],
                estimated_duration=0
            )
            mock_execute.return_value = {"status": "completed", "findings": []}
            mock_learn.return_value = None
            
            result = await supervisor.process_user_request("", {})
            
            assert "task_id" in result
    
    @pytest.mark.asyncio
    async def test_analyze_task_with_none_parameters(self):
        """Test task analysis with None parameters."""
        supervisor = SupervisorAgent()
        
        task = await supervisor._analyze_and_create_task("test request", {"parameters": None})
        
        assert task.parameters["target"] == "localhost"  # Default value
    
    def test_system_status_with_tasks(self):
        """Test system status when tasks exist."""
        supervisor = SupervisorAgent()
        
        # Add some mock tasks
        mock_task = Task(
            name="Test Task",
            description="Test",
            task_type="test",
            priority=Priority.MEDIUM,
            parameters={}
        )
        
        supervisor.system_state.active_tasks[mock_task.id] = mock_task
        supervisor.system_state.completed_tasks.append(mock_task)
        
        status = supervisor.get_system_status()
        
        assert status["active_tasks"] == 1
        assert status["completed_tasks"] == 1
    
    @pytest.mark.asyncio
    async def test_execution_with_all_plan_types(self):
        """Test that all plan types can be created and have valid structure."""
        supervisor = SupervisorAgent()
        
        task_types = ["penetration_test", "network_scan", "web_assessment", "unknown_type"]
        
        for task_type in task_types:
            task = Task(
                name=f"Test {task_type}",
                description=f"Test {task_type} execution",
                task_type=task_type,
                priority=Priority.MEDIUM,
                parameters={"target": "localhost"}
            )
            
            plan = await supervisor._create_execution_plan(task)
            
            assert isinstance(plan, TaskExecutionPlan)
            assert plan.task_id == task.id
            assert isinstance(plan.steps, list)
            assert isinstance(plan.assigned_agents, list)
            assert isinstance(plan.estimated_duration, (int, float))
