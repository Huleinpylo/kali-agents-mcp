# Test Configuration for Kali Agents MCP

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

# Test fixtures for common mocks
@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for LLM interactions"""
    mock_client = AsyncMock()
    mock_client.chat.return_value = {
        "message": {
            "content": "Mock LLM response for testing",
            "role": "assistant"
        }
    }
    return mock_client

@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for tool interactions"""
    mock_server = Mock()
    mock_server.get_tools.return_value = {
        "nmap_scan": Mock(),
        "gobuster_scan": Mock(),
        "sqlmap_test": Mock()
    }
    return mock_server

@pytest.fixture
def mock_subprocess():
    """Mock subprocess for tool execution"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Mock tool output"
        mock_run.return_value.stderr = ""
        yield mock_run

@pytest.fixture
def temp_config_file():
    """Create temporary configuration file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
# Test configuration
mcp_servers:
  network:
    host: localhost
    port: 5000
  web:
    host: localhost
    port: 5001

llm:
  model: llama3.2
  host: localhost
  port: 11434

security:
  require_authorization: true
  audit_logging: true
  sandbox_mode: true
""")
        temp_path = f.name
    
    yield temp_path
    os.unlink(temp_path)

@pytest.fixture
def mock_agent_state():
    """Mock agent state for testing"""
    return {
        "messages": [
            {"role": "user", "content": "Test message"},
            {"role": "assistant", "content": "Test response"}
        ],
        "context": {
            "target": "test.example.com",
            "scope": "web",
            "authorization": True
        },
        "results": {},
        "performance_metrics": {
            "execution_time": 1.5,
            "success_rate": 0.95,
            "error_count": 0
        }
    }

@pytest.fixture
def mock_target_environment():
    """Mock target environment for safe testing"""
    return {
        "target": "test.localhost",
        "authorized": True,
        "scope": ["web", "network"],
        "restrictions": {
            "max_ports": 100,
            "timeout": 30,
            "rate_limit": "1/second"
        }
    }

@pytest.fixture
def mock_ml_context():
    """Mock ML algorithm context"""
    return {
        "fuzzy_logic": {
            "task_complexity": 0.7,
            "agent_workload": 0.3,
            "success_probability": 0.85
        },
        "genetic_algorithm": {
            "population_size": 50,
            "mutation_rate": 0.1,
            "generations": 10
        },
        "q_learning": {
            "learning_rate": 0.1,
            "discount_factor": 0.95,
            "exploration_rate": 0.15
        }
    }

# Test database for performance metrics
@pytest.fixture
def mock_performance_db():
    """Mock performance database"""
    return {
        "agents": {
            "network_agent": {
                "total_executions": 150,
                "success_rate": 0.92,
                "avg_execution_time": 2.5,
                "specializations": ["port_scanning", "os_detection"]
            },
            "web_agent": {
                "total_executions": 200,
                "success_rate": 0.88,
                "avg_execution_time": 3.2,
                "specializations": ["directory_enum", "vuln_scanning"]
            }
        },
        "tools": {
            "nmap": {"usage_count": 500, "success_rate": 0.95},
            "gobuster": {"usage_count": 300, "success_rate": 0.87},
            "sqlmap": {"usage_count": 150, "success_rate": 0.75}
        }
    }

# Security test fixtures
@pytest.fixture
def mock_authorization_context():
    """Mock authorization context for security testing"""
    return {
        "user": "test_user",
        "role": "pentester",
        "permissions": ["network_scan", "web_test", "report_generate"],
        "target_authorizations": ["test.localhost", "demo.example.com"],
        "session_id": "test_session_123",
        "expires_at": "2025-12-31T23:59:59Z"
    }

@pytest.fixture
def mock_audit_logger():
    """Mock audit logger for security testing"""
    mock_logger = Mock()
    mock_logger.log_action = Mock()
    mock_logger.log_security_event = Mock()
    mock_logger.log_tool_execution = Mock()
    return mock_logger

# Async test helpers
@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_mock_supervisor():
    """Async mock supervisor agent"""
    supervisor = AsyncMock()
    supervisor.process_user_request.return_value = {
        "status": "completed",
        "plan": ["network_recon", "web_analysis"],
        "results": {"findings": ["open_ports", "web_directories"]},
        "execution_time": 45.2
    }
    return supervisor

# Test data fixtures
@pytest.fixture
def sample_nmap_output():
    """Sample nmap output for parsing tests"""
    return """
# Nmap 7.94 scan initiated
Nmap scan report for test.localhost (127.0.0.1)
Host is up (0.00011s latency).
Not shown: 998 closed ports
PORT     STATE SERVICE    VERSION
22/tcp   open  ssh        OpenSSH 8.9p1 Ubuntu 3ubuntu0.1
80/tcp   open  http       Apache httpd 2.4.52
443/tcp  open  https      Apache httpd 2.4.52
Service detection performed.
"""

@pytest.fixture
def sample_gobuster_output():
    """Sample gobuster output for parsing tests"""
    return """
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://test.localhost
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirb/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Timeout:                 10s
===============================================================
/admin                (Status: 200) [Size: 1234]
/backup               (Status: 403) [Size: 278]
/login                (Status: 200) [Size: 2156]
/uploads              (Status: 301) [Size: 234] [--> http://test.localhost/uploads/]
===============================================================
"""

@pytest.fixture
def sample_sqlmap_output():
    """Sample sqlmap output for parsing tests"""
    return """
[INFO] testing connection to the target URL
[INFO] checking if the target is protected by some kind of WAF/IPS
[INFO] testing if the target URL content is stable
[INFO] target URL content is stable
[INFO] testing if GET parameter 'id' is dynamic
[INFO] GET parameter 'id' appears to be dynamic
[INFO] heuristic (basic) test shows that GET parameter 'id' might be injectable
[INFO] testing for SQL injection on GET parameter 'id'
[INFO] GET parameter 'id' is vulnerable. Do you want to keep testing the others (if any)? [y/N] N
sqlmap identified the following injection point(s) with a total of 46 HTTP(s) requests:
---
Parameter: id (GET)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: id=1 AND 1=1
---
"""

# Performance test fixtures
@pytest.fixture
def performance_benchmarks():
    """Performance benchmarks for testing"""
    return {
        "network_scan": {
            "max_execution_time": 30.0,
            "min_success_rate": 0.90,
            "max_memory_usage": "100MB"
        },
        "web_analysis": {
            "max_execution_time": 60.0,
            "min_success_rate": 0.85,
            "max_memory_usage": "150MB"
        },
        "vulnerability_assessment": {
            "max_execution_time": 120.0,
            "min_success_rate": 0.80,
            "max_memory_usage": "200MB"
        }
    }

# Error simulation fixtures
@pytest.fixture
def mock_network_error():
    """Mock network error for testing error handling"""
    from unittest.mock import Mock
    error = Mock()
    error.side_effect = ConnectionError("Network unreachable")
    return error

@pytest.fixture
def mock_tool_failure():
    """Mock tool failure for testing resilience"""
    from unittest.mock import Mock
    mock_run = Mock()
    mock_run.returncode = 1
    mock_run.stdout = ""
    mock_run.stderr = "Tool execution failed"
    return mock_run

# Test markers for categorization
try:
    import pytest_asyncio  # type: ignore
except Exception:  # pragma: no cover - fallback if plugin unavailable
    pytest_plugins = []
else:
    pytest_plugins = ['pytest_asyncio']

def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "ml: mark test as ML algorithm test"
    )

# Test environment setup
def pytest_sessionstart(session):
    """Setup test environment"""
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["DISABLE_AUTH"] = "true"
    os.environ["MOCK_TOOLS"] = "true"

def pytest_sessionfinish(session, exitstatus):
    """Cleanup test environment"""
    if "TESTING" in os.environ:
        del os.environ["TESTING"]