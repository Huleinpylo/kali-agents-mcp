"""
Kali Agents Configuration Package

This package contains all configuration settings and constants for the Kali Agents system.
"""

from .settings import (
    MCP_SERVERS,
    LLM_CONFIG,
    KALI_TOOLS,
    WORDLISTS,
    METASPLOIT_CONFIG,
    BURP_CONFIG,
    REPORT_CONFIG,
    SECURITY_CONFIG,
    LOGGING_CONFIG,
    DATABASE_CONFIG,
    NETWORK_CONFIG,
    OSINT_CONFIG,
    SOCIAL_CONFIG,
    DEVELOPMENT_CONFIG,
    PROJECT_ROOT,
)

__all__ = [
    "MCP_SERVERS",
    "LLM_CONFIG", 
    "KALI_TOOLS",
    "WORDLISTS",
    "METASPLOIT_CONFIG",
    "BURP_CONFIG",
    "REPORT_CONFIG",
    "SECURITY_CONFIG",
    "LOGGING_CONFIG",
    "DATABASE_CONFIG",
    "NETWORK_CONFIG",
    "OSINT_CONFIG",
    "SOCIAL_CONFIG",
    "DEVELOPMENT_CONFIG",
    "PROJECT_ROOT",
]
