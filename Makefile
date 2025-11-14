.PHONY: help install install-dev test test-unit test-integration test-security test-coverage \
        lint format clean run docs build docker-build docker-run security-scan \
        pre-commit setup-hooks check all

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
ISORT := $(PYTHON) -m isort
FLAKE8 := $(PYTHON) -m flake8
MYPY := $(PYTHON) -m mypy
BANDIT := $(PYTHON) -m bandit

# Default target
help: ## Show this help message
	@echo "Kali Agents MCP - Development Commands"
	@echo "======================================"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# Installation targets
install: ## Install production dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev: ## Install development dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt

setup-hooks: ## Setup pre-commit hooks
	$(PIP) install pre-commit
	pre-commit install
	@echo "Pre-commit hooks installed successfully!"

# Testing targets
test: ## Run all tests with coverage
	$(PYTEST) tests/ -v \
		--cov=src \
		--cov-report=term-missing \
		--cov-report=html:htmlcov \
		--cov-report=xml

test-unit: ## Run unit tests only
	$(PYTEST) tests/ -v -m unit

test-integration: ## Run integration tests only
	$(PYTEST) tests/ -v -m integration

test-security: ## Run security tests only
	$(PYTEST) tests/ -v -m security

test-coverage: ## Generate coverage report
	$(PYTEST) tests/ --cov=src --cov-report=html:htmlcov
	@echo "Coverage report generated in htmlcov/index.html"

test-fast: ## Run tests without coverage (faster)
	$(PYTEST) tests/ -v --no-cov

test-verbose: ## Run tests with maximum verbosity
	$(PYTEST) tests/ -vv --tb=long --no-cov

# Code quality targets
lint: ## Run all linters
	@echo "Running flake8..."
	$(FLAKE8) src tests
	@echo "Running mypy..."
	$(MYPY) src
	@echo "Linting complete!"

format: ## Format code with black and isort
	@echo "Formatting with black..."
	$(BLACK) src tests
	@echo "Sorting imports with isort..."
	$(ISORT) src tests
	@echo "Formatting complete!"

check-format: ## Check code formatting without making changes
	$(BLACK) --check src tests
	$(ISORT) --check-only src tests

security-scan: ## Run security scans
	@echo "Running bandit security scan..."
	$(BANDIT) -r src/ -ll
	@echo "Checking dependencies for vulnerabilities..."
	$(PIP) install safety
	safety check --json
	@echo "Security scan complete!"

# Clean targets
clean: ## Clean generated files and caches
	@echo "Cleaning Python caches..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.py~" -delete
	@echo "Cleaning test and coverage artifacts..."
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache
	@echo "Cleaning build artifacts..."
	rm -rf build dist *.egg-info
	@echo "Clean complete!"

clean-all: clean ## Clean everything including virtual environment
	rm -rf venv/
	@echo "All clean!"

# Run targets
run: ## Run the CLI
	$(PYTHON) -m src.cli.main --help

run-api: ## Run the FastAPI server
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-network-server: ## Run the Network MCP server
	$(PYTHON) -m src.mcp_servers.network_server

run-web-server: ## Run the Web MCP server
	$(PYTHON) -m src.mcp_servers.web_server

run-vulnerability-server: ## Run the Vulnerability MCP server
	$(PYTHON) -m src.mcp_servers.vulnerability_server

run-forensic-server: ## Run the Forensic MCP server
	$(PYTHON) -m src.mcp_servers.forensic_server

# Documentation targets
docs: ## Generate documentation
	@echo "Documentation generation not yet configured"
	@echo "TODO: Setup Sphinx or MkDocs"

docs-serve: ## Serve documentation locally
	@echo "Documentation serving not yet configured"

# Build targets
build: ## Build the package
	$(PYTHON) -m build

# Docker targets
docker-build: ## Build Docker image
	docker build --target api -t kali-agents-api .
	docker build --target cli -t kali-agents-cli .

docker-run: ## Run Docker container
	docker-compose up --build

docker-stop: ## Stop Docker containers
	docker-compose down

docker-clean: ## Clean Docker images and containers
	docker-compose down -v
	docker rmi kali-agents-api kali-agents-cli 2>/dev/null || true

# Development workflow targets
check: lint test ## Run all checks (lint + test)

all: clean install-dev format lint test ## Run full development workflow

pre-commit: format lint ## Run pre-commit checks

ci: ## Simulate CI pipeline locally
	@echo "Running CI pipeline..."
	@make clean
	@make install-dev
	@make lint
	@make test
	@make security-scan
	@echo "CI pipeline complete!"

# Quick development targets
dev-setup: ## Complete development environment setup
	@echo "Setting up development environment..."
	@make install-dev
	@make setup-hooks
	@echo "Creating .env file from example..."
	@test -f .env || cp .env.example .env 2>/dev/null || echo "No .env.example found"
	@echo "Development environment ready!"

watch-tests: ## Watch for changes and run tests automatically
	$(PYTEST) tests/ -v --cov=src -f

# Version and info targets
version: ## Show version information
	@echo "Kali Agents MCP"
	@echo "Version: 0.1.0"
	@$(PYTHON) --version
	@$(PIP) --version

list-deps: ## List installed dependencies
	$(PIP) list

check-deps: ## Check for outdated dependencies
	$(PIP) list --outdated

# Database targets
db-init: ## Initialize database
	$(PYTHON) -m src.database.init

db-migrate: ## Run database migrations
	@echo "Database migrations not yet configured"

# Git workflow helpers
git-status: ## Show git status
	@git status

commit: ## Interactive commit with conventional commits format
	@echo "Commit types: feat, fix, docs, test, refactor, perf, security"
	@read -p "Enter commit type: " type; \
	read -p "Enter commit message: " msg; \
	git commit -m "$$type: $$msg"

# Maintenance targets
update-deps: ## Update dependencies (use with caution)
	$(PIP) install --upgrade pip
	$(PIP) list --outdated

freeze-deps: ## Freeze current dependencies
	$(PIP) freeze > requirements-freeze.txt
	@echo "Dependencies frozen to requirements-freeze.txt"
