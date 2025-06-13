"""
Kali Agents Data Models Package

This package contains all data models for the Kali Agents system:
- Core models for agents, tasks, and system state
- Machine learning algorithms for adaptation
- Security findings and vulnerability models
"""

from .core import (
    AgentType,
    TaskStatus,
    Priority,
    Severity,
    CommunicationType,
    PerformanceMetrics,
    LearningContext,
    Tool,
    AgentCapability,
    AgentCommunication,
    TaskExecutionPlan,
    Task,
    AgentState,
    SupervisorDecision,
    SystemState,
    SecurityFinding,
    AdaptationRule,
    create_network_agent_state,
    create_pentest_task
)

from .ml_algorithms import (
    AdaptationAlgorithm,
    FuzzyLogicEngine,
    GeneticAlgorithm,
    QLearningAgent,
    PatternRecognition,
    Individual,
    create_adaptation_algorithm
)

__all__ = [
    # Core enums
    "AgentType",
    "TaskStatus", 
    "Priority",
    "Severity",
    "CommunicationType",
    
    # Core data classes
    "PerformanceMetrics",
    "LearningContext",
    "Tool",
    "AgentCapability",
    "AgentCommunication",
    "TaskExecutionPlan",
    "Task",
    "AgentState",
    "SupervisorDecision",
    "SystemState",
    "SecurityFinding",
    "AdaptationRule",
    
    # Factory functions
    "create_network_agent_state",
    "create_pentest_task",
    
    # ML algorithms
    "AdaptationAlgorithm",
    "FuzzyLogicEngine",
    "GeneticAlgorithm", 
    "QLearningAgent",
    "PatternRecognition",
    "Individual",
    "create_adaptation_algorithm"
]

# Package metadata
__version__ = "0.1.0"
__description__ = "Data models for Kali Agents adaptive orchestration system"
