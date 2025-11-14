# Dependency Management

**Version**: 1.0.0
**Last Updated**: 2025-01-13
**Status**: Active

---

## Overview

Kali Agents MCP uses a dual-strategy approach to dependency management:

1. **Exact Pins** (`requirements.txt`, `requirements-dev.txt`) - For reproducible development and production builds
2. **Flexible Ranges** (`pyproject.toml`) - For library compatibility and downstream consumers

This approach ensures:
- Reproducible builds in CI/CD
- Predictable behavior across development environments
- Compatibility for projects that depend on Kali Agents
- Easy security updates and dependency tracking

---

## File Structure

### `requirements.txt`
**Purpose**: Production dependencies with exact version pins

```bash
# Install production dependencies
pip install -r requirements.txt
```

**Characteristics**:
- Exact versions (e.g., `fastmcp==2.8.0`)
- Used in CI/CD for reproducible builds
- Updated monthly or when security vulnerabilities are discovered
- Guarantees identical behavior across all environments

### `requirements-dev.txt`
**Purpose**: Development dependencies with exact version pins

```bash
# Install development dependencies (includes production deps)
pip install -r requirements-dev.txt
```

**Characteristics**:
- Includes production dependencies via `-r requirements.txt`
- Contains testing, linting, and documentation tools
- Exact versions for consistent development experience
- Used by contributors and in CI/CD

### `pyproject.toml`
**Purpose**: Package metadata and flexible dependency ranges

```bash
# Install package with flexible dependencies
pip install -e .

# Install with optional dependencies
pip install -e ".[dev]"
pip install -e ".[security]"
pip install -e ".[docs]"
```

**Characteristics**:
- Version ranges with upper bounds (e.g., `fastmcp>=2.8.0,<3.0.0`)
- Prevents major version breakage
- Allows minor and patch updates
- Suitable for library consumers

---

## Version Pinning Strategy

### Philosophy

- **requirements.txt**: Lock everything for reproducibility
- **pyproject.toml**: Allow flexibility within major versions
- **Security**: Update immediately for CVEs regardless of schedule

### Version Range Format

```python
# Semantic Versioning: MAJOR.MINOR.PATCH

# pyproject.toml - Allow minor and patch updates
"fastmcp>=2.8.0,<3.0.0"  # Allows 2.8.1, 2.9.0, but not 3.0.0

# requirements.txt - Exact version
"fastmcp==2.8.0"  # Only this exact version
```

### Upper Bound Rationale

Upper bounds prevent:
- Breaking changes from major version updates
- Unexpected behavior in production
- CI/CD failures from incompatible updates
- Supply chain attacks via malicious major versions

---

## Updating Dependencies

### Monthly Review Process

1. **Check for outdated dependencies**:
   ```bash
   pip install -r requirements.txt
   pip list --outdated
   ```

2. **Review changelog and release notes** for each update:
   - Breaking changes?
   - New features needed?
   - Security fixes?
   - Deprecation warnings?

3. **Update in isolation** (one dependency at a time for complex updates):
   ```bash
   # Update specific package
   pip install --upgrade fastmcp==2.9.0
   ```

4. **Run full test suite**:
   ```bash
   ./test.sh
   pytest tests/ -v --cov=src
   ```

5. **Update requirements files**:
   ```bash
   # Update requirements.txt with new version
   # Edit manually to update specific versions
   ```

6. **Update `CHANGELOG.md`**:
   ```markdown
   ### Changed
   - Updated fastmcp from 2.8.0 to 2.9.0
   - Updated requests from 2.31.0 to 2.31.1 (security fix)
   ```

7. **Create PR** with:
   - Test results
   - Changelog updates
   - Breaking change notes (if any)
   - Security advisory references (if applicable)

### Automated Monthly Check

A GitHub Actions workflow runs on the 1st of each month:

**File**: `.github/workflows/dependency-update.yml`

This workflow:
- Checks for outdated dependencies
- Creates a GitHub issue with the list
- Labels it as `dependencies` and `maintenance`

---

## Security Updates

### Immediate Response Protocol

1. **Monitor security advisories**:
   - GitHub Security Advisories
   - PyPI advisories
   - CVE databases
   - Tool-specific security mailing lists

2. **Assess impact**:
   ```bash
   # Check if vulnerable version is in use
   pip show <package-name>

   # Run security audit
   pip install safety
   safety check -r requirements.txt
   ```

3. **Update immediately**:
   ```bash
   # Update to patched version
   pip install --upgrade <package>==<safe-version>

   # Run tests
   ./test.sh
   ```

4. **Create hotfix release** if critical:
   ```bash
   # Update version in pyproject.toml
   # Create git tag
   git tag -a v0.1.1 -m "Security fix: CVE-XXXX-XXXXX"
   git push origin v0.1.1
   ```

### Security Scanning Tools

**Included in CI/CD**:
- `bandit` - Python security linter
- `safety` - Dependency vulnerability checker
- `semgrep` - Semantic code analysis
- **GitHub Dependabot** - Automated security updates

**Manual Scanning**:
```bash
# Check for vulnerabilities
pip install safety
safety check -r requirements.txt

# Security linting
pip install bandit
bandit -r src/

# Semantic analysis
pip install semgrep
semgrep --config=auto src/
```

---

## CI/CD Integration

### GitHub Actions Usage

**Test Workflow** (`.github/workflows/tests.yml`):
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt  # Exact pins
    pip install -r requirements-dev.txt
```

**Monthly Dependency Check** (`.github/workflows/dependency-update.yml`):
- Runs on schedule (1st of month)
- Creates issue with outdated dependencies
- Does not auto-update (requires human review)

---

## Troubleshooting

### Dependency Conflicts

**Symptom**: `pip` reports conflicting dependencies

**Solution**:
```bash
# Clear cache and reinstall
pip cache purge
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Version Mismatch

**Symptom**: Tests pass locally but fail in CI

**Solution**:
```bash
# Ensure using exact versions from requirements.txt
pip freeze > current-versions.txt
diff current-versions.txt requirements.txt

# Reinstall with exact versions
pip install --force-reinstall -r requirements.txt
```

### Outdated Pins

**Symptom**: Can't install package due to old dependencies

**Solution**:
```bash
# Check what's outdated
pip list --outdated

# Follow monthly review process
# Update requirements.txt and test
```

---

## Best Practices

### For Contributors

1. **Always install via `requirements-dev.txt`**:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Never manually edit version pins** without:
   - Running full test suite
   - Updating CHANGELOG.md
   - Getting PR review

3. **Report dependency issues** immediately:
   - Create GitHub issue
   - Tag as `dependencies`
   - Include error messages and environment details

### For Maintainers

1. **Review dependency updates monthly**
2. **Respond to security advisories within 24 hours**
3. **Document all dependency changes in CHANGELOG.md**
4. **Test with both pinned and latest versions**
5. **Keep pyproject.toml ranges current**

### For Package Users

1. **Use pyproject.toml dependencies** for integration:
   ```bash
   pip install kali-agents-mcp
   ```

2. **Use requirements.txt for exact reproduction**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Pin your own dependencies** based on your needs

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-01-13 | 1.0.0 | Initial dependency management strategy |

---

## References

- [Semantic Versioning](https://semver.org/)
- [pip requirements file format](https://pip.pypa.io/en/stable/reference/requirements-file-format/)
- [PEP 508 - Dependency specification](https://peps.python.org/pep-0508/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Maintained By**: Kali Agents Development Team
**Questions**: Open an issue on GitHub with the `dependencies` label
