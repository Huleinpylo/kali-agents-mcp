# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Kali Agents** is an intelligent orchestration system for Kali Linux cybersecurity tools using MCP (Model Context Protocol) and Pydantic AI. The system uses a supervisor-agent architecture with ML-based adaptive learning (fuzzy logic, genetic algorithms, Q-learning) to coordinate security assessments.

**Technology Stack**: Python 3.10+, FastMCP 2.8.0, Pydantic AI (in refactoring to this), SQLite, asyncio

**Current Status**: Refactoring to MCP architecture v2 (branch: `refactor/mcp-architecture-v2`)

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Testing
```bash
# Run all tests with coverage (enforces 80% minimum)
./test.sh

# Run tests manually with coverage
pytest --cov=src --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_supervisor_agent.py -v

# Run with markers
pytest -m security  # Run only security tests
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Run only integration tests

# Generate HTML coverage report
pytest --cov=src --cov-report=html:htmlcov
# View: open htmlcov/index.html
```

**Coverage Requirements**: 80% minimum (configured in `pyproject.toml`), warnings treated as errors

### Code Quality
```bash
# Format code (Black + isort)
black src tests
isort src tests

# Lint
flake8 src tests
mypy src

# Security scan
bandit -r src -f json -o bandit_report.json

# All quality checks
black src tests && isort src tests && flake8 src tests && mypy src && bandit -r src
```

### Running the System
```bash
# Start MCP data server (SQLite-backed)
python -m src.mcp_servers.data_server

# CLI commands
kali-agents recon --target 192.168.1.0/24
kali-agents web --url https://example.com --deep
kali-agents pentest --target example.com --scope full
kali-agents status  # System status
kali-agents interactive  # Interactive mode
kali-agents demo  # Run demonstration
```

## Architecture

### Core Components

**Supervisor Agent** (`src/agents/supervisor.py`)
- Main orchestrator coordinating all specialized agents
- Uses ML algorithms (fuzzy logic, genetic algorithms, Q-learning) for task assignment
- Creates execution plans and learns from results
- Entry point: `SupervisorAgent.process_user_request(request, parameters)`

**MCP Servers** (`src/mcp_servers/`)
- `network_server.py`: Network reconnaissance (nmap, masscan, zmap)
- `web_server.py`: Web application testing (gobuster, nikto)
- `data_server.py`: SQLite persistence for scan results
- Built with FastMCP, expose security tools as MCP tools
- Tools decorated with `@mcp.tool` and use `Context` for logging

**Data Models** (`src/models/`)
- `core.py`: Pydantic models for system state (AgentState, Task, SystemState, etc.)
- `ml_algorithms.py`: ML implementations (fuzzy logic, genetic algorithms, Q-learning)
- All models use dataclasses with type hints

**CLI** (`src/cli/main.py`)
- Typer-based CLI with rich terminal output
- Commands: `recon`, `web`, `pentest`, `osint`, `forensics`, `status`, `interactive`
- Natural language support in interactive mode

### Agent Architecture

**Specialized Agents** (6 types defined in architecture):
1. **Network Agent**: nmap, masscan, zmap, netdiscover
2. **Web Agent**: gobuster, nikto, burp suite, wpscan
3. **Vulnerability Agent**: sqlmap, metasploit, searchsploit, nuclei (not yet implemented)
4. **Forensic Agent**: volatility, autopsy, binwalk, wireshark (not yet implemented)
5. **Social Agent**: SET, maltego, theHarvester, shodan (not yet implemented)
6. **Report Agent**: Automated penetration testing reports (not yet implemented)

**Task Execution Flow**:
1. User request → Supervisor analyzes → Creates Task
2. Supervisor creates TaskExecutionPlan with steps
3. Each step assigns agent + tools + estimated time
4. Supervisor executes plan sequentially
5. Results parsed, findings extracted
6. Learning algorithms updated based on performance

### MCP Server Patterns

**Security-Critical Patterns**:
```python
# ALWAYS use subprocess arrays, NEVER shell=True
result = subprocess.run(
    ["nmap", "-sV", target],  # Array, not string
    capture_output=True,
    text=True,
    timeout=300  # Always set timeout
)

# ALWAYS validate inputs with constraints
@mcp.tool
async def tool_name(
    target: str,  # Validate in function
    ctx: Optional[Context] = None  # Context for logging
) -> Dict[str, Any]:
    # Input validation BEFORE subprocess
    if not is_valid_target(target):
        raise ValueError("Invalid target")
```

**Subprocess Security**:
- NEVER use `shell=True` - creates command injection risk
- Build commands as lists: `["nmap", target]` not `f"nmap {target}"`
- Always validate user inputs before subprocess calls
- Set timeouts to prevent DoS
- Capture output, don't pipe to shell

**Parser Patterns**:
- Use `defusedxml` for XML parsing (protects against billion laughs)
- JSON: standard `json` module is safe
- Text: regex with `re.compile()`, handle ANSI escape codes
- Always handle partial/malformed outputs gracefully

## Critical Guidelines

### Security

**Input Validation**:
- All MCP tool parameters must be validated BEFORE subprocess calls
- Use IP address validation for network targets
- Validate port ranges (1-65535)
- Reject special characters that could enable injection
- Path validation: ensure no traversal (`..`, absolute paths outside scope)

**Authorized Testing Only**:
- All security tools require explicit authorization
- CLI confirms authorization for destructive operations
- Document authorized use requirements
- Never bypass security confirmations

### Testing Requirements

**Test Structure**:
- Mirror source tree: `tests/test_supervisor_agent.py` for `src/agents/supervisor.py`
- Use markers: `@pytest.mark.security`, `@pytest.mark.integration`, `@pytest.mark.slow`
- 80% coverage minimum (enforced by CI)
- Security tests mandatory for all MCP tools

**Test Patterns**:
```python
# Mock subprocess calls
@patch('subprocess.run')
def test_tool(mock_subprocess):
    mock_subprocess.return_value = Mock(returncode=0, stdout="output")
    # Test without calling real tools

# Security test: command injection
@pytest.mark.security
def test_rejects_injection():
    with pytest.raises(ValueError):
        await tool(target="192.168.1.1; rm -rf /")

# Async tests
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result["success"]
```

### Code Quality Standards

- **Type hints**: Required for all functions (`mypy --strict`)
- **Formatting**: Black (88 chars), isort (black profile)
- **Docstrings**: Required for all public functions/classes
- **Error handling**: Never silent failures, log with loguru
- **Async/await**: Use for I/O operations, MCP tools, database

### ML Integration

**Algorithms** (`src/models/ml_algorithms.py`):
- **Fuzzy Logic**: Risk assessment with linguistic variables
- **Genetic Algorithms**: Scan strategy optimization
- **Q-Learning**: Adaptive tool selection

**Usage Pattern**:
```python
# Create algorithm
algo = create_adaptation_algorithm("fuzzy_logic", {"rules": rules})

# Adapt based on performance
result = algo.adapt(learning_context, performance_metrics)

# Update agent state
agent.learning_state.model_state = result
```

## Claude Code Specialized Agents

This repository has specialized Claude Code agents in `.claude/agents/`:

1. **mcp-security-validator**: Validates MCP security (use before merging MCP changes)
2. **parser-generator**: Generates security tool output parsers with tests
3. **pydantic-agent-builder**: Builds agents following Pydantic AI patterns
4. **coverage-enforcer**: Ensures 80%+ test coverage
5. **security-docs-generator**: Generates penetration testing reports and documentation

**See `SPECIALIZED_AGENTS.md` for complete usage guide.**

## Configuration

**Environment Variables** (`.env`):
- `DB_PATH`: SQLite database path (default: `data/kali_agents.db`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- Additional configs in `src/config/settings.py`

**Tool Paths** (`src/config/settings.py`):
```python
KALI_TOOLS = {
    "nmap": "/usr/bin/nmap",
    "masscan": "/usr/bin/masscan",
    "gobuster": "/usr/bin/gobuster",
    # ... etc
}
```

## Important Files

- `AGENTS.md`: Day-to-day development guidelines, structure, testing
- `CONTEXT.MD`: Pydantic AI reference documentation
- `SPECIALIZED_AGENTS.md`: Claude Code agent usage guide
- `CONTRIBUTING.md`: Contribution workflow
- `pyproject.toml`: All tool configurations (pytest, black, mypy, bandit)
- `.env.example`: Example environment configuration

## Common Pitfalls

1. **Command Injection**: Always use subprocess arrays, never `shell=True`
2. **Coverage Gaps**: Run coverage before committing, CI enforces 80%
3. **Missing Type Hints**: `mypy` will fail, all functions need types
4. **Async/Sync Mixing**: MCP tools are async, use `await` properly
5. **Hard-coded Paths**: Use `KALI_TOOLS` config, tools may be in different locations
6. **Missing Authorization**: Security operations must confirm authorization first
7. **Unhandled Errors**: Always handle subprocess failures, network timeouts

## Workflow for Adding MCP Tools

1. **Security Review**: Use `mcp-security-validator` agent to review security
2. **Implementation**: Add tool to appropriate server in `src/mcp_servers/`
3. **Input Validation**: Validate ALL parameters before subprocess
4. **Parser**: Use `parser-generator` agent to create output parser
5. **Tests**: Use `coverage-enforcer` agent to generate comprehensive tests
6. **Documentation**: Use `security-docs-generator` agent to document tool
7. **Coverage Check**: Run `pytest --cov` to verify 80%+
8. **Quality Check**: Run `black`, `isort`, `flake8`, `mypy`, `bandit`

## Branch Context

Currently on `refactor/mcp-architecture-v2` - refactoring to use Pydantic AI framework patterns while maintaining FastMCP for tool integration. Supervisor agent uses direct Pydantic AI patterns, specialized agents will follow same architecture.
