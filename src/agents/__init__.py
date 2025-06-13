"""
Kali Agents Package

This package contains all the intelligent agents for the Kali Agents system:
- Supervisor Agent: Central orchestrator with ML-based decision making
- Specialized Agents: Domain-specific agents for different security tasks
"""

from .supervisor import SupervisorAgent, create_supervisor_agent

__all__ = [
    "SupervisorAgent",
    "create_supervisor_agent"
]

# Package metadata
__version__ = "0.1.0"
__description__ = "Intelligent agents for Kali Agents orchestration system"
