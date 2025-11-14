"""
Intelligent Supervisor Agent for Kali Agents System

The Supervisor Agent orchestrates all other agents using ML algorithms
for optimal task assignment and adaptive learning.
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from fastmcp import Client

from src.models import (
    AgentType, TaskStatus, Priority, AgentState, Task, 
    SystemState, PerformanceMetrics, LearningContext,
    create_adaptation_algorithm, create_network_agent_state
)


class SupervisorAgent:
    """Intelligent Supervisor Agent with ML-based decision making."""
    
    def __init__(self, agent_id: Optional[str] = None):
        self.agent_id = agent_id or f"supervisor_{uuid.uuid4().hex[:8]}"
        self.system_state = SystemState()
        self.mcp_clients: Dict[str, Client] = {}
        self.adaptation_algorithms = {
            "fuzzy_logic": create_adaptation_algorithm("fuzzy_logic", {}),
            "genetic_algorithm": create_adaptation_algorithm("genetic_algorithm", {"population_size": 20}),
            "q_learning": create_adaptation_algorithm("q_learning", {"learning_rate": 0.1})
        }
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all specialized agents in the system."""
        agent_configs = [
            ("network_agent", AgentType.NETWORK),
            ("web_agent", AgentType.WEB),
            ("vulnerability_agent", AgentType.VULNERABILITY),
            ("forensic_agent", AgentType.FORENSIC),
            ("social_agent", AgentType.SOCIAL),
            ("report_agent", AgentType.REPORT)
        ]
        
        for agent_id, agent_type in agent_configs:
            if agent_type == AgentType.NETWORK:
                agent_state = create_network_agent_state(agent_id)
            else:
                agent_state = AgentState(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    learning_state=LearningContext(
                        algorithm_type="fuzzy_logic",
                        parameters={"proficiency": 0.7}
                    )
                )
            
            self.system_state.agents[agent_id] = agent_state
    
    async def process_user_request(self, request: str, parameters: Union[Dict[str, Any], None] = None) -> Dict[str, Any]:
        """Process a high-level user request and orchestrate execution."""
        print(f"? Supervisor processing request: {request}")
        
        # Analyze request and create task
        task = await self._analyze_and_create_task(request, parameters or {})
        self.system_state.active_tasks[task.id] = task
        
        # Create and execute plan
        execution_plan = await self._create_execution_plan(task)
        task.execution_plan = execution_plan
        results = await self._execute_plan(task)
        status_flag = results.get("status")
        if status_flag == "completed":
            task.status = TaskStatus.COMPLETED
        elif status_flag in {"failed", TaskStatus.FAILED.value}:
            task.status = TaskStatus.FAILED
        else:
            task.status = task.status or TaskStatus.PENDING
        
        # Learn from execution
        await self._learn_from_execution(task, results)
        
        return {
            "task_id": task.id,
            "status": task.status.value,
            "results": results,
            "performance": task.performance_metrics.to_dict()
        }
    
    async def _analyze_and_create_task(self, request: str, parameters: Dict[str, Any]) -> Task:
        """Analyze user request and create appropriate task."""
        request_lower = request.lower()
        
        # Determine task type based on keywords
        if "pentest" in request_lower or "penetration test" in request_lower:
            task_type = "penetration_test"
            priority = Priority.HIGH
        elif "scan" in request_lower or "recon" in request_lower:
            task_type = "network_scan"
            priority = Priority.MEDIUM
        elif "web" in request_lower:
            task_type = "web_assessment"
            priority = Priority.MEDIUM
        else:
            task_type = "general_assessment"
            priority = Priority.MEDIUM
        
        # Extract target
        target = parameters.get("target", "localhost")
        
        return Task(
            name=f"{task_type.replace('_', ' ').title()} - {target}",
            description=request,
            task_type=task_type,
            priority=priority,
            parameters={"target": target, "original_request": request, **parameters},
            learning_context=LearningContext(
                algorithm_type="genetic_algorithm",
                parameters={"optimization_target": "efficiency_accuracy_balance"}
            )
        )
    
    async def _create_execution_plan(self, task: Task) -> Any:
        """Create intelligent execution plan for the task."""
        from src.models.core import TaskExecutionPlan
        
        plan_steps = []
        
        if task.task_type == "penetration_test":
            plan_steps = [
                {"step": 1, "name": "Network Reconnaissance", "agent": "network_agent", 
                 "tools": ["nmap_scan", "network_discovery"], "estimated_time": 300},
                {"step": 2, "name": "Web Assessment", "agent": "web_agent", 
                 "tools": ["gobuster_directory", "nikto_scan"], "estimated_time": 600},
                {"step": 3, "name": "Vulnerability Analysis", "agent": "vulnerability_agent", 
                 "tools": ["sqlmap_test"], "estimated_time": 720},
                {"step": 4, "name": "Report Generation", "agent": "report_agent", 
                 "tools": ["generate_report"], "estimated_time": 180}
            ]
        elif task.task_type == "network_scan":
            plan_steps = [
                {"step": 1, "name": "Network Discovery", "agent": "network_agent", 
                 "tools": ["network_discovery", "nmap_scan"], "estimated_time": 240}
            ]
        elif task.task_type == "web_assessment":
            plan_steps = [
                {"step": 1, "name": "Web Reconnaissance", "agent": "web_agent", 
                 "tools": ["gobuster_directory", "web_technology_detection"], "estimated_time": 360},
                {"step": 2, "name": "Vulnerability Scanning", "agent": "web_agent", 
                 "tools": ["nikto_scan", "sqlmap_test"], "estimated_time": 600}
            ]
        return TaskExecutionPlan(
            task_id=task.id,
            steps=plan_steps,
            assigned_agents=[step["agent"] for step in plan_steps],
            estimated_duration=sum(step["estimated_time"] for step in plan_steps)
        )
    
    async def _execute_plan(self, task: Task) -> Dict[str, Any]:
        """Execute the task plan using assigned agents."""
        results = {"steps_completed": [], "findings": [], "errors": [], "execution_time": 0.0}
        
        start_time = datetime.now()
        
        if not task.execution_plan:
            return {"error": "No execution plan available"}
        
        try:
            for step in task.execution_plan.steps:
                step_start = datetime.now()
                print(f"? Executing step {step['step']}: {step['name']}")
                
                step_result = await self._execute_step(step, task.parameters)
                
                step_duration = (datetime.now() - step_start).total_seconds()
                step_result["execution_time"] = step_duration
                results["steps_completed"].append(step_result)
                
                # Extract findings
                if "findings" in step_result:
                    results["findings"].extend(step_result["findings"])
                
                # Handle errors
                if step_result.get("status") == "error":
                    results["errors"].append({
                        "step": step['step'],
                        "error": step_result.get("error", "Unknown error")
                    })
                
                print(f"? Step {step['step']} completed in {step_duration:.2f}s")
        
        except Exception as e:
            results["errors"].append({"error": f"Execution failed: {str(e)}"})
            task.status = TaskStatus.FAILED
        
        total_time = (datetime.now() - start_time).total_seconds()
        results["execution_time"] = total_time
        
        # Update task status and performance
        if not results["errors"]:
            task.status = TaskStatus.COMPLETED
        
        task.performance_metrics = PerformanceMetrics(
            execution_time=total_time,
            success_rate=1.0 if not results["errors"] else 0.0,
            accuracy=0.9,
            error_count=len(results["errors"]),
            confidence_score=0.8
        )
        
        return results
    
    async def _execute_step(self, step: Dict[str, Any], task_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step using the appropriate agent."""
        agent_name = step["agent"]
        tools = step["tools"]
        
        try:
            step_results = []
            
            # Execute each tool in the step
            for tool_name in tools:
                tool_result = await self._simulate_tool_execution(tool_name, task_parameters)
                step_results.append({"tool": tool_name, "result": tool_result})
            
            return {
                "status": "completed",
                "agent": agent_name,
                "tools_executed": step_results,
                "findings": self._extract_findings_from_results(step_results)
            }
        
        except Exception as e:
            return {"status": "error", "agent": agent_name, "error": str(e)}
    
    async def _simulate_tool_execution(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate tool execution for demo purposes."""
        target = parameters.get("target", "localhost")
        
        # Simulate different tool outputs
        if tool_name == "nmap_scan":
            return {
                "status": "completed",
                "target": target,
                "hosts": {
                    target: {
                        "status": "up",
                        "ports": [
                            {"port": 22, "protocol": "tcp", "service": "ssh", "state": "open"},
                            {"port": 80, "protocol": "tcp", "service": "http", "state": "open"},
                            {"port": 443, "protocol": "tcp", "service": "https", "state": "open"}
                        ]
                    }
                }
            }
        elif tool_name == "network_discovery":
            # Ensure target is a valid IP address for the simulated network
            import ipaddress
            try:
                ip = str(ipaddress.ip_address(target))
            except Exception:
                ip = "127.0.0.1"
            return {
                "status": "completed",
                "network": f"{ip}/24",
                "live_hosts": [{"ip": ip, "hostname": ip, "status": "up"}],
                "total_hosts": 1
            }
        elif tool_name == "gobuster_directory":
            return {
                "status": "completed",
                "url": f"http://{target}",
                "discovered_paths": [
                    {"path": "/admin", "status_code": 200, "size": 1234},
                    {"path": "/login.php", "status_code": 200, "size": 567}
                ],
                "total_found": 2
            }
        elif tool_name == "nikto_scan":
            return {
                "status": "completed",
                "url": f"http://{target}",
                "vulnerabilities": [
                    {"id": "OSVDB-3092", "msg": "Server header found", "severity": "info"}
                ],
                "total_vulnerabilities": 1
            }
        elif tool_name == "sqlmap_test":
            return {
                "status": "completed",
                "url": f"http://{target}/login.php",
                "injection_points": [],
                "vulnerable": False
            }
        else:
            return {"status": "completed", "message": f"Tool {tool_name} executed successfully"}
    
    def _extract_findings_from_results(self, step_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract security findings from tool results."""
        findings = []
        
        for tool_result in step_results:
            result = tool_result.get("result", {})
            
            # Extract open ports as findings
            if "hosts" in result:
                for host, host_info in result["hosts"].items():
                    for port in host_info.get("ports", []):
                        if port.get("state") == "open":
                            findings.append({
                                "type": "open_port",
                                "host": host,
                                "port": port["port"],
                                "service": port.get("service", "unknown"),
                                "severity": "info"
                            })
            
            # Extract web vulnerabilities
            if "vulnerabilities" in result:
                for vuln in result["vulnerabilities"]:
                    findings.append({
                        "type": "web_vulnerability",
                        "description": vuln.get("msg", ""),
                        "severity": vuln.get("severity", "info"),
                        "reference": vuln.get("id", "")
                    })
            
            # Extract discovered paths
            if "discovered_paths" in result:
                for path in result["discovered_paths"]:
                    if path.get("status_code") == 200:
                        findings.append({
                            "type": "interesting_path",
                            "path": path["path"],
                            "status_code": path["status_code"],
                            "severity": "info"
                        })
        
        return findings
    
    async def _learn_from_execution(self, task: Task, results: Dict[str, Any]):
        """Learn from task execution to improve future performance."""
        # Create learning data
        findings = results.get("findings")
        steps_completed = results.get("steps_completed")
        findings_count = len(findings) if isinstance(findings, list) else results.get("findings_count", 0)
        steps_count = len(steps_completed) if isinstance(steps_completed, list) else results.get("steps_count", 0)

        learning_data = {
            "task_type": task.task_type,
            "execution_time": results["execution_time"],
            "success": len(results["errors"]) == 0,
            "findings_count": findings_count,
            "steps_count": steps_count
        }
        
        # Update adaptation algorithms
        performance = task.performance_metrics
        
        for algorithm_name, algorithm in self.adaptation_algorithms.items():
            if task.learning_context and task.learning_context.algorithm_type == algorithm_name:
                adaptation_result = algorithm.adapt(task.learning_context, performance)
                self.system_state.learning_insights[f"{algorithm_name}_latest"] = adaptation_result
        
        # Update agent performance history
        for agent_id in self.system_state.agents.keys():
            agent_state = self.system_state.agents[agent_id]
            agent_state.performance_history.append(performance)
            
            # Keep only last 50 performance records
            if len(agent_state.performance_history) > 50:
                agent_state.performance_history = agent_state.performance_history[-50:]
        
        print(f"? Learning completed for task {task.id}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "supervisor_id": self.agent_id,
            "agents": {agent_id: agent.status for agent_id, agent in self.system_state.agents.items()},
            "active_tasks": len(self.system_state.active_tasks),
            "completed_tasks": len(self.system_state.completed_tasks),
            "learning_algorithms": list(self.adaptation_algorithms.keys()),
            "total_decisions": len(self.system_state.supervisor_decisions)
        }


def create_supervisor_agent(agent_id: Optional[str] = None) -> SupervisorAgent:
    """Create and initialize a supervisor agent."""
    return SupervisorAgent(agent_id)
