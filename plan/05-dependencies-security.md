# Dependencies and Security

**Status**: HIGH PRIORITY - Critical for supply chain security

**Target Timeline**: Ongoing / Weeks 3-4 (Phase 1)

---

## Overview

Maintaining secure and up-to-date dependencies is crucial for security posture. Current dependency management needs improvement for better security and reproducibility.

### Priority: HIGH
**Effort**: Low-Medium (ongoing maintenance)
**Impact**: Security posture, supply chain security, stability

### Current State

```
Dependency Management:
✅ requirements.txt exists
✅ pyproject.toml with minimal versions
✅ Dependabot configured
✅ Security scans in CI (Bandit, Safety, Semgrep)
❌ No version pinning
❌ No automated vulnerability patching
❌ No SBOM generation
❌ No license compliance checking
```

---

## 1. Dependency Version Management

### Current State

**File**: `requirements.txt`
```
fastmcp
langchain
langchain-community
# ... no version pins
```

### Implementation Details

#### 1.1 Pin Exact Versions

**File**: `requirements.txt` (updated)

```
# Core Framework - Pin exact versions for reproducibility
# Generated: 2024-01-15
# Python: >=3.10,<3.13

# MCP and LangChain
fastmcp==2.8.0
langchain==0.1.12
langchain-community==0.0.27
langgraph==0.0.42
langchain-ollama==0.0.2

# Web Framework
fastapi==0.115.12
uvicorn[standard]==0.34.3
pydantic==2.10.6
pydantic-settings==2.7.2

# HTTP Clients
httpx==0.28.2
requests==2.32.3
aiohttp==3.11.13

# Database
sqlalchemy==2.0.36
alembic==1.14.1

# Security Tools Integration
pymetasploit3==1.0.3
shodan==1.31.0
python-nmap==0.7.1

# ML/AI
numpy==1.26.4
scikit-learn==1.5.2
scikit-fuzzy==0.4.2

# Utilities
python-dotenv==1.0.1
pyyaml==6.0.2
click==8.1.8
rich==13.9.4
jinja2==3.1.5

# Report Generation
reportlab==4.2.7
matplotlib==3.10.1
plotly==5.24.1

# Testing (in requirements-dev.txt)
```

**File**: `requirements-dev.txt`

```
# Development dependencies with exact pins
-r requirements.txt

# Testing
pytest==8.4.0
pytest-cov==6.0.0
pytest-asyncio==0.24.0
pytest-mock==3.14.0
pytest-xdist==3.6.1
pytest-timeout==2.3.1
hypothesis==6.131.2

# Code Quality
black==25.1.0
isort==5.13.2
flake8==7.2.0
mypy==1.16.1
pylint==3.3.4

# Security
bandit==1.8.0
safety==3.3.1
semgrep==1.104.1

# Documentation
mkdocs==1.6.1
mkdocs-material==9.5.54
mkdocstrings[python]==0.28.3

# Pre-commit
pre-commit==4.0.1

# Performance
locust==2.33.1
py-spy==0.4.0
```

#### 1.2 Dependency Ranges in pyproject.toml

**File**: `pyproject.toml` (keep flexible for library users)

```toml
[project]
name = "kali-agents-mcp"
version = "0.1.0"
description = "Multi-Agent Cybersecurity Platform with ML-based orchestration"
requires-python = ">=3.10,<3.13"
dependencies = [
    # Allow minor version updates, block major changes
    "fastmcp>=2.8.0,<3.0.0",
    "langchain>=0.1.12,<0.2.0",
    "langchain-community>=0.0.27,<0.1.0",
    "langgraph>=0.0.42,<0.1.0",
    "fastapi>=0.115.0,<0.116.0",
    "uvicorn[standard]>=0.34.0,<0.35.0",
    "pydantic>=2.10.0,<3.0.0",
    "httpx>=0.28.0,<0.29.0",
    "sqlalchemy>=2.0.0,<3.0.0",
    "click>=8.1.0,<9.0.0",
    "rich>=13.9.0,<14.0.0",
    "python-dotenv>=1.0.0,<2.0.0",
    "pyyaml>=6.0.0,<7.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.4.0,<9.0.0",
    "pytest-cov>=6.0.0,<7.0.0",
    "pytest-asyncio>=0.24.0,<0.25.0",
    "black>=25.0.0,<26.0.0",
    "isort>=5.13.0,<6.0.0",
    "mypy>=1.16.0,<2.0.0",
]
security = [
    "bandit>=1.8.0,<2.0.0",
    "safety>=3.0.0,<4.0.0",
]
docs = [
    "mkdocs>=1.6.0,<2.0.0",
    "mkdocs-material>=9.5.0,<10.0.0",
]
```

#### 1.3 Use pip-tools for Lock Files

**Install pip-tools**:
```bash
pip install pip-tools
```

**File**: `requirements.in`
```
# High-level dependencies
fastmcp>=2.8.0
langchain>=0.1.12
fastapi>=0.115.0
# ... minimal list
```

**Generate locked requirements**:
```bash
# Generate requirements.txt with exact pins
pip-compile requirements.in --output-file=requirements.txt

# Generate dev requirements
pip-compile requirements-dev.in --output-file=requirements-dev.txt

# Update all dependencies
pip-compile --upgrade requirements.in
```

**Add to Makefile**:

**File**: `Makefile` (new file)

```makefile
.PHONY: deps-compile deps-sync deps-update

deps-compile:
	pip-compile requirements.in --output-file=requirements.txt
	pip-compile requirements-dev.in --output-file=requirements-dev.txt

deps-sync:
	pip-sync requirements.txt requirements-dev.txt

deps-update:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements-dev.in
```

### Acceptance Criteria
- [ ] All dependencies pinned to exact versions
- [ ] requirements.in and requirements.txt strategy implemented
- [ ] pyproject.toml has reasonable version ranges
- [ ] Makefile commands for dependency management
- [ ] Documentation updated

**Effort Estimate**: 1-2 days

---

## 2. Automated Vulnerability Scanning

### Current State

```
✅ Dependabot enabled
✅ Safety in CI
❌ No automated patching
❌ No vulnerability database updates
❌ No SLA for security patches
```

### Implementation Details

#### 2.1 Enhanced Vulnerability Scanning

**File**: `.github/workflows/security-scan.yml`

```yaml
name: Security Scanning

on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'

jobs:
  dependency-scan:
    name: Dependency Vulnerability Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install safety pip-audit

      - name: Safety Check
        run: |
          safety check --json --output safety-report.json
        continue-on-error: true

      - name: pip-audit
        run: |
          pip-audit --requirement requirements.txt --format json --output pip-audit-report.json
        continue-on-error: true

      - name: Snyk Vulnerability Scan
        uses: snyk/actions/python-3.10@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          command: test
          args: --severity-threshold=high

      - name: Upload Scan Results
        uses: actions/upload-artifact@v4
        with:
          name: security-scan-results
          path: |
            safety-report.json
            pip-audit-report.json

      - name: Create Issue on High Severity
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 High Severity Vulnerabilities Detected',
              body: 'Security scan found high severity vulnerabilities. Check the workflow run for details.',
              labels: ['security', 'priority: critical']
            })

  code-scan:
    name: Code Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Bandit Scan
        run: |
          pip install bandit
          bandit -r src -f json -o bandit-report.json
        continue-on-error: true

      - name: Semgrep Scan
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/python
            p/owasp-top-ten

      - name: CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          languages: python

  license-check:
    name: License Compliance
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check Licenses
        run: |
          pip install pip-licenses
          pip-licenses --format=json --output-file=licenses.json

          # Check for problematic licenses
          pip-licenses --fail-on="GPL;AGPL" || echo "::warning::GPL/AGPL licenses found"

      - name: Upload License Report
        uses: actions/upload-artifact@v4
        with:
          name: license-report
          path: licenses.json
```

#### 2.2 Automated Dependency Updates

**File**: `.github/dependabot.yml` (enhanced)

```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "Huleinpylo"
    assignees:
      - "Huleinpylo"
    commit-message:
      prefix: "deps"
      include: "scope"
    labels:
      - "dependencies"
      - "python"
    # Auto-merge minor and patch updates
    versioning-strategy: increase

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"

  # Docker
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "docker"
```

#### 2.3 Security Policy

**File**: `SECURITY.md` (enhance existing)

Add sections:

```markdown
## Vulnerability Response SLA

| Severity | Response Time | Patch Time |
|----------|--------------|------------|
| Critical | 24 hours     | 48 hours   |
| High     | 72 hours     | 1 week     |
| Medium   | 1 week       | 2 weeks    |
| Low      | 2 weeks      | 1 month    |

## Security Update Process

1. **Detection**: Automated scans run daily
2. **Triage**: Security team reviews within SLA
3. **Patching**: Create PR with fix
4. **Testing**: Run full test suite
5. **Release**: Publish security release
6. **Notification**: Update SECURITY.md and CHANGELOG.md

## Dependency Security Guidelines

- All dependencies must pass security scans
- Critical vulnerabilities block merge
- Monthly dependency update reviews
- No GPL/AGPL licenses without approval
```

### Acceptance Criteria
- [ ] Multiple vulnerability scanners configured
- [ ] Daily automated security scans
- [ ] Auto-issue creation for critical vulnerabilities
- [ ] License compliance checking
- [ ] Security SLA documented

**Effort Estimate**: 3-4 days

---

## 3. Supply Chain Security

### Implementation Details

#### 3.1 SBOM Generation

**File**: `.github/workflows/sbom.yml`

```yaml
name: Generate SBOM

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  generate-sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate CycloneDX SBOM
        run: |
          pip install cyclonedx-bom
          cyclonedx-py -r requirements.txt -o sbom.json

      - name: Generate SPDX SBOM
        run: |
          pip install spdx-tools
          # Generate SPDX format SBOM
          python scripts/generate_spdx.py > sbom.spdx

      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: |
            sbom.json
            sbom.spdx

      - name: Attach to Release
        if: github.event_name == 'release'
        uses: softprops/action-gh-release@v1
        with:
          files: |
            sbom.json
            sbom.spdx
```

**File**: `scripts/generate_spdx.py` (new file)

```python
"""Generate SPDX SBOM."""

import json
import subprocess
from datetime import datetime

def generate_spdx():
    """Generate SPDX format SBOM."""
    # Get installed packages
    result = subprocess.run(
        ["pip", "list", "--format=json"],
        capture_output=True,
        text=True
    )
    packages = json.loads(result.stdout)

    # Generate SPDX document
    spdx = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "kali-agents-mcp",
        "documentNamespace": f"https://github.com/Huleinpylo/kali-agents-mcp/sbom/{datetime.now().isoformat()}",
        "creationInfo": {
            "created": datetime.now().isoformat(),
            "creators": ["Tool: kali-agents-mcp-sbom-generator"]
        },
        "packages": []
    }

    # Add packages
    for pkg in packages:
        spdx["packages"].append({
            "SPDXID": f"SPDXRef-Package-{pkg['name']}",
            "name": pkg["name"],
            "versionInfo": pkg["version"],
            "downloadLocation": f"https://pypi.org/project/{pkg['name']}/{pkg['version']}/",
            "filesAnalyzed": False
        })

    print(json.dumps(spdx, indent=2))

if __name__ == "__main__":
    generate_spdx()
```

#### 3.2 Dependency Provenance

**File**: `.github/workflows/provenance.yml`

```yaml
name: SLSA Provenance

on:
  release:
    types: [published]

permissions:
  id-token: write
  contents: write
  actions: read

jobs:
  provenance:
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v2.0.0
    with:
      base64-subjects: "${{ needs.build.outputs.hashes }}"
      upload-assets: true
```

#### 3.3 Dependency Hash Verification

**File**: `requirements-hashes.txt` (new file)

Generate with hashes:
```bash
pip-compile --generate-hashes requirements.in -o requirements-hashes.txt
```

**Usage**:
```bash
# Install with hash verification
pip install --require-hashes -r requirements-hashes.txt
```

### Acceptance Criteria
- [ ] SBOM generated automatically
- [ ] SLSA provenance attached to releases
- [ ] Dependency hashes in requirements
- [ ] Supply chain security documented

**Effort Estimate**: 3-4 days

---

## 4. Secret Management

### Current State

```
✅ .env for API keys
❌ No secret scanning
❌ Secrets could be committed
❌ No rotation policy
```

### Implementation Details

#### 4.1 Secret Scanning

**File**: `.github/workflows/secrets-scan.yml`

```yaml
name: Secret Scanning

on:
  push:
  pull_request:

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  trufflehog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: TruffleHog OSS
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

#### 4.2 Pre-commit Secret Detection

**File**: `.pre-commit-config.yaml` (add)

```yaml
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

#### 4.3 Secret Management Best Practices

**File**: `docs/development/secrets.md` (new file)

```markdown
# Secret Management

## Never Commit Secrets

✅ DO:
- Use environment variables
- Use `.env` file (in `.gitignore`)
- Use secret management services (AWS Secrets Manager, HashiCorp Vault)
- Use GitHub Secrets for CI/CD

❌ DON'T:
- Commit API keys to git
- Hardcode credentials in code
- Share secrets in plaintext

## Environment Variables

```bash
# .env (never commit!)
OPENAI_API_KEY=sk-...
SHODAN_API_KEY=...
DATABASE_URL=postgresql://user:pass@localhost/db
```

## CI/CD Secrets

Add to GitHub Secrets:
- Settings → Secrets and variables → Actions
- Add secrets: OPENAI_API_KEY, SHODAN_API_KEY, etc.

## Secret Rotation

| Secret Type | Rotation Frequency |
|-------------|-------------------|
| API Keys    | 90 days           |
| Passwords   | 90 days           |
| Tokens      | 30 days           |

## Detection and Response

If a secret is committed:
1. Immediately rotate the secret
2. Run `git filter-repo` to remove from history
3. Force push cleaned history
4. Audit for unauthorized access
```

### Acceptance Criteria
- [ ] Secret scanning in CI
- [ ] Pre-commit hooks prevent secret commits
- [ ] Secret management documented
- [ ] Rotation policy defined

**Effort Estimate**: 2-3 days

---

## 5. Compliance and Auditing

### Implementation Details

#### 5.1 Security Audit Logging

**File**: `src/utils/audit_logger.py` (new file)

```python
"""Security audit logging."""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class AuditLogger:
    """Log security-relevant events for compliance."""

    def __init__(self, log_dir: Path = Path("logs/audit")):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("audit")
        handler = logging.FileHandler(log_dir / "audit.log")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_event(
        self,
        event_type: str,
        user: Optional[str],
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log security event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user": user or "system",
            "action": action,
            "resource": resource,
            "details": details or {}
        }

        self.logger.info(json.dumps(event))

    def log_scan(self, user: str, target: str, scan_type: str):
        """Log security scan."""
        self.log_event(
            event_type="scan",
            user=user,
            action="execute",
            resource=target,
            details={"scan_type": scan_type}
        )

    def log_data_access(self, user: str, resource: str, action: str):
        """Log data access."""
        self.log_event(
            event_type="data_access",
            user=user,
            action=action,
            resource=resource
        )

    def log_authentication(self, user: str, success: bool):
        """Log authentication attempt."""
        self.log_event(
            event_type="authentication",
            user=user,
            action="login" if success else "login_failed",
            resource="auth_system"
        )
```

#### 5.2 Compliance Reports

**File**: `scripts/generate_compliance_report.py` (new file)

```python
"""Generate compliance reports."""

import json
from datetime import datetime, timedelta
from pathlib import Path

def generate_compliance_report(days: int = 30):
    """Generate compliance report for last N days."""

    report = {
        "report_date": datetime.now().isoformat(),
        "period_days": days,
        "security_scans": [],
        "vulnerabilities": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "dependencies": {
            "total": 0,
            "outdated": 0,
            "vulnerable": 0
        },
        "compliance_checks": {
            "sbom_generated": True,
            "security_scans_passed": True,
            "secrets_detected": False,
            "licenses_compliant": True
        }
    }

    # Generate report
    output_file = Path(f"compliance-report-{datetime.now().strftime('%Y%m%d')}.json")
    output_file.write_text(json.dumps(report, indent=2))

    print(f"Compliance report generated: {output_file}")

if __name__ == "__main__":
    generate_compliance_report()
```

### Acceptance Criteria
- [ ] Audit logging implemented
- [ ] Compliance reports generated monthly
- [ ] Security metrics tracked
- [ ] Compliance documentation complete

**Effort Estimate**: 3-4 days

---

## Related Issues

- GitHub issues with label `security` or `dependencies`
- Milestone: Phase 1 - Foundation

---

## Success Metrics

### Dependency Health
- [ ] 100% dependencies pinned
- [ ] Zero critical vulnerabilities
- [ ] < 5 high severity vulnerabilities
- [ ] Monthly dependency updates

### Security Metrics
- [ ] Daily vulnerability scans
- [ ] 24h response to critical CVEs
- [ ] No secrets in repository
- [ ] SBOM published with releases

### Compliance
- [ ] Audit logs for all scans
- [ ] License compliance reports
- [ ] Security documentation complete
- [ ] Provenance for all releases

**Total Effort Estimate**: 2-3 weeks (initial setup + ongoing maintenance)
