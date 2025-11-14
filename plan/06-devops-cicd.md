# DevOps and CI/CD

**Status**: MEDIUM PRIORITY - Improves development workflow

**Target Timeline**: Weeks 6-8 (Phase 2)

---

## Overview

Current CI/CD is functional but can be improved with better workflows, deployment automation, and monitoring.

### Priority: MEDIUM
**Effort**: Medium (2-3 weeks)
**Impact**: Developer productivity, deployment reliability, operational efficiency

### Current State

```
CI/CD Status:
✅ Multi-platform tests (Linux, Windows, macOS)
✅ Security scanning (Bandit, Safety, CodeQL)
✅ Code formatting (Black, isort)
✅ Dependabot configured
❌ No automated deployment
❌ No docker-compose for local development
❌ No monitoring/observability
❌ Limited caching in CI
❌ No release automation
```

---

## 1. Improve CI Performance

### Current State

CI jobs take ~10-15 minutes. Can be optimized with better caching and parallel execution.

### Implementation Details

#### 1.1 Optimize GitHub Actions

**File**: `.github/workflows/tests.yml` (optimize)

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
  workflow_dispatch:

# Cancel in-progress runs for same PR
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  changes:
    name: Detect Changes
    runs-on: ubuntu-latest
    outputs:
      python: ${{ steps.filter.outputs.python }}
      docs: ${{ steps.filter.outputs.docs }}
      docker: ${{ steps.filter.outputs.docker }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            python:
              - 'src/**'
              - 'tests/**'
              - 'requirements*.txt'
              - 'pyproject.toml'
            docs:
              - 'docs/**'
              - 'mkdocs.yml'
            docker:
              - 'Dockerfile'
              - 'docker-compose.yml'

  lint:
    name: Lint
    runs-on: ubuntu-latest
    needs: changes
    if: needs.changes.outputs.python == 'true'
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          cache-dependency-path: |
            requirements.txt
            requirements-dev.txt

      - name: Cache pre-commit
        uses: actions/cache@v4
        with:
          path: ~/.cache/pre-commit
          key: pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}

      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
          pre-commit install

      - name: Run pre-commit
        run: pre-commit run --all-files

  test:
    name: Test Python ${{ matrix.python-version }} on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    needs: changes
    if: needs.changes.outputs.python == 'true'
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12']
        exclude:
          # Reduce matrix on non-main branches
          - os: windows-latest
            python-version: '3.10'
          - os: macos-latest
            python-version: '3.10'

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests
        run: |
          pytest tests/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=term-missing \
            --junit-xml=junit.xml \
            -n auto

      - name: Upload coverage
        if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: unittests
          token: ${{ secrets.CODECOV_TOKEN }}

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.os }}-${{ matrix.python-version }}
          path: junit.xml

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: changes
    if: needs.changes.outputs.python == 'true'
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install bandit safety semgrep

      - name: Run Bandit
        run: bandit -r src -f json -o bandit-report.json
        continue-on-error: true

      - name: Run Safety
        run: safety check --json --output safety-report.json
        continue-on-error: true

      - name: Run Semgrep
        run: semgrep --config=auto src --json > semgrep-report.json
        continue-on-error: true

      - name: Upload security reports
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
            semgrep-report.json

  integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: [lint, test]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y nmap masscan

      - name: Install Python dependencies
        run: pip install -r requirements-dev.txt

      - name: Run integration tests
        run: pytest tests/integration -v --timeout=300
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test

  build-docker:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: changes
    if: needs.changes.outputs.docker == 'true' || needs.changes.outputs.python == 'true'
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and cache
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          cache-from: type=gha
          cache-to: type=gha,mode=max
          tags: kali-agents-mcp:test
```

#### 1.2 Use Build Matrix Strategically

Only run full matrix on main branch, subset on PRs to save time.

#### 1.3 Implement Artifact Caching

Cache dependencies, pre-commit hooks, and build artifacts between runs.

### Acceptance Criteria
- [ ] CI runtime < 5 minutes for PRs
- [ ] Aggressive caching configured
- [ ] Parallel test execution
- [ ] Path filtering for selective tests
- [ ] Build matrix optimized

**Effort Estimate**: 3-4 days

---

## 2. Deployment Automation

### Current State

```
❌ No automated deployment
❌ Manual release process
❌ No staging environment
```

### Implementation Details

#### 2.1 Automated Releases

**File**: `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'

permissions:
  contents: write
  id-token: write

jobs:
  build:
    name: Build Distribution
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install build tools
        run: pip install build twine

      - name: Build package
        run: python -m build

      - name: Check package
        run: twine check dist/*

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: distributions
          path: dist/

  publish-pypi:
    name: Publish to PyPI
    needs: build
    runs-on: ubuntu-latest
    environment: release
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: distributions
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

  publish-docker:
    name: Publish Docker Image
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}

      - name: Extract version
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            huleinpylo/kali-agents-mcp:latest
            huleinpylo/kali-agents-mcp:${{ steps.version.outputs.VERSION }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  create-release:
    name: Create GitHub Release
    needs: [publish-pypi, publish-docker]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate changelog
        id: changelog
        run: |
          # Extract changelog for this version
          sed -n '/## \[/,/## \[/p' CHANGELOG.md | sed '1d;$d' > release-notes.md

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: release-notes.md
          files: |
            dist/*
          generate_release_notes: true
```

#### 2.2 Staging Environment

**File**: `docker-compose.staging.yml`

```yaml
version: '3.8'

services:
  api:
    image: huleinpylo/kali-agents-mcp:staging
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/kali_agents
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    depends_on:
      - db
      - redis
    networks:
      - staging

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=kali_agents
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - staging

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - staging

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - api
    networks:
      - staging

volumes:
  postgres_data:
  redis_data:

networks:
  staging:
    driver: bridge
```

#### 2.3 Deployment Scripts

**File**: `scripts/deploy.sh`

```bash
#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

echo "Deploying version $VERSION to $ENVIRONMENT..."

# Pull latest images
docker-compose -f docker-compose.$ENVIRONMENT.yml pull

# Stop old containers
docker-compose -f docker-compose.$ENVIRONMENT.yml down

# Start new containers
docker-compose -f docker-compose.$ENVIRONMENT.yml up -d

# Run migrations
docker-compose -f docker-compose.$ENVIRONMENT.yml exec -T api alembic upgrade head

# Health check
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "Deployment successful!"
```

### Acceptance Criteria
- [ ] Automated PyPI publishing
- [ ] Automated Docker publishing
- [ ] GitHub releases created automatically
- [ ] Staging environment configured
- [ ] Deployment scripts tested

**Effort Estimate**: 1 week

---

## 3. Local Development Environment

### Implementation Details

#### 3.1 Docker Compose for Development

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - /app/.venv  # Prevent host venv from being mounted
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/kali_agents
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=kali_agents
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  pgadmin:
    image: dpage/pgadmin4:latest
    ports:
      - "5050:80"
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@example.com
      - PGADMIN_DEFAULT_PASSWORD=admin
    depends_on:
      - db

  redis-commander:
    image: rediscommander/redis-commander:latest
    ports:
      - "8081:8081"
    environment:
      - REDIS_HOSTS=local:redis:6379
    depends_on:
      - redis

volumes:
  postgres_data:
  redis_data:
```

**File**: `Dockerfile.dev`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nmap \
    masscan \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application
COPY . .

# Install in development mode
RUN pip install -e .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--reload"]
```

#### 3.2 Development Scripts

**File**: `Makefile`

```makefile
.PHONY: help dev-up dev-down dev-logs test lint format clean

help:
	@echo "Available commands:"
	@echo "  make dev-up       - Start development environment"
	@echo "  make dev-down     - Stop development environment"
	@echo "  make dev-logs     - Show logs"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean temporary files"

dev-up:
	docker-compose up -d
	@echo "Development environment started!"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
	@echo "PgAdmin: http://localhost:5050"
	@echo "Redis Commander: http://localhost:8081"

dev-down:
	docker-compose down

dev-logs:
	docker-compose logs -f api

dev-shell:
	docker-compose exec api bash

test:
	pytest tests/ -v --cov=src

test-watch:
	pytest-watch -- tests/ -v

lint:
	pre-commit run --all-files

format:
	black src tests
	isort src tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov dist build

db-migrate:
	docker-compose exec api alembic upgrade head

db-reset:
	docker-compose exec api alembic downgrade base
	docker-compose exec api alembic upgrade head

db-shell:
	docker-compose exec db psql -U postgres kali_agents
```

#### 3.3 VS Code Development Container

**File**: `.devcontainer/devcontainer.json`

```json
{
  "name": "Kali Agents MCP",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "api",
  "workspaceFolder": "/app",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "charliermarsh.ruff",
        "github.copilot",
        "eamodio.gitlens",
        "ms-azuretools.vscode-docker",
        "tamasfe.even-better-toml"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
        "python.formatting.provider": "black",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
          "source.organizeImports": true
        }
      }
    }
  },
  "postCreateCommand": "pip install -e .",
  "remoteUser": "root"
}
```

### Acceptance Criteria
- [ ] docker-compose for local development
- [ ] Development Dockerfile optimized
- [ ] Makefile with common commands
- [ ] VS Code devcontainer configured
- [ ] Database GUI tools included

**Effort Estimate**: 3-4 days

---

## 4. Monitoring and Observability

### Implementation Details

#### 4.1 Application Metrics

**File**: `src/utils/metrics.py`

```python
"""Application metrics using Prometheus."""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from functools import wraps
import time

# Metrics
scan_counter = Counter(
    'kali_agents_scans_total',
    'Total number of scans',
    ['scan_type', 'status']
)

scan_duration = Histogram(
    'kali_agents_scan_duration_seconds',
    'Scan duration in seconds',
    ['scan_type']
)

active_scans = Gauge(
    'kali_agents_active_scans',
    'Number of currently active scans'
)

agent_errors = Counter(
    'kali_agents_errors_total',
    'Total number of errors',
    ['agent', 'error_type']
)

def track_scan(scan_type: str):
    """Decorator to track scan metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            active_scans.inc()
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                scan_counter.labels(scan_type=scan_type, status='success').inc()
                return result
            except Exception as e:
                scan_counter.labels(scan_type=scan_type, status='error').inc()
                agent_errors.labels(agent=scan_type, error_type=type(e).__name__).inc()
                raise
            finally:
                duration = time.time() - start_time
                scan_duration.labels(scan_type=scan_type).observe(duration)
                active_scans.dec()

        return wrapper
    return decorator
```

**File**: `src/api/routers/metrics.py`

```python
"""Metrics endpoint."""

from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()

@router.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

#### 4.2 Structured Logging

**File**: `src/utils/logging_config.py`

```python
"""Structured logging configuration."""

import logging
import json
from datetime import datetime
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)

def setup_logging(log_level: str = "INFO", json_logs: bool = True):
    """Configure application logging."""
    formatter = JSONFormatter() if json_logs else logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level))
```

#### 4.3 Health Checks

**File**: `src/api/routers/health.py`

```python
"""Health check endpoints."""

from fastapi import APIRouter, status
from typing import Dict, Any
import asyncio

router = APIRouter()

@router.get("/health")
async def health() -> Dict[str, str]:
    """Basic health check."""
    return {"status": "healthy"}

@router.get("/health/ready")
async def readiness() -> Dict[str, Any]:
    """Readiness probe - check if app can serve requests."""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "mcp_servers": await check_mcp_servers(),
    }

    all_healthy = all(checks.values())

    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks
    }

@router.get("/health/live")
async def liveness() -> Dict[str, str]:
    """Liveness probe - check if app is alive."""
    return {"status": "alive"}

async def check_database() -> bool:
    """Check database connectivity."""
    try:
        # Check database connection
        return True
    except:
        return False

async def check_redis() -> bool:
    """Check Redis connectivity."""
    try:
        # Check Redis connection
        return True
    except:
        return False

async def check_mcp_servers() -> bool:
    """Check MCP server health."""
    try:
        # Check MCP servers
        return True
    except:
        return False
```

#### 4.4 Monitoring Stack

**File**: `docker-compose.monitoring.yml`

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki.yml:/etc/loki/local-config.yaml
      - loki_data:/loki

  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./promtail.yml:/etc/promtail/config.yml
      - /var/log:/var/log:ro
    command: -config.file=/etc/promtail/config.yml

volumes:
  prometheus_data:
  grafana_data:
  loki_data:
```

**File**: `prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kali-agents'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
```

### Acceptance Criteria
- [ ] Prometheus metrics exposed
- [ ] Structured JSON logging
- [ ] Health check endpoints
- [ ] Grafana dashboards
- [ ] Log aggregation with Loki

**Effort Estimate**: 1 week

---

## 5. Performance Optimization

### Implementation Details

#### 5.1 Response Caching

**File**: `src/utils/cache.py`

```python
"""Caching utilities using Redis."""

import json
from typing import Optional, Any, Callable
from functools import wraps
import hashlib
from redis import Redis

redis_client = Redis(host='localhost', port=6379, decode_responses=True)

def cache_response(ttl: int = 300):
    """Decorator to cache function responses."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{func.__name__}:{args}:{kwargs}"
            cache_key = f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"

            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )

            return result

        return wrapper
    return decorator
```

#### 5.2 Database Query Optimization

**File**: `src/db/optimizations.py`

```python
"""Database query optimizations."""

from sqlalchemy.orm import joinedload, selectinload

# Use eager loading for relationships
def get_scans_with_results(limit: int = 100):
    """Get scans with eager-loaded results."""
    return (
        session.query(Scan)
        .options(
            joinedload(Scan.results),
            selectinload(Scan.vulnerabilities)
        )
        .limit(limit)
        .all()
    )

# Index frequently queried columns
"""
CREATE INDEX idx_scans_target ON scans(target);
CREATE INDEX idx_scans_timestamp ON scans(timestamp);
CREATE INDEX idx_results_scan_id ON results(scan_id);
"""
```

### Acceptance Criteria
- [ ] Response caching implemented
- [ ] Database indexes optimized
- [ ] Query performance tested
- [ ] Redis caching configured

**Effort Estimate**: 3-4 days

---

## Related Issues

- GitHub issues with label `devops` or `ci-cd`
- Milestone: Phase 2 - DevOps

---

## Success Metrics

### CI/CD Metrics
- [ ] CI runtime < 5 minutes for PRs
- [ ] < 1 minute for lint-only changes
- [ ] 100% automated releases
- [ ] Zero manual deployment steps

### Reliability Metrics
- [ ] 99.9% deployment success rate
- [ ] < 5 minute rollback time
- [ ] Health checks passing
- [ ] Zero downtime deployments

### Developer Experience
- [ ] < 2 minutes to start dev environment
- [ ] One-command deployments
- [ ] Comprehensive Makefile
- [ ] VS Code devcontainer working

**Total Effort Estimate**: 2-3 weeks
