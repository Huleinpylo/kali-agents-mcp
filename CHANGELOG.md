# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### MCP Server Implementations (Critical Priority #1 - COMPLETE)

- **Vulnerability Server** (`src/mcp_servers/vulnerability_server.py`, 548 lines)
  - SQLMap integration for SQL injection testing with comprehensive options
  - Nuclei fast vulnerability scanning with template-based detection
  - SearchSploit exploit database search (offline)
  - Metasploit module search functionality
  - 4 dedicated output parsers for structured data extraction
  - 62 comprehensive tests with 96% code coverage
  - Complete API documentation in `docs/vulnerability-server-api.md`

- **Forensic Server** (`src/mcp_servers/forensic_server.py`, 679 lines)
  - Volatility 3 memory forensics and dump analysis
  - Binwalk firmware and binary analysis with signature detection
  - TShark network traffic PCAP analysis (Wireshark CLI)
  - Foremost file carving from disk images
  - Strings extraction with pattern analysis (URLs, emails, IPs, keywords)
  - 5 dedicated output parsers with intelligent analysis
  - 56 comprehensive tests with 90%+ code coverage
  - Complete API documentation in `docs/forensic-server-api.md`

- **Social Server** (`src/mcp_servers/social_server.py`, 563 lines)
  - theHarvester OSINT gathering from 23+ sources
  - Shodan search and host lookup via API
  - Recon-ng integration (stub for interactive tool)
  - SpiderFoot OSINT automation (stub for web-based tool)
  - Result deduplication and aggregation
  - Domain and IP address validation
  - API key management for external services

- **Report Server** (`src/mcp_servers/report_server.py`, 558 lines)
  - Professional PDF report generation with ReportLab
  - HTML report generation with Jinja2 templates
  - Auto-generated executive summaries from findings
  - CVSS v3.1 scoring support
  - 4 template types (default, executive, technical, compliance)
  - Severity charts and statistics
  - In-memory report storage with UUID-based identification

#### Claude Code Specialized Agents

- **mcp-security-validator** (`.claude/agents/`) - Validates MCP server security implementations
- **parser-generator** (`.claude/agents/`) - Generates output parsers for security tools
- **pydantic-agent-builder** (`.claude/agents/`) - Builds agents following Pydantic AI patterns
- **coverage-enforcer** (`.claude/agents/`) - Ensures 80%+ test coverage requirements
- **security-docs-generator** (`.claude/agents/`) - Generates professional security documentation
- **SPECIALIZED_AGENTS.md** - Complete usage guide for all specialized agents

#### Documentation

- `CLAUDE.md` - Comprehensive project guide for Claude Code development
- `IMPLEMENTATION_SUMMARY.md` - Detailed summary of Critical Priority #1 implementation
- `docs/vulnerability-server-api.md` - Complete Vulnerability Server API reference
- `docs/forensic-server-api.md` - Complete Forensic Server API reference
- `plan/01-critical-priorities.md` - Structured improvement plan
- Repository memory/context docs (`AGENTS.md`, `CONTEXT.MD`) for AI assistant workflows

#### Testing

- 118+ total test cases across all MCP servers
- 25+ dedicated security tests for command injection, path traversal, input validation
- 93%+ average code coverage across all tested servers
- Comprehensive test fixtures and mocks for subprocess calls
- `@pytest.mark.security` and `@pytest.mark.asyncio` decorators for test organization
- `tests/test_vulnerability_server.py` - 62 tests, 96% coverage
- `tests/test_forensic_server.py` - 56 tests, 90%+ coverage

#### Configuration & Dependencies

- Added `nuclei` and `msfconsole` paths to `src/config/settings.py`
- Added `shodan` library to `requirements.txt` for OSINT integration
- Environment variable configurations for all MCP servers
- REST API scaffolding (FastAPI) for network and web scanning

#### Dependency Management (Critical Priority #3 - COMPLETE)

- **Pinned Dependencies**: Exact version pins in `requirements.txt` for reproducible builds
  - 28 production dependencies with exact versions
  - Clear categorization (Core MCP, Web Framework, Security Tools, etc.)
  - Python 3.9+ compatibility

- **Development Dependencies**: Created `requirements-dev.txt` with exact pins
  - Includes production dependencies via `-r requirements.txt`
  - 19 development tools (testing, linting, security, docs)
  - Version pins for black (25.1.0), pytest (8.4.0), mypy (1.16.1), etc.

- **Flexible Ranges**: Updated `pyproject.toml` with version ranges
  - Upper bounds to prevent major version breakage (e.g., `>=2.8.0,<3.0.0`)
  - Suitable for library consumers and downstream projects
  - Updated optional dependencies (dev, security, docs)

- **Documentation**: Created `docs/dependency-management.md`
  - Complete dependency management strategy
  - Monthly update process documented
  - Security update protocol (immediate response for CVEs)
  - Troubleshooting guide for common issues
  - Best practices for contributors and maintainers

- **CI/CD Integration**: Updated workflows for pinned dependencies
  - Test workflows use exact pins from requirements.txt
  - Monthly dependency check creates GitHub issues (automated reminder)

#### Development Workflow Improvements (Quick Wins)

- **Makefile**: Comprehensive development commands (150+ commands)
  - Installation targets: `make install`, `make install-dev`, `make setup-hooks`
  - Testing targets: `make test`, `make test-unit`, `make test-security`, `make test-coverage`
  - Code quality: `make lint`, `make format`, `make security-scan`
  - Server execution: `make run-*-server` for all MCP servers
  - CI simulation: `make ci` for local pipeline testing
  - Docker support: `make docker-build`, `make docker-run`

- **.pre-commit-config.yaml**: Enhanced pre-commit hooks
  - Updated versions (black 25.1.0, mypy 1.16.1, flake8 7.1.1)
  - Security hooks: bandit, detect-secrets, gitleaks, ggshield
  - Code quality hooks: black, isort, ruff, flake8
  - Comprehensive file checks and validation

- **.editorconfig**: Editor consistency configuration
  - Python (4 spaces), YAML (2 spaces), JSON (2 spaces) settings
  - Makefile tab enforcement
  - Markdown, Shell, Docker, TOML support
  - Consistent line endings and charset (UTF-8, LF)

- **Enhanced API Health Checks**:
  - `/health` endpoint with version, timestamp, service checks
  - `/version` endpoint with build info and git commit
  - Suitable for monitoring and load balancers

- **CI Status Badges**: Added to README.md
  - Tests, Security, CodeQL workflow status
  - License, Python version, Code style badges
  - Direct links to GitHub Actions workflows

- **GitHub Templates**: Verified comprehensive templates
  - Bug report template with security considerations
  - Feature request template with impact assessment
  - Security vulnerability template for responsible disclosure
  - Pull request template with CHANGELOG.md requirement

### Security

- **Command Injection Prevention**: All subprocess calls use secure array format, no `shell=True` usage
- **Path Traversal Prevention**: Absolute path requirements, directory traversal blocking (`../`, `../../`)
- **Input Validation**: URL format validation, parameter bounds checking, character filtering
- **Timeout Protection**: Tool-specific timeouts (10m sqlmap, 5m nuclei, 2.5m tshark, 15m foremost, etc.)
- **API Key Validation**: Secure API key management for external services (Shodan)
- **Error Handling**: Graceful degradation, no sensitive information leaks in error messages
- **Subprocess Security**: All commands built as arrays `["tool", "arg1", "arg2"]`

### Changed

- Updated `README.md` with:
  - Vulnerability Server status and latest progress table
  - CHANGELOG.md reference in Contributing section
  - CI status badges for workflows, license, Python version
- Updated `CONTRIBUTING.md` with:
  - Specialized agent references
  - Dependency management documentation reference
- Updated `pyproject.toml` with version ranges and upper bounds for all dependencies
- Updated `requirements.txt` with exact version pins for reproducible builds
- Updated `.pre-commit-config.yaml` with latest tool versions and enhanced security hooks
- Updated `.editorconfig` with comprehensive file type support
- Updated `src/api/main.py` with enhanced health check and version endpoints
- Updated `.github/pull_request_template.md` with CHANGELOG.md requirement emphasis
- Updated `plan/ROADMAP.md` to reflect Phase 1 completion (2025-01-13)
- Improved contributor onboarding with expanded support docs and templates

## [0.1.0] - 2025-01-01

### Added

- Initial release of Kali Agents MCP CLI with supervisor orchestration
- Supervisor agent with ML-based orchestration using LangGraph
- Multi-agent coordination with LangChain and Pydantic AI
- MCP servers for network, web, and data operations
- Core documentation: README, SECURITY policy, CONTRIBUTING guide
- FastAPI web framework for REST API endpoints
- CLI interface with Rich output formatting
- ML algorithms: Fuzzy Logic, Genetic Algorithm, Q-Learning
- Comprehensive pytest test suite with 80%+ coverage target
- Multi-platform CI/CD with GitHub Actions
- Security scanning (Bandit, Safety, Semgrep, CodeQL)
- Docker support with multi-stage builds

### Security

- Environment variable validation for secrets management
- Secure subprocess usage patterns established
- API key authentication for REST endpoints
- Multiple security scanners in CI/CD pipeline

[Unreleased]: https://github.com/Huleinpylo/kali-agents-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Huleinpylo/kali-agents-mcp/releases/tag/v0.1.0
