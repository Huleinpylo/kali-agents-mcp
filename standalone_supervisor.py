"""
Standalone Supervisor Agent for Demo Purposes

This is a simplified version of the supervisor that works independently
for demonstration purposes when the full system isn't available.

⚠️  Developers and AI copilots: read `AGENTS.md` (workflow expectations) and
`CONTEXT.MD` (Pydantic AI reference) before extending this module so demos stay
aligned with production conventions.
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(Enum):
    NETWORK = "network"
    WEB = "web"
    VULNERABILITY = "vulnerability"
    FORENSIC = "forensic"
    SOCIAL = "social"
    REPORT = "report"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceMetrics:
    execution_time: float = 0.0
    success_rate: float = 0.0
    accuracy: float = 0.0
    error_count: int = 0
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_time": self.execution_time,
            "success_rate": self.success_rate,
            "accuracy": self.accuracy,
            "error_count": self.error_count,
            "confidence_score": self.confidence_score
        }


@dataclass
class AgentState:
    agent_id: str
    agent_type: AgentType
    status: str = "ready"
    performance_metrics: PerformanceMetrics = None
    
    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = PerformanceMetrics(
                success_rate=0.85 + (hash(self.agent_id) % 15) / 100,  # Random performance
                accuracy=0.80 + (hash(self.agent_id) % 20) / 100,
                confidence_score=0.75 + (hash(self.agent_id) % 25) / 100
            )


@dataclass
class SystemState:
    agents: Dict[str, AgentState] = None
    active_tasks: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.agents is None:
            self.agents = {}
        if self.active_tasks is None:
            self.active_tasks = {}


class StandaloneSupervisor:
    """Standalone supervisor for demo purposes."""
    
    def __init__(self, agent_id: Optional[str] = None):
        self.agent_id = agent_id or f"supervisor_{uuid.uuid4().hex[:8]}"
        self.system_state = SystemState()
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize demo agents."""
        agent_configs = [
            ("network_agent", AgentType.NETWORK),
            ("web_agent", AgentType.WEB),
            ("vulnerability_agent", AgentType.VULNERABILITY),
            ("forensic_agent", AgentType.FORENSIC),
            ("social_agent", AgentType.SOCIAL),
            ("report_agent", AgentType.REPORT)
        ]
        
        for agent_id, agent_type in agent_configs:
            self.system_state.agents[agent_id] = AgentState(
                agent_id=agent_id,
                agent_type=agent_type
            )
    
    async def process_user_request(self, request: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user request with realistic simulation."""
        if parameters is None:
            parameters = {}
            
        print(f"🧠 Supervisor processing request: {request}")
        
        # Simulate analysis time
        await asyncio.sleep(0.5)
        
        # Determine task type
        request_lower = request.lower()
        if "pentest" in request_lower or "penetration test" in request_lower:
            return await self._simulate_pentest(parameters)
        elif "scan" in request_lower or "recon" in request_lower:
            return await self._simulate_network_scan(parameters)
        elif "web" in request_lower:
            return await self._simulate_web_assessment(parameters)
        elif "osint" in request_lower:
            return await self._simulate_osint(parameters)
        elif "forensic" in request_lower:
            return await self._simulate_forensics(parameters)
        else:
            return await self._simulate_general_assessment(parameters)
    
    async def _simulate_pentest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate penetration test execution."""
        target = params.get("target", "demo.testfire.net")
        
        phases = [
            {"name": "Network Reconnaissance", "duration": 3.2, "agent": "network_agent"},
            {"name": "Web Application Testing", "duration": 4.1, "agent": "web_agent"},
            {"name": "Vulnerability Assessment", "duration": 3.8, "agent": "vulnerability_agent"},
            {"name": "Report Generation", "duration": 1.5, "agent": "report_agent"}
        ]
        
        results = {"phases": [], "findings": [], "total_time": 0}
        
        for phase in phases:
            await asyncio.sleep(phase["duration"] / 10)  # Scaled for demo
            
            phase_result = {
                "name": phase["name"],
                "agent": phase["agent"],
                "duration": phase["duration"],
                "status": "completed",
                "findings": await self._generate_findings(phase["name"], target)
            }
            
            results["phases"].append(phase_result)
            results["findings"].extend(phase_result["findings"])
            results["total_time"] += phase["duration"]
        
        return {
            "status": "completed",
            "task_type": "penetration_test",
            "target": target,
            "results": results,
            "performance": PerformanceMetrics(
                execution_time=results["total_time"],
                success_rate=0.94,
                accuracy=0.89,
                confidence_score=0.92
            ).to_dict()
        }
    
    async def _simulate_network_scan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate network scanning."""
        target = params.get("target", "192.168.1.0/24")
        
        await asyncio.sleep(1.0)  # Simulate scan time
        
        findings = [
            f"Host {target.split('/')[0] if '/' in target else target} is alive",
            "Open ports: 22/ssh, 80/http, 443/https",
            "OS Detection: Linux 3.x-4.x (96% confidence)",
            "Service versions detected for all open ports"
        ]
        
        return {
            "status": "completed",
            "task_type": "network_scan",
            "target": target,
            "results": {
                "findings": findings,
                "hosts_discovered": 1,
                "ports_found": 3,
                "execution_time": 2.3
            },
            "performance": PerformanceMetrics(
                execution_time=2.3,
                success_rate=0.97,
                accuracy=0.94,
                confidence_score=0.91
            ).to_dict()
        }
    
    async def _simulate_web_assessment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate web application assessment."""
        url = params.get("url", "https://demo.testfire.net")
        
        await asyncio.sleep(1.5)  # Simulate assessment time
        
        findings = [
            "Directory found: /admin (403 Forbidden)",
            "Directory found: /backup (200 OK)",
            "Potential SQL injection in login form",
            "Technology stack: Apache 2.4.x, PHP 7.x, MySQL"
        ]
        
        return {
            "status": "completed",
            "task_type": "web_assessment",
            "target": url,
            "results": {
                "findings": findings,
                "vulnerabilities": 2,
                "directories_found": 2,
                "execution_time": 3.7
            },
            "performance": PerformanceMetrics(
                execution_time=3.7,
                success_rate=0.91,
                accuracy=0.87,
                confidence_score=0.89
            ).to_dict()
        }
    
    async def _simulate_osint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate OSINT research."""
        target = params.get("target", "John Doe")
        
        await asyncio.sleep(1.2)  # Simulate research time
        
        findings = [
            f"Social media profiles found for {target}",
            "LinkedIn profile with company information",
            "Email patterns discovered: first.last@company.com",
            "Phone number format identified: +1-555-XXX-XXXX"
        ]
        
        return {
            "status": "completed",
            "task_type": "osint_research",
            "target": target,
            "results": {
                "findings": findings,
                "profiles_found": 3,
                "contact_info": 2,
                "execution_time": 2.8
            },
            "performance": PerformanceMetrics(
                execution_time=2.8,
                success_rate=0.88,
                accuracy=0.85,
                confidence_score=0.87
            ).to_dict()
        }
    
    async def _simulate_forensics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate forensic analysis."""
        target = params.get("target", "memory_dump.mem")
        
        await asyncio.sleep(2.0)  # Simulate analysis time
        
        findings = [
            "Suspicious process detected: malware.exe",
            "Network connections to suspicious IPs",
            "Registry modifications found",
            "File system artifacts indicate data exfiltration"
        ]
        
        return {
            "status": "completed",
            "task_type": "forensic_analysis",
            "target": target,
            "results": {
                "findings": findings,
                "artifacts_found": 15,
                "iocs_discovered": 4,
                "execution_time": 4.2
            },
            "performance": PerformanceMetrics(
                execution_time=4.2,
                success_rate=0.93,
                accuracy=0.91,
                confidence_score=0.94
            ).to_dict()
        }
    
    async def _simulate_general_assessment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate general security assessment."""
        target = params.get("target", "system")
        
        await asyncio.sleep(1.0)
        
        findings = [
            "Security assessment completed",
            "Multiple security issues identified",
            "Recommendations generated",
            "Report prepared for review"
        ]
        
        return {
            "status": "completed",
            "task_type": "general_assessment",
            "target": target,
            "results": {
                "findings": findings,
                "issues_found": 5,
                "recommendations": 8,
                "execution_time": 1.8
            },
            "performance": PerformanceMetrics(
                execution_time=1.8,
                success_rate=0.90,
                accuracy=0.86,
                confidence_score=0.88
            ).to_dict()
        }
    
    async def _generate_findings(self, phase_name: str, target: str) -> List[str]:
        """Generate realistic findings for each phase."""
        findings_map = {
            "Network Reconnaissance": [
                f"Host {target} is alive (ping response)",
                "Open ports: 22/ssh, 80/http, 443/https",
                "OS Detection: Linux 3.x-4.x (96% confidence)",
                "Service versions detected for all open ports"
            ],
            "Web Application Testing": [
                "Directory found: /admin (403 Forbidden)",
                "Directory found: /backup (200 OK)",
                "Potential vulnerability: SQL injection in login form",
                "Technology stack: Apache 2.4.x, PHP 7.x, MySQL"
            ],
            "Vulnerability Assessment": [
                "Confirmed: SQL injection in /login.php parameter 'username'",
                "Database: MySQL 5.7.x detected",
                "Privilege escalation possible via weak sudo configuration",
                "3 critical vulnerabilities identified"
            ],
            "Report Generation": [
                "Executive summary generated",
                "Technical findings documented",
                "Risk assessment completed",
                "Remediation recommendations provided"
            ]
        }
        
        return findings_map.get(phase_name, ["Phase completed successfully"])


def create_supervisor_agent(agent_id: Optional[str] = None) -> StandaloneSupervisor:
    """Create standalone supervisor for demo."""
    return StandaloneSupervisor(agent_id)
