"""
Kali Agents - "At Your Service"

Intelligent orchestration system for Kali Linux cybersecurity tools using MCP and LangGraph.

This package provides a complete multi-agent system for automating cybersecurity workflows,
including network reconnaissance, web application testing, vulnerability assessment,
digital forensics, and social engineering.

Philosophy: "Kali Agents at Your Service" - Because ethical hackers deserve tools
as intelligent as they are.
"""

__version__ = "0.1.0"
__author__ = "Simon Terrien"
__email__ = "simon.terrien@example.com"
__description__ = "Intelligent orchestration system for Kali Linux cybersecurity tools"

# Package metadata
PACKAGE_NAME = "kali-agents"
PACKAGE_VERSION = __version__
PACKAGE_DESCRIPTION = __description__
PACKAGE_AUTHOR = __author__
PACKAGE_LICENSE = "MIT"

# Agent types
AGENT_TYPES = [
    "supervisor",
    "network", 
    "web",
    "vulnerability",
    "forensic",
    "social",
    "report"
]

# Supported scan types
SCAN_TYPES = [
    "recon",
    "network",
    "web", 
    "vulnerability",
    "forensic",
    "osint",
    "pentest"
]

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__description__",
    "PACKAGE_NAME",
    "PACKAGE_VERSION", 
    "PACKAGE_DESCRIPTION",
    "PACKAGE_AUTHOR",
    "PACKAGE_LICENSE",
    "AGENT_TYPES",
    "SCAN_TYPES",
]
