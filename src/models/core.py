"""
Core data models for Kali Agents adaptive orchestration system.

This module contains the foundational data structures for the intelligent
supervisor-agent architecture with machine learning capabilities.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Callable
from datetime import datetime
from enum import Enum
import json
import uuid


class AgentType(Enum):
    """Types of specialized agents in the system."""
    SUPERVISOR = "supervisor"
    NETWORK = "network"
    WEB = "web"
    VULNERABILITY = "vulnerability"
    FORENSIC = "forensic"
    SOCIAL = "social"
    REPORT = "report"


class TaskStatus(Enum):
    """Status of a task execution."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REQUIRES_ADAPTATION = "requires_adaptation"


class Priority(Enum):
    """Priority levels for tasks and findings."""
    LOW = 1
    MEDIUM = 3
    HIGH = 7
    CRITICAL = 10


class Severity(Enum):
    """Severity levels for vulnerabilities and findings."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CommunicationType(Enum):
    """Types of agent-to-agent communication."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    COLLABORATION = "collaboration"
    FEEDBACK = "feedback"
    LEARNING_UPDATE = "learning_update"


@dataclass
class PerformanceMetrics:
    """Performance metrics for agents and tasks."""
    execution_time: float = 0.0
    success_rate: float = 0.0
    accuracy: float = 0.0
    resource_usage: Dict[str, float] = field(default_factory=dict)
    error_count: int = 0
    improvement_rate: float = 0.0
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_time": self.execution_time,
            "success_rate": self.success_rate,
            "accuracy": self.accuracy,
            "resource_usage": self.resource_usage,
            "error_count": self.error_count,
            "improvement_rate": self.improvement_rate,
            "confidence_score": self.confidence_score
        }


@dataclass
class LearningContext:
    """Context for machine learning and adaptation."""
    algorithm_type: str  # "fuzzy_logic", "genetic_algorithm", "neural_network", etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    training_data: List[Dict[str, Any]] = field(default_factory=list)
    model_state: Dict[str, Any] = field(default_factory=dict)
    last_update: datetime = field(default_factory=datetime.now)
    adaptation_threshold: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm_type": self.algorithm_type,
            "parameters": self.parameters,
            "training_data": self.training_data,
            "model_state": self.model_state,
            "last_update": self.last_update.isoformat(),
            "adaptation_threshold": self.adaptation_threshold
        }


@dataclass
class Tool:
    """Represents a tool that can be used by agents."""
    name: str
    description: str
    category: str
    mcp_server: str
    function_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    estimated_time: float = 0.0
    risk_level: Priority = Priority.LOW
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "mcp_server": self.mcp_server,
            "function_name": self.function_name,
            "parameters": self.parameters,
            "requirements": self.requirements,
            "estimated_time": self.estimated_time,
            "risk_level": self.risk_level.value,
            "dependencies": self.dependencies
        }


@dataclass
class AgentCapability:
    """Represents a capability that an agent possesses."""
    name: str
    description: str
    tools: List[Tool] = field(default_factory=list)
    proficiency_level: float = 0.5  # 0.0 to 1.0
    learning_rate: float = 0.1
    specializations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "tools": [tool.to_dict() for tool in self.tools],
            "proficiency_level": self.proficiency_level,
            "learning_rate": self.learning_rate,
            "specializations": self.specializations
        }


@dataclass 
class AgentCommunication:
    """Represents communication between agents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    receiver_id: str = ""
    message_type: CommunicationType = CommunicationType.REQUEST
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: Priority = Priority.MEDIUM
    requires_response: bool = False
    response_timeout: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "requires_response": self.requires_response,
            "response_timeout": self.response_timeout
        }


@dataclass
class TaskExecutionPlan:
    """Represents an execution plan for a task."""
    task_id: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    assigned_agents: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    fallback_plans: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "steps": self.steps,
            "assigned_agents": self.assigned_agents,
            "dependencies": self.dependencies,
            "estimated_duration": self.estimated_duration,
            "risk_assessment": self.risk_assessment,
            "success_criteria": self.success_criteria,
            "fallback_plans": self.fallback_plans
        }


@dataclass
class Task:
    """Represents a task in the system."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    task_type: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    assigned_agent: Optional[str] = None
    parent_task: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    execution_plan: Optional[TaskExecutionPlan] = None
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    learning_context: Optional[LearningContext] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "assigned_agent": self.assigned_agent,
            "parent_task": self.parent_task,
            "subtasks": self.subtasks,
            "parameters": self.parameters,
            "results": self.results,
            "execution_plan": self.execution_plan.to_dict() if self.execution_plan else None,
            "performance_metrics": self.performance_metrics.to_dict(),
            "learning_context": self.learning_context.to_dict() if self.learning_context else None
        }


@dataclass
class AgentState:
    """Represents the current state of an agent."""
    agent_id: str
    agent_type: AgentType
    status: str = "idle"  # "idle", "busy", "learning", "adapting", "error"
    current_task: Optional[str] = None
    workload: float = 0.0  # 0.0 to 1.0
    capabilities: List[AgentCapability] = field(default_factory=list)
    performance_history: List[PerformanceMetrics] = field(default_factory=list)
    learning_state: Optional[LearningContext] = None
    last_update: datetime = field(default_factory=datetime.now)
    communication_queue: List[AgentCommunication] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "status": self.status,
            "current_task": self.current_task,
            "workload": self.workload,
            "capabilities": [cap.to_dict() for cap in self.capabilities],
            "performance_history": [perf.to_dict() for perf in self.performance_history],
            "learning_state": self.learning_state.to_dict() if self.learning_state else None,
            "last_update": self.last_update.isoformat(),
            "communication_queue": [comm.to_dict() for comm in self.communication_queue]
        }


@dataclass
class SupervisorDecision:
    """Represents a decision made by the supervisor."""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_type: str = ""  # "task_assignment", "resource_allocation", "adaptation", etc.
    context: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    confidence: float = 0.0
    alternatives_considered: List[Dict[str, Any]] = field(default_factory=list)
    expected_outcome: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    feedback_received: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type,
            "context": self.context,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "alternatives_considered": self.alternatives_considered,
            "expected_outcome": self.expected_outcome,
            "timestamp": self.timestamp.isoformat(),
            "feedback_received": self.feedback_received
        }


@dataclass
class SystemState:
    """Represents the overall state of the Kali Agents system."""
    agents: Dict[str, AgentState] = field(default_factory=dict)
    active_tasks: Dict[str, Task] = field(default_factory=dict)
    completed_tasks: List[Task] = field(default_factory=list)
    pending_communications: List[AgentCommunication] = field(default_factory=list)
    system_performance: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    supervisor_decisions: List[SupervisorDecision] = field(default_factory=list)
    learning_insights: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agents": {k: v.to_dict() for k, v in self.agents.items()},
            "active_tasks": {k: v.to_dict() for k, v in self.active_tasks.items()},
            "completed_tasks": [task.to_dict() for task in self.completed_tasks],
            "pending_communications": [comm.to_dict() for comm in self.pending_communications],
            "system_performance": self.system_performance.to_dict(),
            "supervisor_decisions": [dec.to_dict() for dec in self.supervisor_decisions],
            "learning_insights": self.learning_insights
        }


@dataclass
class SecurityFinding:
    """Represents a security finding or vulnerability."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    severity: Severity = Severity.INFO
    category: str = ""
    affected_target: str = ""
    discovery_method: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    remediation: str = ""
    references: List[str] = field(default_factory=list)
    confidence: float = 0.0
    discovered_at: datetime = field(default_factory=datetime.now)
    verified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "category": self.category,
            "affected_target": self.affected_target,
            "discovery_method": self.discovery_method,
            "evidence": self.evidence,
            "remediation": self.remediation,
            "references": self.references,
            "confidence": self.confidence,
            "discovered_at": self.discovered_at.isoformat(),
            "verified": self.verified
        }


@dataclass
class AdaptationRule:
    """Represents a rule for system adaptation."""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    condition: str = ""  # Condition expression
    action: str = ""  # Action to take
    priority: Priority = Priority.MEDIUM
    success_rate: float = 0.0
    usage_count: int = 0
    last_applied: Optional[datetime] = None
    effectiveness_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "condition": self.condition,
            "action": self.action,
            "priority": self.priority.value,
            "success_rate": self.success_rate,
            "usage_count": self.usage_count,
            "last_applied": self.last_applied.isoformat() if self.last_applied else None,
            "effectiveness_score": self.effectiveness_score
        }


# Factory functions for creating common objects

def create_network_agent_state(agent_id: str) -> AgentState:
    """Create a NetworkAgent state with appropriate capabilities."""
    network_tools = [
        Tool(
            name="nmap_scan",
            description="Network port scanning and service detection",
            category="network_reconnaissance",
            mcp_server="network_server",
            function_name="nmap_scan",
            estimated_time=30.0,
            risk_level=Priority.LOW
        ),
        Tool(
            name="masscan_ports",
            description="High-speed port scanning",
            category="network_reconnaissance", 
            mcp_server="network_server",
            function_name="masscan_ports",
            estimated_time=15.0,
            risk_level=Priority.LOW
        ),
        Tool(
            name="network_discovery",
            description="Discover live hosts on network",
            category="network_reconnaissance",
            mcp_server="network_server", 
            function_name="network_discovery",
            estimated_time=20.0,
            risk_level=Priority.LOW
        )
    ]
    
    network_capability = AgentCapability(
        name="network_reconnaissance",
        description="Network scanning and discovery capabilities",
        tools=network_tools,
        proficiency_level=0.8,
        specializations=["port_scanning", "service_detection", "network_mapping"]
    )
    
    return AgentState(
        agent_id=agent_id,
        agent_type=AgentType.NETWORK,
        capabilities=[network_capability],
        learning_state=LearningContext(
            algorithm_type="fuzzy_logic",
            parameters={"scan_intensity": 0.7, "accuracy_threshold": 0.8}
        )
    )


def create_pentest_task(target: str, scope: str = "full") -> Task:
    """Create a penetration testing task."""
    return Task(
        name=f"Penetration Test - {target}",
        description=f"Comprehensive security assessment of {target}",
        task_type="penetration_test",
        priority=Priority.HIGH,
        parameters={
            "target": target,
            "scope": scope,
            "methodology": "OWASP",
            "compliance_requirements": ["PCI-DSS", "ISO27001"]
        },
        learning_context=LearningContext(
            algorithm_type="genetic_algorithm",
            parameters={"population_size": 50, "mutation_rate": 0.1}
        )
    )
