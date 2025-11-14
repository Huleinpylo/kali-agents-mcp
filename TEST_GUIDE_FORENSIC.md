# Forensic Server Test Suite Guide

## Overview

This comprehensive test suite provides **90%+ code coverage** for the Forensic Server MCP module at `src/mcp_servers/forensic_server.py`. The test file contains **56 test functions** organized into 11 distinct test categories with emphasis on security and correctness.

## File Location
- **Test File:** `/home/kali/kali-agents-mcp/tests/test_forensic_server.py`
- **Module Under Test:** `/home/kali/kali-agents-mcp/src/mcp_servers/forensic_server.py`

## Quick Start

### Running All Tests
```bash
pytest tests/test_forensic_server.py -v
```

### Running Tests by Category
```bash
# Security tests only
pytest tests/test_forensic_server.py -v -m security

# Happy path tests
pytest tests/test_forensic_server.py -v -k "TestHappyPathTests"

# Error handling tests
pytest tests/test_forensic_server.py -v -k "TestErrorHandling"

# Parser tests
pytest tests/test_forensic_server.py -v -k "TestParsers"
```

### Generating Coverage Reports
```bash
# Terminal report with missing lines
pytest tests/test_forensic_server.py --cov=src.mcp_servers.forensic_server --cov-report=term-missing

# HTML report (generates htmlcov/index.html)
pytest tests/test_forensic_server.py --cov=src.mcp_servers.forensic_server --cov-report=html

# XML report for CI/CD integration
pytest tests/test_forensic_server.py --cov=src.mcp_servers.forensic_server --cov-report=xml
```

## Test Categories (56 Tests Total)

### 1. Happy Path Tests (6 tests)
Tests normal, expected behavior of all forensic tools:
- `TestHappyPathTests::test_volatility_analyze_memory_dump` - Memory dump analysis
- `TestHappyPathTests::test_binwalk_finds_signatures` - Firmware signature detection
- `TestHappyPathTests::test_tshark_analyzes_pcap` - PCAP network analysis
- `TestHappyPathTests::test_foremost_carves_files` - File recovery from images
- `TestHappyPathTests::test_strings_extracts_printable` - String extraction
- `TestHappyPathTests::test_health_check_all_tools_available` - Tool availability check

**Purpose:** Verify that each forensic tool produces expected output when given valid inputs.

**Run:** `pytest tests/test_forensic_server.py::TestHappyPathTests -v`

### 2. Security Tests (16 tests) - CRITICAL
#### 2a. Path Traversal Prevention (8 tests)
Prevents directory traversal attacks via path manipulation:
- Tests rejection of relative paths (./file, ../file)
- Tests rejection of traversal patterns (../../etc/passwd)
- Tests enforcement of absolute path requirement
- Tests across all tools (volatility, binwalk, tshark, foremost, strings)

**Run:** `pytest tests/test_forensic_server.py -v -m security -k "traversal or path"`

#### 2b. File Validation (6 tests)
Ensures files exist and are valid:
- `test_volatility_rejects_non_existent_files` - File existence check
- `test_volatility_rejects_directories` - Directory vs file validation
- Tests across all tools

**Run:** `pytest tests/test_forensic_server.py::TestFileValidation -v`

#### 2c. Parameter Validation (5 tests)
Validates input parameters:
- Min length bounds (1-100) for strings
- Encoding whitelist (ascii, unicode, utf-8, s, S)
- No shell=True in subprocess calls

**Run:** `pytest tests/test_forensic_server.py -v -m security -k "validate or encoding"`

### 3. Error Handling Tests (6 tests)
Tests graceful handling of various failure scenarios:
- `test_volatility_handles_timeout` - Timeout handling
- `test_volatility_handles_tool_not_found` - Missing tool handling
- `test_binwalk_handles_subprocess_error` - Subprocess errors
- `test_tshark_handles_malformed_json` - Malformed output parsing
- `test_foremost_handles_timeout` - Foremost-specific timeouts
- `test_strings_handles_timeout` - String extraction timeouts

**Purpose:** Verify tools fail gracefully with appropriate error messages.

**Run:** `pytest tests/test_forensic_server.py::TestErrorHandling -v`

### 4. Parser Tests (5 tests)
Tests output parsing correctness:
- `test_parse_volatility_pslist_output` - Process list parsing
- `test_parse_volatility_netscan_output` - Network connection parsing
- `test_parse_binwalk_signatures` - Signature offset/description parsing
- `test_parse_tshark_json` - JSON packet parsing
- `test_parse_foremost_audit` - Audit file and carved file counting

**Purpose:** Verify parsing functions correctly extract data from tool outputs.

**Run:** `pytest tests/test_forensic_server.py::TestParsers -v`

### 5. String Analysis Tests (3 tests)
Tests pattern detection in extracted strings:
- `test_analyze_strings_patterns` - URL, email, IP, path detection
- `test_analyze_strings_deduplication` - Duplicate removal
- `test_analyze_strings_empty_input` - Empty input handling

**Purpose:** Verify string analysis correctly identifies security-relevant patterns.

**Run:** `pytest tests/test_forensic_server.py::TestStringAnalysis -v`

### 6. Tool Availability Tests (3 tests)
Tests health checks and tool detection:
- `test_health_check_tool_missing` - All tools missing scenario
- `test_health_check_partial_tools` - Some tools missing scenario
- `test_binwalk_tool_not_found` / `test_tshark_tool_not_found`

**Purpose:** Verify tool availability checking works correctly.

**Run:** `pytest tests/test_forensic_server.py::TestToolAvailability -v`

### 7. Context Logging Tests (3 tests)
Tests FastMCP context logging:
- `test_volatility_logs_to_context` - Volatility logging
- `test_binwalk_logs_to_context` - Binwalk logging
- `test_error_logging_to_context` - Error logging

**Purpose:** Verify progress and error messages are logged to context.

**Run:** `pytest tests/test_forensic_server.py::TestContextLogging -v`

### 8. Output Directory Handling (2 tests)
Tests temporary directory and output directory management:
- `test_foremost_creates_output_directory` - Directory creation
- `test_foremost_uses_temp_directory_by_default` - Default temp directory

**Purpose:** Verify output directories are created correctly.

**Run:** `pytest tests/test_forensic_server.py::TestOutputDirectoryHandling -v`

### 9. Option Handling Tests (4 tests)
Tests tool-specific options and flags:
- `test_binwalk_extract_option` - -e flag handling
- `test_tshark_display_filter_option` - Display filter passing
- `test_foremost_file_types_option` - File type filtering
- `test_strings_encoding_options` - Encoding flag handling

**Purpose:** Verify tool options are correctly passed to subprocess commands.

**Run:** `pytest tests/test_forensic_server.py::TestOptionHandling -v`

### 10. Edge Cases and Boundary Tests (4 tests)
Tests boundary conditions and edge cases:
- `test_volatility_multiple_plugins` - Multiple plugin execution
- `test_tshark_empty_pcap` - Empty PCAP handling
- `test_strings_large_output_truncation` - Output truncation at 1000 strings
- `test_tshark_protocol_counting` - Protocol statistics

**Purpose:** Verify correct handling of edge cases and boundaries.

**Run:** `pytest tests/test_forensic_server.py::TestEdgeCases -v`

### 11. Integration Tests (3 tests)
Tests multi-component integration scenarios:
- `test_volatility_with_profile` - Volatility profile specification
- `test_binwalk_multiple_analysis_options` - Combined options
- `test_tshark_with_field_extraction` - Field extraction

**Purpose:** Verify tools work correctly with multiple options combined.

**Run:** `pytest tests/test_forensic_server.py::TestIntegration -v`

## Test Fixtures

The test suite includes 12 comprehensive fixtures for creating test data:

### File Fixtures (5)
```python
mock_memory_dump          # 24KB test memory dump
mock_firmware_file        # Binary firmware file with ELF header
mock_pcap_file           # PCAP network capture file
mock_disk_image          # Disk image file
mock_binary_file         # Binary with detectable strings
```

### Context Fixtures (1)
```python
mock_context             # Async mock FastMCP Context
```

### Output Fixtures (7)
```python
volatility_pslist_output          # Sample process list output
volatility_netscan_output         # Sample network connections
binwalk_signatures_output         # Sample binwalk signatures
tshark_json_output               # Sample tshark JSON packets
foremost_audit_output            # Sample foremost results
strings_with_patterns            # Strings with URLs, emails, IPs
```

### Mock Fixtures (2)
```python
mock_subprocess          # Mocked subprocess.run
patch_tool_paths        # Patches Path.exists() for tool availability
```

All fixtures use pytest's `tmp_path` to create temporary files, ensuring:
- No permanent files created
- Proper cleanup after tests
- Isolation between tests

## Key Testing Features

### Security-First Design
1. **16 dedicated security tests** verify input validation
2. **Path traversal prevention** blocks directory attacks
3. **Parameter validation** prevents injection attacks
4. **Subprocess safety** - no shell=True anywhere
5. **File validation** checks existence and type

### Comprehensive Mocking
- All subprocess calls are mocked (no real tool execution)
- Tool paths are mocked via Path.exists() patches
- Temporary files created via pytest's tmp_path fixture
- Context logging mocked with AsyncMock

### Realistic Test Data
- Actual volatility output format samples
- Real binwalk signature format
- Authentic tshark JSON structure
- Proper foremost audit.txt format
- Strings with security-relevant patterns (passwords, APIs, IPs)

### Error Path Coverage
- Timeout scenarios (subprocess.TimeoutExpired)
- Missing tools (tool binary not found)
- Malformed output (invalid JSON)
- File not found scenarios
- Directory instead of file

## Coverage Metrics

### Expected Coverage by Component
- **volatility_analyze()** - 95%+ coverage
- **binwalk_analyze()** - 95%+ coverage
- **tshark_analyze()** - 95%+ coverage
- **foremost_carve()** - 95%+ coverage
- **strings_extract()** - 95%+ coverage
- **health_check()** - 100% coverage
- **Parser functions** - 100% coverage
- **String analysis** - 100% coverage

### Overall Target
**90%+ code coverage** for the entire forensic_server module

### Running Coverage Analysis
```bash
# Show which lines are not covered
pytest tests/test_forensic_server.py \
  --cov=src.mcp_servers.forensic_server \
  --cov-report=term-missing

# Generate HTML coverage report
pytest tests/test_forensic_server.py \
  --cov=src.mcp_servers.forensic_server \
  --cov-report=html
# Open htmlcov/index.html in browser
```

## Async Testing with pytest-asyncio

All async functions are tested using `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_volatility_analyze_memory_dump(mock_memory_dump, mock_context):
    result = await volatility_analyze(
        memory_dump=mock_memory_dump,
        ctx=mock_context
    )
    assert result["status"] == "completed"
```

### Run with proper asyncio mode:
```bash
pytest tests/test_forensic_server.py -v --asyncio-mode=auto
```

## Important Notes

### No Real Tool Execution
All tests mock subprocess.run() to prevent:
- Actually running forensic tools
- Creating real output files
- Requiring tool installation
- Long test execution times

### Permanent Test Files
The forensic_server.py uses temp files for foremost output. Tests handle this with:
```python
@pytest.fixture
def foremost_audit_output(tmp_path):
    # Creates real directory structure for testing
    output_dir = tmp_path / "foremost_output"
    # ... create audit.txt and subdirectories
    return str(output_dir)
```

### Path Validation Testing
Security tests verify path validation without using real sensitive paths:
```python
async def test_volatility_rejects_directory_traversal(mock_context):
    result = await volatility_analyze(
        memory_dump="../../../etc/passwd"
    )
    assert result["status"] == "failed"
    assert "must be absolute" in result["error"]
```

## Common Test Patterns

### Testing a Tool Function
```python
@pytest.mark.asyncio
async def test_tool_function(mock_file, mock_context, mock_subprocess, patch_tool_paths):
    result = await tool_function(
        file_path=mock_file,
        ctx=mock_context
    )
    assert result["status"] == "completed"
    assert "expected_key" in result
```

### Testing Security Validation
```python
@pytest.mark.security
@pytest.mark.asyncio
async def test_tool_rejects_invalid_input(mock_context):
    result = await tool_function(
        file_path="invalid_input",
        ctx=mock_context
    )
    assert result["status"] == "failed"
    assert "error" in result
```

### Testing Error Handling
```python
@pytest.mark.asyncio
async def test_tool_handles_error(mock_context, patch_tool_paths):
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Error message")
        result = await tool_function(file_path=valid_file)
        assert result["status"] == "failed"
```

### Testing Parsers
```python
def test_parser_function(sample_output):
    result = _parse_output(sample_output)
    assert result["status"] == "completed"
    assert "expected_key" in result
    assert len(result["data"]) > 0
```

## Troubleshooting

### Tests Fail with "ModuleNotFoundError: No module named 'pytest'"
Install test dependencies:
```bash
pip install -e ".[dev]"
# or
pip install pytest pytest-asyncio pytest-cov
```

### Tests Fail with asyncio-related errors
Ensure pytest-asyncio is installed and use:
```bash
pytest tests/test_forensic_server.py --asyncio-mode=auto
```

### Tests Pass but Coverage is Low
Check which lines are not covered:
```bash
pytest tests/test_forensic_server.py \
  --cov=src.mcp_servers.forensic_server \
  --cov-report=term-missing
```

### Subprocess Mock Not Working
Ensure you're using the correct patch path:
```python
# Correct - patches where it's used
@patch('src.mcp_servers.forensic_server.subprocess.run')

# Wrong - patches where it's defined
@patch('subprocess.run')
```

## Contributing New Tests

When adding tests to this suite:

1. **Follow the naming convention:** `test_<component>_<scenario>`
2. **Use appropriate markers:**
   - `@pytest.mark.asyncio` - for async functions
   - `@pytest.mark.security` - for security tests
   - `@pytest.mark.integration` - for integration tests
3. **Include docstrings** explaining what is tested
4. **Use fixtures** for common test data
5. **Mock external dependencies** (subprocess, file system)
6. **Test both success and failure paths**
7. **Keep tests independent** - no test should depend on another

## Test Execution Examples

### Run all tests with verbose output
```bash
pytest tests/test_forensic_server.py -v
```

### Run only security tests
```bash
pytest tests/test_forensic_server.py -v -m security
```

### Run tests matching a pattern
```bash
pytest tests/test_forensic_server.py -v -k "volatility"
```

### Run a specific test class
```bash
pytest tests/test_forensic_server.py::TestHappyPathTests -v
```

### Run a specific test function
```bash
pytest tests/test_forensic_server.py::TestHappyPathTests::test_volatility_analyze_memory_dump -v
```

### Run with coverage and stop on first failure
```bash
pytest tests/test_forensic_server.py -x --cov=src.mcp_servers.forensic_server
```

### Run with detailed failure output
```bash
pytest tests/test_forensic_server.py -vv --tb=long
```

### Run in parallel (requires pytest-xdist)
```bash
pip install pytest-xdist
pytest tests/test_forensic_server.py -n auto
```

## Related Files

- **Module under test:** `/home/kali/kali-agents-mcp/src/mcp_servers/forensic_server.py`
- **Test configuration:** `/home/kali/kali-agents-mcp/pyproject.toml`
- **Test fixtures:** `/home/kali/kali-agents-mcp/tests/conftest.py`
- **Other test files:** `/home/kali/kali-agents-mcp/tests/test_*.py`

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Plugin](https://pytest-asyncio.readthedocs.io/)
- [pytest Coverage Plugin](https://pytest-cov.readthedocs.io/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

