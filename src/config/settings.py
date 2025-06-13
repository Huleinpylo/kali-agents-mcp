import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# MCP Server configurations
MCP_SERVERS = {
    "data": {
        "host": os.getenv("DATA_SERVER_HOST", "localhost"),
        "port": int(os.getenv("DATA_SERVER_PORT", 5000)),
        "transport": os.getenv("MCP_TRANSPORT", "http")
    },
    "network": {
        "host": os.getenv("DATA_SERVER_HOST", "localhost"),
        "port": int(os.getenv("NETWORK_SERVER_PORT", 5001)),
        "transport": os.getenv("MCP_TRANSPORT", "http")
    },
    "web": {
        "host": os.getenv("DATA_SERVER_HOST", "localhost"),
        "port": int(os.getenv("WEB_SERVER_PORT", 5002)),
        "transport": os.getenv("MCP_TRANSPORT", "http")
    },
    "vulnerability": {
        "host": os.getenv("DATA_SERVER_HOST", "localhost"),
        "port": int(os.getenv("VULN_SERVER_PORT", 5003)),
        "transport": os.getenv("MCP_TRANSPORT", "http")
    },
    "forensic": {
        "host": os.getenv("DATA_SERVER_HOST", "localhost"),
        "port": int(os.getenv("FORENSIC_SERVER_PORT", 5004)),
        "transport": os.getenv("MCP_TRANSPORT", "http")
    },
    "social": {
        "host": os.getenv("DATA_SERVER_HOST", "localhost"),
        "port": int(os.getenv("SOCIAL_SERVER_PORT", 5005)),
        "transport": os.getenv("MCP_TRANSPORT", "http")
    },
    "report": {
        "host": os.getenv("DATA_SERVER_HOST", "localhost"),
        "port": int(os.getenv("REPORT_SERVER_PORT", 5006)),
        "transport": os.getenv("MCP_TRANSPORT", "http")
    }
}

# LLM configuration
LLM_CONFIG = {
    "model": os.getenv("LLM_MODEL", "llama3.2"),
    "host": os.getenv("LLM_HOST", "localhost"),
    "port": int(os.getenv("LLM_PORT", 11434)),
    "base_url": f"http://{os.getenv('LLM_HOST', 'localhost')}:{os.getenv('LLM_PORT', 11434)}"
}

# Kali Tools Configuration
KALI_TOOLS = {
    "nmap": os.getenv("NMAP_PATH", "/usr/bin/nmap"),
    "gobuster": os.getenv("GOBUSTER_PATH", "/usr/bin/gobuster"),
    "sqlmap": os.getenv("SQLMAP_PATH", "/usr/bin/sqlmap"),
    "nikto": os.getenv("NIKTO_PATH", "/usr/bin/nikto"),
    "dirb": os.getenv("DIRB_PATH", "/usr/bin/dirb"),
    "masscan": os.getenv("MASSCAN_PATH", "/usr/bin/masscan"),
    "searchsploit": os.getenv("SEARCHSPLOIT_PATH", "/usr/bin/searchsploit"),
}

# Wordlists Configuration
WORDLISTS = {
    "common": os.getenv("WORDLIST_COMMON", "/usr/share/wordlists/dirb/common.txt"),
    "big": os.getenv("WORDLIST_BIG", "/usr/share/wordlists/dirb/big.txt"),
    "rockyou": os.getenv("WORDLIST_ROCKYOU", "/usr/share/wordlists/rockyou.txt"),
}

# Metasploit Configuration
METASPLOIT_CONFIG = {
    "host": os.getenv("MSF_RPC_HOST", "localhost"),
    "port": int(os.getenv("MSF_RPC_PORT", 55553)),
    "user": os.getenv("MSF_RPC_USER", "msf"),
    "password": os.getenv("MSF_RPC_PASS", "password"),
}

# Burp Suite Configuration
BURP_CONFIG = {
    "host": os.getenv("BURP_API_HOST", "localhost"),
    "port": int(os.getenv("BURP_API_PORT", 1337)),
    "api_key": os.getenv("BURP_API_KEY", ""),
}

# Report Configuration
REPORT_CONFIG = {
    "output_dir": Path(os.getenv("REPORT_OUTPUT_DIR", "./reports")),
    "template_dir": Path(os.getenv("REPORT_TEMPLATE_DIR", "./templates")),
    "company_name": os.getenv("COMPANY_NAME", "Your Company"),
    "pentester_name": os.getenv("PENTESTER_NAME", "Your Name"),
}

# Security Configuration
SECURITY_CONFIG = {
    "api_key_secret": os.getenv("API_KEY_SECRET", "your_secret_key_here"),
    "jwt_secret": os.getenv("JWT_SECRET", "your_jwt_secret_here"),
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "file": Path(os.getenv("LOG_FILE", "./logs/kali-agents.log")),
}

# Database Configuration
DATABASE_CONFIG = {
    "type": os.getenv("DB_TYPE", "sqlite"),
    "path": Path(os.getenv("DB_PATH", "./data/kali-agents.db")),
}

# Network Configuration
NETWORK_CONFIG = {
    "default_timeout": int(os.getenv("DEFAULT_TIMEOUT", 30)),
    "max_concurrent_scans": int(os.getenv("MAX_CONCURRENT_SCANS", 5)),
    "rate_limit_delay": float(os.getenv("RATE_LIMIT_DELAY", 1.0)),
}

# OSINT Configuration
OSINT_CONFIG = {
    "shodan_api_key": os.getenv("SHODAN_API_KEY", ""),
    "virustotal_api_key": os.getenv("VIRUSTOTAL_API_KEY", ""),
    "censys_api_id": os.getenv("CENSYS_API_ID", ""),
    "censys_api_secret": os.getenv("CENSYS_API_SECRET", ""),
}

# Social Engineering Configuration
SOCIAL_CONFIG = {
    "set_config_path": Path(os.getenv("SET_CONFIG_PATH", "/etc/setoolkit/set.config")),
    "gophish_api_key": os.getenv("GOPHISH_API_KEY", ""),
    "gophish_url": os.getenv("GOPHISH_URL", "https://localhost:3333"),
}

# Development Configuration
DEVELOPMENT_CONFIG = {
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "development_mode": os.getenv("DEVELOPMENT_MODE", "false").lower() == "true",
}
