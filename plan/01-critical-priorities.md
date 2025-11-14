# Critical Priorities

**Status**: MUST COMPLETE - Foundation for all other work

**Target Timeline**: Weeks 1-4 (Phase 1)

---

## 1. Complete MCP Server Implementations

### Overview
Currently only Network and Web MCP servers are fully implemented. Data server exists but Vulnerability, Forensic, Social, and Report servers are missing or incomplete.

### Priority: CRITICAL
**Effort**: High (2-3 weeks per agent)
**Impact**: Blocks core functionality

### Current State
```
✅ Network Server (src/mcp_servers/network_server.py)
✅ Web Server (src/mcp_servers/web_server.py)
✅ Data Server (src/mcp_servers/data_server.py)
✅ Vulnerability Server (src/mcp_servers/vulnerability_server.py) – 548 LOC, 4 hardened parsers, 62 pytest cases (96% coverage), docs in docs/vulnerability-server-api.md
❌ Forensic Server - NOT IMPLEMENTED
❌ Social Server - NOT IMPLEMENTED
❌ Report Server - NOT IMPLEMENTED
```

### Implementation Details

#### 1.1 Vulnerability Agent MCP Server *(Status: ✅ Complete as of 2025-01-15)*

**File**: `src/mcp_servers/vulnerability_server.py`

**Highlights**
- Tooling: `sqlmap_scan`, `nuclei_scan`, `searchsploit_query`, `metasploit_search` (async, no `shell=True`, enforced timeouts: 10m/5m/30s/60s) + lightweight `health_check`.
- Security: URL/argument validation, parameter bounds, allow-listed characters, graceful error handling, no sensitive leakbacks.
- Parsers: `_parse_sqlmap_output`, `_parse_nuclei_output`, `_parse_searchsploit_text`, `_parse_metasploit_search` cover structured + table outputs.
- Quality: `tests/test_vulnerability_server.py` (62 tests, 96% coverage) spanning happy paths, security, parser fidelity, and error handling with `@pytest.mark.security` + `@pytest.mark.asyncio`.
- Documentation: `docs/vulnerability-server-api.md` (API reference, examples, legal notes) + README/AGENTS cross-links; configs updated in `src/config/settings.py` (`KALI_TOOLS` includes nuclei/msfconsole).

**Tools to Integrate**:
- `sqlmap` - SQL injection testing
- `metasploit` - Exploitation framework (via RPC)
- `nuclei` - Vulnerability scanner
- `searchsploit` - Exploit database search

**Key Functions**:
```python
async def sqlmap_scan(target: str, options: Dict[str, Any]) -> Dict[str, Any]
async def nuclei_scan(target: str, templates: List[str]) -> Dict[str, Any]
async def searchsploit_query(query: str) -> Dict[str, Any]
async def metasploit_search(keyword: str) -> Dict[str, Any]
async def metasploit_exploit(exploit_path: str, options: Dict) -> Dict[str, Any]
```

**Output Parsers**:
- SQLMap JSON output parser
- Nuclei JSON output parser
- Searchsploit text parser
- Metasploit RPC response handler

**Dependencies**:
- Add `pymetasploit3` to requirements.txt
- Add `pynuclei` wrapper or use subprocess
- Document required Kali tools in README

**Acceptance Criteria**:
- [x] All tool functions implemented with proper error handling
- [x] Output parsers extract key vulnerability data
- [x] Integration tests (pytest) with mock tool outputs + coverage ≥90% (96% achieved)
- [x] Documentation with usage examples (`docs/vulnerability-server-api.md`)
- [x] FastMCP server configuration + CLI wiring scaffolded
- [x] Health checks for tool availability

---

#### 1.2 Forensic Agent MCP Server

**File**: `src/mcp_servers/forensic_server.py`

**Tools to Integrate**:
- `volatility` - Memory forensics
- `autopsy` - Digital forensics (if CLI available)
- `binwalk` - Firmware analysis
- `wireshark` / `tshark` - Network analysis
- `foremost` - File carving
- `strings` - String extraction

**Key Functions**:
```python
async def volatility_analyze(memory_dump: str, profile: str, plugins: List[str]) -> Dict[str, Any]
async def binwalk_analyze(firmware_file: str) -> Dict[str, Any]
async def tshark_analyze(pcap_file: str, filters: str) -> Dict[str, Any]
async def foremost_carve(image_file: str, output_dir: str) -> Dict[str, Any]
async def strings_extract(file_path: str, min_length: int = 4) -> List[str]
```

**Output Parsers**:
- Volatility plugin output parser
- Binwalk signature extraction
- TShark JSON output parser
- Foremost recovery report parser

**Dependencies**:
- Add `volatility3` to requirements.txt
- Document pcap file handling requirements
- Add file upload/storage mechanism

**Acceptance Criteria**:
- [ ] Memory forensics working with Volatility 3
- [ ] Network traffic analysis with tshark
- [ ] Firmware analysis with binwalk
- [ ] File carving functionality
- [ ] Integration tests with sample forensic files
- [ ] Security: validate file paths and prevent directory traversal

---

#### 1.3 Social Agent MCP Server

**File**: `src/mcp_servers/social_server.py`

**Tools to Integrate**:
- `theHarvester` - OSINT gathering
- `shodan` - Internet device search (API)
- `maltego` - Link analysis (if CLI available)
- `recon-ng` - Web reconnaissance
- `spiderfoot` - OSINT automation

**Key Functions**:
```python
async def theharvester_search(domain: str, sources: List[str]) -> Dict[str, Any]
async def shodan_search(query: str) -> Dict[str, Any]
async def shodan_host(ip: str) -> Dict[str, Any]
async def reconng_search(domain: str, modules: List[str]) -> Dict[str, Any]
async def spiderfoot_scan(target: str, modules: List[str]) -> Dict[str, Any]
```

**Output Parsers**:
- theHarvester JSON/XML parser
- Shodan API response handler
- Recon-ng database query results
- SpiderFoot JSON output

**Dependencies**:
- Add `shodan` to requirements.txt
- Store API keys in environment (already configured)
- Add rate limiting for API calls

**Acceptance Criteria**:
- [ ] OSINT gathering with multiple sources
- [ ] Shodan integration with API key management
- [ ] Results aggregation and deduplication
- [ ] Rate limiting to prevent API exhaustion
- [ ] Integration tests with mock API responses
- [ ] Privacy considerations documented

---

#### 1.4 Report Agent MCP Server

**File**: `src/mcp_servers/report_server.py`

**Purpose**: Professional penetration testing report generation

**Key Functions**:
```python
async def create_report(scan_results: Dict, template: str = "default") -> str
async def add_executive_summary(report_id: str, findings: List[Dict]) -> Dict
async def add_technical_details(report_id: str, section: str, data: Dict) -> Dict
async def add_vulnerability(report_id: str, vuln: Dict) -> Dict
async def generate_pdf(report_id: str, output_path: str) -> str
async def generate_html(report_id: str) -> str
async def list_templates() -> List[str]
```

**Report Components**:
- Executive Summary (LLM-generated)
- Scope and Methodology
- Findings Summary with severity ratings
- Detailed Technical Findings
- Evidence (screenshots, logs)
- Recommendations
- Appendices (raw tool outputs)

**Templates**:
- Default Professional Template
- Executive Template (brief)
- Technical Deep-Dive Template
- Compliance Template (PCI DSS, HIPAA, etc.)

**Technologies**:
- `reportlab` for PDF generation (already in requirements)
- `jinja2` for HTML templates (already in requirements)
- LangChain for LLM-powered executive summaries
- Chart generation with `matplotlib` or `plotly`

**Acceptance Criteria**:
- [ ] PDF report generation with professional styling
- [ ] HTML report with interactive elements
- [ ] Multiple template support
- [ ] LLM-generated executive summaries
- [ ] Vulnerability severity charts
- [ ] Evidence attachment support
- [ ] Report metadata (date, tester, scope)
- [ ] Export formats: PDF, HTML, Markdown, JSON

---

### Testing Requirements

For each MCP server:

1. **Unit Tests**:
   - Test each function with mock tool outputs
   - Test error handling (tool not found, invalid input)
   - Test output parsers with sample data

2. **Integration Tests**:
   - Test with actual Kali tools in Docker container
   - Test MCP server startup and health checks
   - Test tool availability detection

3. **Security Tests**:
   - Command injection prevention
   - Path traversal prevention
   - Input validation
   - Output sanitization

4. **Performance Tests**:
   - Response time benchmarks
   - Concurrent request handling
   - Resource usage under load

### Documentation Requirements

For each MCP server:

1. **API Documentation**:
   - Function signatures with type hints
   - Parameter descriptions
   - Return value schemas
   - Error codes and handling

2. **Usage Examples**:
   - Basic usage with curl/httpx
   - Python client examples
   - Integration with supervisor agent
   - Common workflows

3. **Setup Guide**:
   - Required Kali tools installation
   - Environment variables
   - API key configuration
   - Testing instructions

---

## 2. Add CHANGELOG.md

### Overview
No changelog exists, making it difficult to track changes between versions.

### Priority: HIGH
**Effort**: Low (1-2 hours)
**Impact**: Improves project transparency and release management

### Implementation

**File**: `CHANGELOG.md` (root directory)

**Format**: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

**Initial Structure**:
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive improvement plan in /plan directory
- GitHub issues for all improvement items

## [0.1.0] - 2024-XX-XX

### Added
- Initial project structure with MCP architecture
- Supervisor agent with ML-based orchestration
- Network MCP server (nmap, masscan integration)
- Web MCP server (gobuster, nikto, sqlmap integration)
- Data MCP server for scan result storage
- ML algorithms: Fuzzy Logic, Genetic Algorithm, Q-Learning
- Comprehensive test suite with 80% coverage target
- Multi-platform CI/CD with GitHub Actions
- Security scanning (Bandit, Safety, Semgrep, CodeQL)
- CLI interface with Rich output
- Documentation (README, SECURITY, CONTRIBUTING)

### Security
- Environment variable validation for secrets
- Multiple security scanning tools in CI
- OSSF Scorecard integration
- Supply chain security with SLSA

[Unreleased]: https://github.com/Huleinpylo/kali-agents-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Huleinpylo/kali-agents-mcp/releases/tag/v0.1.0
```

### Automation

**Update CI/CD** to generate changelog entries:

1. Add changelog update reminder to PR template
2. Create GitHub Action to enforce changelog updates
3. Automate changelog generation from commit messages (optional)

**File**: `.github/workflows/changelog.yml`
```yaml
name: Changelog Check
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check Changelog Updated
        run: |
          if git diff origin/main HEAD -- CHANGELOG.md | grep -q "^+.*"; then
            echo "✅ Changelog updated"
          else
            echo "⚠️  Consider updating CHANGELOG.md"
            # Don't fail, just warn
          fi
```

### Acceptance Criteria
- [ ] CHANGELOG.md created with proper format
- [ ] v0.1.0 changes documented
- [ ] Unreleased section added
- [ ] Links to compare views and releases
- [ ] Mentioned in README.md
- [ ] Added to PR template reminder
- [ ] Changelog check in CI (warning only)

---

## 3. Dependency Version Pinning

### Overview
requirements.txt has no version pins; pyproject.toml only has minimum versions. This leads to unpredictable builds and potential breakage.

### Priority: HIGH
**Effort**: Low (2-3 hours)
**Impact**: Reproducible builds, easier debugging, supply chain security

### Current State

**requirements.txt** (no pins):
```
fastmcp
langchain
langchain-community
...
```

**pyproject.toml** (minimum versions only):
```toml
dependencies = [
    "fastmcp>=2.8.0",
    "langchain>=0.1.12",
    ...
]
```

### Implementation Strategy

#### Option 1: requirements.txt with Exact Pins (Recommended)

**File**: `requirements.txt`
```
# Pin exact versions for reproducible builds
# Generated: 2024-XX-XX
# Python: 3.10+

# Core MCP and LangChain
fastmcp==2.8.0
langchain==0.1.12
langchain-community==0.0.27
langgraph==0.0.42
langchain-ollama==0.0.2

# Web Framework
fastapi==0.115.12
uvicorn==0.34.3

# ... (continue with all dependencies)
```

**File**: `requirements-dev.txt`
```
# Development dependencies with exact pins
-r requirements.txt

pytest==8.4.0
pytest-cov==4.0.0
pytest-asyncio==1.0.0
black==25.1.0
isort==5.12.0
flake8==7.2.0
mypy==1.16.1
bandit==1.7.5

# ... (continue with all dev dependencies)
```

**Keep pyproject.toml flexible** for library users:
```toml
dependencies = [
    "fastmcp>=2.8.0,<3.0.0",
    "langchain>=0.1.12,<0.2.0",
    ...
]
```

#### Option 2: Use pip-tools (Alternative)

**Install pip-tools**:
```bash
pip install pip-tools
```

**File**: `requirements.in` (high-level dependencies)
```
fastmcp>=2.8.0
langchain>=0.1.12
langchain-community
# ... minimal list
```

**Generate locked requirements**:
```bash
pip-compile requirements.in --output-file requirements.txt
pip-compile requirements-dev.in --output-file requirements-dev.txt
```

**Benefits**:
- Automatic transitive dependency resolution
- Easy updates with `pip-compile --upgrade`
- Clear separation of direct vs. transitive deps

#### Implementation Steps

1. **Audit Current Dependencies**:
   ```bash
   pip freeze > current-deps.txt
   pip list --outdated
   ```

2. **Test Current Versions**:
   ```bash
   ./test.sh
   python -m src.cli.main --help
   ```

3. **Create Pinned Requirements**:
   ```bash
   # Option 1: Direct freeze
   pip freeze > requirements-lock.txt

   # Option 2: Use pip-tools
   pip-compile requirements.in
   ```

4. **Update pyproject.toml**:
   - Add version upper bounds for major version changes
   - Keep reasonable minimum versions
   - Document versioning policy in CONTRIBUTING.md

5. **Update CI/CD**:
   - Use `requirements.txt` for reproducible CI builds
   - Add monthly dependency update job
   - Test with both pinned and latest versions

6. **Document Strategy**:
   Create `docs/dependency-management.md`

### Versioning Policy

**Document in CONTRIBUTING.md**:

```markdown
## Dependency Management

### Version Pinning Strategy

- **requirements.txt**: Exact pins for reproducible development
- **pyproject.toml**: Flexible ranges for library compatibility
- **CI**: Uses pinned versions for consistency

### Updating Dependencies

1. Monthly review: `pip list --outdated`
2. Test updates in isolation
3. Update requirements.txt
4. Run full test suite
5. Update CHANGELOG.md
6. Create PR with test results

### Security Updates

- Immediate response to security advisories
- Use `pip-audit` or `safety` to check vulnerabilities
- Update ASAP and create hotfix release if needed
```

### Security Benefits

- **Supply Chain Security**: Know exact versions used
- **Vulnerability Tracking**: Easier to track CVEs
- **Reproducible Security Audits**: Audit specific versions
- **Rollback Safety**: Can revert to known-good versions

### CI/CD Updates

**Update `.github/workflows/tests.yml`**:
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt  # Use pinned versions
    pip install -r requirements-dev.txt
```

**Add monthly dependency update workflow**:

**File**: `.github/workflows/dependency-update.yml`
```yaml
name: Dependency Update Check

on:
  schedule:
    - cron: '0 0 1 * *'  # First day of month
  workflow_dispatch:

jobs:
  check-updates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Check for outdated dependencies
        run: |
          pip install -r requirements.txt
          pip list --outdated > outdated-deps.txt
          cat outdated-deps.txt

      - name: Create Issue if Updates Available
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const outdated = fs.readFileSync('outdated-deps.txt', 'utf8');
            if (outdated.includes('Package')) {
              github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: 'Monthly Dependency Update Review',
                body: `## Outdated Dependencies\n\n\`\`\`\n${outdated}\n\`\`\`\n\nPlease review and update as appropriate.`,
                labels: ['dependencies', 'maintenance']
              });
            }
```

### Acceptance Criteria
- [ ] requirements.txt with exact version pins created
- [ ] requirements-dev.txt with exact version pins created
- [ ] pyproject.toml updated with reasonable version ranges
- [ ] All tests pass with pinned versions
- [ ] Dependency management policy documented
- [ ] CI uses pinned versions
- [ ] Monthly update workflow added
- [ ] CHANGELOG.md updated

---

## Success Metrics

### Completion Criteria

All three critical items must be completed before moving to Phase 2:

1. ✅ All 4 MCP servers implemented and tested
2. ✅ CHANGELOG.md created and integrated into workflow
3. ✅ Dependencies pinned and strategy documented

### Quality Gates

- [ ] All new code has 90%+ test coverage
- [ ] All security scans pass
- [ ] Documentation complete for all new features
- [ ] CI/CD pipeline green
- [ ] Code review completed

### Timeline

- **Week 1**: Vulnerability and Forensic servers
- **Week 2**: Social and Report servers
- **Week 3**: CHANGELOG.md and dependency pinning
- **Week 4**: Integration testing and documentation

---

## Related Issues

- See GitHub Issues with label `priority: critical`
- Milestone: Phase 1 - Foundation

---

## Next Steps

After completing critical priorities, proceed to:
- **[Phase 2: Core Features](./ROADMAP.md#phase-2)**
- Focus on specialized agents and report generation
- Increase test coverage to 90%
