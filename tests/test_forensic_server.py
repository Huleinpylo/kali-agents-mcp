# tests/test_forensic_server.py
"""
Comprehensive tests for Forensic Server MCP to achieve 90%+ coverage.

Security Focus:
- Path traversal prevention
- File validation
- Absolute path enforcement
- Input sanitization
- Subprocess safety (no shell=True)

Test Categories:
1. Happy Path Tests (6+ tests)
2. Security Tests (10+ tests)
3. Error Handling Tests (6+ tests)
4. Parser Tests (5+ tests)
5. Path Validation Tests (5+ tests)
"""

import pytest
import asyncio
import json
import tempfile
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
from typing import Dict, Any

try:
    from src.mcp_servers.forensic_server import (
        volatility_analyze,
        binwalk_analyze,
        tshark_analyze,
        foremost_carve,
        strings_extract,
        health_check,
        _parse_volatility_output,
        _parse_binwalk_output,
        _parse_tshark_output,
        _parse_foremost_output,
        _analyze_strings
    )
except ModuleNotFoundError:
    from mcp_servers.forensic_server import (
        volatility_analyze,
        binwalk_analyze,
        tshark_analyze,
        foremost_carve,
        strings_extract,
        health_check,
        _parse_volatility_output,
        _parse_binwalk_output,
        _parse_tshark_output,
        _parse_foremost_output,
        _analyze_strings
    )


# ============================================================================
# FIXTURES - Mock Forensic Files and Data
# ============================================================================

@pytest.fixture
def mock_memory_dump(tmp_path):
    """Create a temporary memory dump file for testing."""
    dump_file = tmp_path / "memory.dmp"
    dump_file.write_bytes(b"MOCK_MEMORY_DUMP_CONTENT" * 1000)
    return str(dump_file)


@pytest.fixture
def mock_firmware_file(tmp_path):
    """Create a temporary firmware file for testing."""
    firmware_file = tmp_path / "firmware.bin"
    firmware_file.write_bytes(b"\x7f\x45\x4c\x46" + b"MOCK_FIRMWARE" * 100)
    return str(firmware_file)


@pytest.fixture
def mock_pcap_file(tmp_path):
    """Create a temporary PCAP file for testing."""
    pcap_file = tmp_path / "traffic.pcap"
    pcap_file.write_bytes(b"\xd4\xc3\xb2\xa1" + b"MOCK_PCAP_DATA" * 100)
    return str(pcap_file)


@pytest.fixture
def mock_disk_image(tmp_path):
    """Create a temporary disk image file for testing."""
    image_file = tmp_path / "disk.img"
    image_file.write_bytes(b"MOCK_DISK_IMAGE" * 1000)
    return str(image_file)


@pytest.fixture
def mock_binary_file(tmp_path):
    """Create a temporary binary file for string extraction."""
    binary_file = tmp_path / "binary.exe"
    # Include detectable strings
    content = b"\x00\x00" + b"C:\\Windows\\System32" + b"\x00\x00"
    content += b"password123" + b"\x00\x00"
    content += b"https://example.com" + b"\x00\x00"
    content += b"admin@example.com" + b"\x00\x00"
    content += b"192.168.1.1"
    binary_file.write_bytes(content * 50)
    return str(binary_file)


@pytest.fixture
def mock_context():
    """Create a mock FastMCP Context."""
    context = AsyncMock()
    context.info = AsyncMock()
    context.error = AsyncMock()
    return context


@pytest.fixture
def volatility_pslist_output():
    """Sample volatility pslist output."""
    return """Volatility 3 Framework 3.14.0.post1
Scanning for processes...

PID     PPID    ImageFileName           Offset(V)       Offset(P)       CreateTime
4       0       System                  0x12345678      0x87654321      2024-01-15 10:00:00
328     4       smss.exe                0x9abcdef0      0xfedcba09      2024-01-15 10:00:05
652     328     csrss.exe               0x11111111      0x22222222      2024-01-15 10:00:10
888     652     winlogon.exe            0x33333333      0x44444444      2024-01-15 10:00:15
"""


@pytest.fixture
def volatility_netscan_output():
    """Sample volatility netscan output."""
    return """Volatility 3 Framework 3.14.0.post1
Scanning for network connections...

Protocol   Local Address       Remote Address      State   PID     Process
TCPv4      192.168.1.100:5357  0.0.0.0:0          LISTEN  4       System
TCPv4      192.168.1.100:139   0.0.0.0:0          LISTEN  328     smss.exe
TCPv4      192.168.1.100:445   192.168.1.50:12345 ESTABLISHED 888  winlogon.exe
"""


@pytest.fixture
def binwalk_signatures_output():
    """Sample binwalk signature scan output."""
    return """Scan Time:     2024-01-15 10:00:00
Target File:   /tmp/firmware.bin
MD5 Checksum:  abc123def456

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             ELF 32-bit LSB executable, ARM
512           0x200           Squashfs filesystem, little endian
8192          0x2000          LZMA compressed data, dictionary size: 8388608
16384         0x4000          gzip compressed data, from FAT filesystem
"""


@pytest.fixture
def tshark_json_output():
    """Sample tshark JSON output."""
    return json.dumps([
        {
            "_index": "packets-2024-01-15",
            "_type": "_doc",
            "_score": 0,
            "_source": {
                "layers": {
                    "frame": {
                        "frame.number": "1",
                        "frame.time": "Jan 15, 2024 10:00:00.000000000 UTC"
                    },
                    "ip": {
                        "ip.src": "192.168.1.100",
                        "ip.dst": "192.168.1.1"
                    },
                    "tcp": {
                        "tcp.srcport": "54321",
                        "tcp.dstport": "80"
                    }
                }
            }
        },
        {
            "_index": "packets-2024-01-15",
            "_type": "_doc",
            "_score": 0,
            "_source": {
                "layers": {
                    "frame": {
                        "frame.number": "2",
                        "frame.time": "Jan 15, 2024 10:00:00.001000000 UTC"
                    },
                    "ip": {
                        "ip.src": "192.168.1.1",
                        "ip.dst": "192.168.1.100"
                    },
                    "tcp": {
                        "tcp.srcport": "80",
                        "tcp.dstport": "54321"
                    }
                }
            }
        }
    ])


@pytest.fixture
def foremost_audit_output(tmp_path):
    """Create mock foremost audit.txt output."""
    output_dir = tmp_path / "foremost_output"
    output_dir.mkdir()

    # Create audit.txt
    audit_file = output_dir / "audit.txt"
    audit_content = """Foremost version 1.5.7
Input file: /tmp/disk.img
Output directory: /tmp/foremost_output
Start time: 2024-01-15 10:00:00
Command line: foremost -i /tmp/disk.img -o /tmp/foremost_output

Searching for File Type: jpg
Files recovered: 15

Searching for File Type: pdf
Files recovered: 8

Searching for File Type: doc
Files recovered: 5

Searching for File Type: zip
Files recovered: 3

End time: 2024-01-15 10:05:00
Total Run Time: 5 minutes
Total files recovered: 31
"""
    audit_file.write_text(audit_content)

    # Create fake recovered file directories
    (output_dir / "jpg").mkdir()
    for i in range(15):
        (output_dir / "jpg" / f"image_{i:05d}.jpg").write_bytes(b"JPEG_DATA")

    (output_dir / "pdf").mkdir()
    for i in range(8):
        (output_dir / "pdf" / f"document_{i:05d}.pdf").write_bytes(b"PDF_DATA")

    (output_dir / "doc").mkdir()
    for i in range(5):
        (output_dir / "doc" / f"file_{i:05d}.doc").write_bytes(b"DOC_DATA")

    return str(output_dir)


@pytest.fixture
def strings_with_patterns():
    """Sample strings with various patterns."""
    return [
        "C:\\Users\\Admin\\Documents",
        "password123",
        "/usr/local/bin",
        "https://github.com/example/repo",
        "admin@company.com",
        "192.168.1.100",
        "api_key=sk_live_abc123",
        "token=ghp_1234567890",
        "secret_value",
        "root:x:0:0",
        "10.0.0.5",
        "https://api.example.com/auth",
        "user@domain.org",
        "/var/log/system.log",
        "C:\\Program Files\\Application"
    ]


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for all forensic tools."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Mock tool output",
            stderr=""
        )
        yield mock_run


@pytest.fixture
def patch_tool_paths():
    """Patch all forensic tool paths to exist."""
    with patch('pathlib.Path.exists') as mock_exists:
        mock_exists.return_value = True
        yield mock_exists


# ============================================================================
# HAPPY PATH TESTS (6+ tests)
# ============================================================================

class TestHappyPathTests:
    """Test normal, expected behavior of forensic tools."""

    @pytest.mark.asyncio
    async def test_volatility_analyze_memory_dump(
        self, mock_memory_dump, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test volatility analysis on valid memory dump."""
        result = await volatility_analyze(
            memory_dump=mock_memory_dump,
            profile=None,
            plugins=["windows.pslist"],
            ctx=mock_context
        )

        assert result["status"] == "completed"
        assert result["dump"] == mock_memory_dump
        assert "plugins" in result
        assert "windows.pslist" in result["plugins"]
        mock_context.info.assert_called()

    @pytest.mark.asyncio
    async def test_binwalk_finds_signatures(
        self, mock_firmware_file, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test binwalk signature detection."""
        with patch('src.mcp_servers.forensic_server._parse_binwalk_output') as mock_parse:
            mock_parse.return_value = {
                "status": "completed",
                "signatures": [
                    {"offset": 0, "offset_hex": "0x0", "description": "ELF executable"},
                    {"offset": 512, "offset_hex": "0x200", "description": "Squashfs filesystem"}
                ]
            }

            result = await binwalk_analyze(
                firmware_file=mock_firmware_file,
                extract=False,
                signature=True,
                ctx=mock_context
            )

        assert result["status"] == "completed"
        assert result["file"] == mock_firmware_file
        assert "signatures" in result
        mock_context.info.assert_called()

    @pytest.mark.asyncio
    async def test_tshark_analyzes_pcap(
        self, mock_pcap_file, mock_context, tshark_json_output, mock_subprocess, patch_tool_paths
    ):
        """Test tshark PCAP analysis."""
        mock_subprocess.return_value.stdout = tshark_json_output

        result = await tshark_analyze(
            pcap_file=mock_pcap_file,
            display_filter="tcp",
            ctx=mock_context
        )

        assert result["status"] == "completed"
        assert result["file"] == mock_pcap_file
        assert result["packet_count"] == 2
        assert "packets" in result
        mock_context.info.assert_called()

    @pytest.mark.asyncio
    async def test_foremost_carves_files(
        self, mock_disk_image, mock_context, foremost_audit_output, mock_subprocess, patch_tool_paths
    ):
        """Test foremost file carving."""
        with patch('src.mcp_servers.forensic_server._parse_foremost_output') as mock_parse:
            mock_parse.return_value = {
                "status": "completed",
                "carved_files": {
                    "jpg": 15,
                    "pdf": 8,
                    "doc": 5,
                    "zip": 3
                },
                "total_carved": 31
            }

            result = await foremost_carve(
                image_file=mock_disk_image,
                output_dir=foremost_audit_output,
                file_types=["jpg", "pdf", "doc"],
                ctx=mock_context
            )

        assert result["status"] == "completed"
        assert result["image"] == mock_disk_image
        assert result["total_carved"] == 31
        mock_context.info.assert_called()

    @pytest.mark.asyncio
    async def test_strings_extracts_printable(
        self, mock_binary_file, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test strings extraction from binary."""
        mock_subprocess.return_value.stdout = (
            "C:\\\\Windows\\\\System32\npassword123\nhttps://example.com\nadmin@example.com\n"
        )

        result = await strings_extract(
            file_path=mock_binary_file,
            min_length=4,
            encoding="ascii",
            ctx=mock_context
        )

        assert result["status"] == "completed"
        assert result["file"] == mock_binary_file
        assert result["total_strings"] > 0
        assert result["min_length"] == 4
        mock_context.info.assert_called()

    @pytest.mark.asyncio
    async def test_health_check_all_tools_available(self, patch_tool_paths):
        """Test health check when all tools are available."""
        result = await health_check()

        assert result["status"] == "healthy"
        assert "tools" in result
        assert "volatility3" in result["tools"]
        assert "binwalk" in result["tools"]
        assert "tshark" in result["tools"]
        assert "foremost" in result["tools"]
        assert "strings" in result["tools"]


# ============================================================================
# SECURITY TESTS (10+ tests) - CRITICAL
# ============================================================================

class TestSecurityPathTraversal:
    """Test path traversal prevention."""

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_volatility_rejects_relative_paths(self, mock_context):
        """Test that volatility rejects relative paths."""
        result = await volatility_analyze(
            memory_dump="memory.dmp",
            ctx=mock_context
        )

        assert result["status"] == "failed"
        assert "must be absolute" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_volatility_rejects_directory_traversal(self, mock_context):
        """Test that volatility rejects directory traversal attempts."""
        malicious_paths = [
            "../../../etc/passwd",
            "../../.ssh/id_rsa",
            "/tmp/../../../etc/shadow",
            "/var/log/../../etc/passwd"
        ]

        for path in malicious_paths:
            result = await volatility_analyze(
                memory_dump=path,
                ctx=mock_context
            )
            assert result["status"] == "failed"
            assert "must be absolute" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_binwalk_validates_file_path(self, mock_context):
        """Test binwalk validates absolute file paths."""
        result = await binwalk_analyze(
            firmware_file="./firmware.bin",
            ctx=mock_context
        )

        assert result["status"] == "failed"
        assert "must be absolute" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_tshark_validates_pcap_path(self, mock_context):
        """Test tshark validates absolute PCAP paths."""
        result = await tshark_analyze(
            pcap_file="./traffic.pcap",
            ctx=mock_context
        )

        assert result["status"] == "failed"
        assert "must be absolute" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_foremost_validates_image_path(self, mock_context):
        """Test foremost validates absolute image paths."""
        result = await foremost_carve(
            image_file="disk.img",
            ctx=mock_context
        )

        assert result["status"] == "failed"
        assert "must be absolute" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_foremost_validates_output_path(self, mock_context, mock_disk_image):
        """Test foremost validates absolute output directory paths."""
        result = await foremost_carve(
            image_file=mock_disk_image,
            output_dir="./output",
            ctx=mock_context
        )

        assert result["status"] == "failed"
        assert "must be absolute" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_strings_rejects_relative_paths(self, mock_context):
        """Test strings rejects relative paths."""
        result = await strings_extract(
            file_path="./binary.exe",
            ctx=mock_context
        )

        assert result["status"] == "failed"
        assert "must be absolute" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_strings_validates_min_length_bounds(self, mock_binary_file):
        """Test strings validates min_length parameter."""
        # Test below minimum
        result = await strings_extract(
            file_path=mock_binary_file,
            min_length=0,
        )
        assert result["status"] == "failed"
        assert "1-100" in result["error"]

        # Test above maximum
        result = await strings_extract(
            file_path=mock_binary_file,
            min_length=101,
        )
        assert result["status"] == "failed"
        assert "1-100" in result["error"]

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_strings_validates_encoding_whitelist(self, mock_binary_file):
        """Test strings validates encoding against whitelist."""
        result = await strings_extract(
            file_path=mock_binary_file,
            encoding="invalid_encoding",
        )

        assert result["status"] == "failed"
        assert "Invalid encoding" in result["error"]
        assert "Allowed:" in result["error"]

    @pytest.mark.security
    def test_no_shell_true_in_subprocess_calls(self, mock_memory_dump, patch_tool_paths):
        """Test that subprocess.run is never called with shell=True."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            # Run all tools with mocked subprocess
            asyncio.run(volatility_analyze(
                memory_dump=mock_memory_dump,
                plugins=["windows.pslist"]
            ))

            # Verify subprocess.run was called without shell=True
            for call in mock_run.call_args_list:
                # Check that shell is not in kwargs or shell is False
                if 'shell' in call.kwargs:
                    assert call.kwargs['shell'] is False


# ============================================================================
# FILE VALIDATION TESTS (5+ tests)
# ============================================================================

class TestFileValidation:
    """Test file validation and existence checking."""

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_volatility_rejects_non_existent_files(self, mock_context):
        """Test volatility rejects non-existent files."""
        result = await volatility_analyze(
            memory_dump="/nonexistent/path/memory.dmp",
            ctx=mock_context
        )

        assert result["status"] == "failed"
        assert "not found" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_volatility_rejects_directories(self, tmp_path, mock_context):
        """Test volatility rejects directory paths."""
        dir_path = str(tmp_path / "somedir")
        Path(dir_path).mkdir()

        result = await volatility_analyze(
            memory_dump=dir_path,
            ctx=mock_context
        )

        assert result["status"] == "failed"
        assert "directory" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_binwalk_validates_file_exists(self, mock_context):
        """Test binwalk validates file exists."""
        result = await binwalk_analyze(
            firmware_file="/nonexistent/firmware.bin",
            ctx=mock_context
        )

        assert result["status"] == "failed"
        assert "not found" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_tshark_validates_file_exists(self, mock_context):
        """Test tshark validates PCAP file exists."""
        result = await tshark_analyze(
            pcap_file="/nonexistent/traffic.pcap",
            ctx=mock_context
        )

        assert result["status"] == "failed"
        assert "not found" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_foremost_validates_image_exists(self, mock_context):
        """Test foremost validates image file exists."""
        result = await foremost_carve(
            image_file="/nonexistent/disk.img",
            ctx=mock_context
        )

        assert result["status"] == "failed"
        assert "not found" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_strings_validates_file_exists(self, mock_context):
        """Test strings validates file exists."""
        result = await strings_extract(
            file_path="/nonexistent/binary.exe",
        )

        assert result["status"] == "failed"
        assert "not found" in result["error"].lower()


# ============================================================================
# ERROR HANDLING TESTS (6+ tests)
# ============================================================================

class TestErrorHandling:
    """Test error handling for various failure scenarios."""

    @pytest.mark.asyncio
    async def test_volatility_handles_timeout(
        self, mock_memory_dump, mock_context, patch_tool_paths
    ):
        """Test volatility timeout handling."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("vol3", 600)

            result = await volatility_analyze(
                memory_dump=mock_memory_dump,
                plugins=["windows.pslist"],
                ctx=mock_context
            )

        assert result["status"] == "completed"
        assert result["plugins"]["windows.pslist"]["status"] == "timeout"

    @pytest.mark.asyncio
    async def test_volatility_handles_tool_not_found(self, mock_memory_dump, mock_context):
        """Test volatility when tool is not installed."""
        with patch('pathlib.Path.exists', return_value=False):
            result = await volatility_analyze(
                memory_dump=mock_memory_dump,
                ctx=mock_context
            )

        assert result["status"] == "failed"
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_binwalk_handles_subprocess_error(
        self, mock_firmware_file, mock_context, patch_tool_paths
    ):
        """Test binwalk subprocess error handling."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Subprocess error")

            result = await binwalk_analyze(
                firmware_file=mock_firmware_file,
                ctx=mock_context
            )

        assert result["status"] == "failed"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_tshark_handles_malformed_json(
        self, mock_pcap_file, mock_context, patch_tool_paths
    ):
        """Test tshark handles malformed JSON output."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "{ invalid json [[[["

            result = await tshark_analyze(
                pcap_file=mock_pcap_file,
                ctx=mock_context
            )

        assert result["status"] == "parse_error"
        assert "parse" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_foremost_handles_timeout(
        self, mock_disk_image, mock_context, patch_tool_paths
    ):
        """Test foremost timeout handling."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("foremost", 900)

            result = await foremost_carve(
                image_file=mock_disk_image,
                ctx=mock_context
            )

        assert result["status"] == "timeout"
        assert "timeout" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_strings_handles_timeout(
        self, mock_binary_file, mock_context, patch_tool_paths
    ):
        """Test strings timeout handling."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("strings", 120)

            result = await strings_extract(
                file_path=mock_binary_file,
            )

        assert result["status"] == "timeout"
        assert "timeout" in result["error"].lower()


# ============================================================================
# PARSER TESTS (5+ tests)
# ============================================================================

class TestParsers:
    """Test output parsing functions."""

    def test_parse_volatility_pslist_output(self, volatility_pslist_output):
        """Test parsing volatility pslist output."""
        result = _parse_volatility_output(volatility_pslist_output, "windows.pslist")

        assert result["status"] == "completed"
        assert result["plugin"] == "windows.pslist"
        assert "data" in result
        assert len(result["data"]) > 0

        # Check parsed process data
        processes = result["data"]
        assert any("process" in p.get("type", "") for p in processes)

    def test_parse_volatility_netscan_output(self, volatility_netscan_output):
        """Test parsing volatility netscan output."""
        result = _parse_volatility_output(volatility_netscan_output, "windows.netscan")

        assert result["status"] == "completed"
        assert result["plugin"] == "windows.netscan"
        assert "data" in result
        assert len(result["data"]) > 0

        # Check parsed network data
        network_data = result["data"]
        assert any("network" in p.get("type", "") for p in network_data)

    def test_parse_binwalk_signatures(self, binwalk_signatures_output):
        """Test parsing binwalk signature output."""
        result = _parse_binwalk_output(binwalk_signatures_output, Path("/tmp/firmware.bin"))

        assert result["status"] == "completed"
        assert "signatures" in result
        assert len(result["signatures"]) > 0

        # Check signature format
        for sig in result["signatures"]:
            assert "offset" in sig
            assert "offset_hex" in sig
            assert "description" in sig
            assert isinstance(sig["offset"], int)

    def test_parse_tshark_json(self, tshark_json_output):
        """Test parsing tshark JSON output."""
        result = _parse_tshark_output(tshark_json_output)

        assert result["status"] == "completed"
        assert result["packet_count"] == 2
        assert "packets" in result
        assert "protocols" in result
        assert len(result["protocols"]) > 0

    def test_parse_foremost_audit(self, foremost_audit_output):
        """Test parsing foremost audit output."""
        result = _parse_foremost_output(foremost_audit_output)

        assert result["status"] == "completed"
        assert "carved_files" in result
        assert result["total_carved"] == 31
        assert result["carved_files"]["jpg"] == 15
        assert result["carved_files"]["pdf"] == 8
        assert "audit" in result


# ============================================================================
# STRING ANALYSIS TESTS
# ============================================================================

class TestStringAnalysis:
    """Test string pattern analysis."""

    def test_analyze_strings_patterns(self, strings_with_patterns):
        """Test analyzing strings for interesting patterns."""
        analysis = _analyze_strings(strings_with_patterns)

        assert "urls" in analysis
        assert "emails" in analysis
        assert "ip_addresses" in analysis
        assert "file_paths" in analysis
        assert "interesting_keywords" in analysis

        # Check that patterns are detected
        assert len(analysis["urls"]) > 0
        assert len(analysis["emails"]) > 0
        assert len(analysis["ip_addresses"]) > 0
        assert len(analysis["file_paths"]) > 0
        assert len(analysis["interesting_keywords"]) > 0

    def test_analyze_strings_deduplication(self):
        """Test that duplicate strings are removed in analysis."""
        strings = [
            "https://example.com",
            "https://example.com",
            "https://example.com",
            "admin@test.com",
            "admin@test.com"
        ]

        analysis = _analyze_strings(strings)

        # Check deduplication
        assert len(analysis["urls"]) == 1
        assert len(analysis["emails"]) == 1

    def test_analyze_strings_empty_input(self):
        """Test analyzing empty string list."""
        analysis = _analyze_strings([])

        assert analysis["urls"] == []
        assert analysis["emails"] == []
        assert analysis["ip_addresses"] == []
        assert analysis["file_paths"] == []
        assert analysis["interesting_keywords"] == []


# ============================================================================
# TOOL AVAILABILITY TESTS
# ============================================================================

class TestToolAvailability:
    """Test tool availability checks."""

    @pytest.mark.asyncio
    async def test_health_check_tool_missing(self):
        """Test health check when tools are missing."""
        with patch('pathlib.Path.exists', return_value=False):
            result = await health_check()

        assert result["status"] == "degraded"
        assert all(not v for v in result["tools"].values())

    @pytest.mark.asyncio
    async def test_health_check_partial_tools(self):
        """Test health check with some tools missing."""
        def side_effect(self):
            # Only volatility available
            return "/usr/bin/vol3" in str(self) and "vol3" in str(self)

        with patch('pathlib.Path.exists', side_effect=side_effect):
            result = await health_check()

        assert result["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_binwalk_tool_not_found(self, mock_firmware_file, mock_context):
        """Test binwalk when tool is not available."""
        with patch('pathlib.Path.exists', return_value=False):
            result = await binwalk_analyze(
                firmware_file=mock_firmware_file,
                ctx=mock_context
            )

        assert result["status"] == "failed"
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_tshark_tool_not_found(self, mock_pcap_file, mock_context):
        """Test tshark when tool is not available."""
        with patch('pathlib.Path.exists', return_value=False):
            result = await tshark_analyze(
                pcap_file=mock_pcap_file,
                ctx=mock_context
            )

        assert result["status"] == "failed"
        assert "not found" in result["error"].lower()


# ============================================================================
# CONTEXT LOGGING TESTS
# ============================================================================

class TestContextLogging:
    """Test context logging functionality."""

    @pytest.mark.asyncio
    async def test_volatility_logs_to_context(
        self, mock_memory_dump, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test that volatility logs progress to context."""
        result = await volatility_analyze(
            memory_dump=mock_memory_dump,
            plugins=["windows.pslist"],
            ctx=mock_context
        )

        assert result["status"] == "completed"
        # Verify context logging was called
        assert mock_context.info.called
        # Should log start, plugin run, and completion
        assert mock_context.info.call_count >= 3

    @pytest.mark.asyncio
    async def test_binwalk_logs_to_context(
        self, mock_firmware_file, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test that binwalk logs progress to context."""
        with patch('src.mcp_servers.forensic_server._parse_binwalk_output') as mock_parse:
            mock_parse.return_value = {"status": "completed", "signatures": []}

            result = await binwalk_analyze(
                firmware_file=mock_firmware_file,
                ctx=mock_context
            )

        assert result["status"] == "completed"
        assert mock_context.info.called

    @pytest.mark.asyncio
    async def test_error_logging_to_context(
        self, mock_firmware_file, mock_context, patch_tool_paths
    ):
        """Test that errors are logged to context."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Tool error")

            result = await binwalk_analyze(
                firmware_file=mock_firmware_file,
                ctx=mock_context
            )

        assert result["status"] == "failed"
        assert mock_context.error.called


# ============================================================================
# OUTPUT DIRECTORY CREATION TESTS
# ============================================================================

class TestOutputDirectoryHandling:
    """Test output directory creation and validation."""

    @pytest.mark.asyncio
    async def test_foremost_creates_output_directory(
        self, mock_disk_image, tmp_path, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test that foremost creates output directory if it doesn't exist."""
        output_dir = str(tmp_path / "new_output_dir")

        with patch('src.mcp_servers.forensic_server._parse_foremost_output') as mock_parse:
            mock_parse.return_value = {
                "status": "completed",
                "carved_files": {},
                "total_carved": 0
            }

            result = await foremost_carve(
                image_file=mock_disk_image,
                output_dir=output_dir,
                ctx=mock_context
            )

        assert result["status"] == "completed"
        assert Path(output_dir).exists()

    @pytest.mark.asyncio
    async def test_foremost_uses_temp_directory_by_default(
        self, mock_disk_image, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test that foremost uses temp directory when output_dir is None."""
        with patch('src.mcp_servers.forensic_server._parse_foremost_output') as mock_parse:
            mock_parse.return_value = {
                "status": "completed",
                "carved_files": {},
                "total_carved": 0
            }

            result = await foremost_carve(
                image_file=mock_disk_image,
                output_dir=None,
                ctx=mock_context
            )

        assert result["status"] == "completed"
        assert result["output_dir"].startswith("/tmp")


# ============================================================================
# OPTION HANDLING TESTS
# ============================================================================

class TestOptionHandling:
    """Test tool option handling."""

    @pytest.mark.asyncio
    async def test_binwalk_extract_option(
        self, mock_firmware_file, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test binwalk with extract option."""
        with patch('src.mcp_servers.forensic_server._parse_binwalk_output') as mock_parse:
            mock_parse.return_value = {"status": "completed", "signatures": []}

            result = await binwalk_analyze(
                firmware_file=mock_firmware_file,
                extract=True,
                ctx=mock_context
            )

        assert result["status"] == "completed"
        assert result["options"]["extract"] is True
        # Verify -e flag was passed
        call_args = mock_subprocess.call_args
        if call_args:
            assert "-e" in str(call_args) or "extract" in str(call_args)

    @pytest.mark.asyncio
    async def test_tshark_display_filter_option(
        self, mock_pcap_file, mock_context, tshark_json_output, mock_subprocess, patch_tool_paths
    ):
        """Test tshark with display filter option."""
        mock_subprocess.return_value.stdout = tshark_json_output

        result = await tshark_analyze(
            pcap_file=mock_pcap_file,
            display_filter="tcp.port == 443",
            ctx=mock_context
        )

        assert result["status"] == "completed"
        assert result["filters"]["display_filter"] == "tcp.port == 443"

    @pytest.mark.asyncio
    async def test_foremost_file_types_option(
        self, mock_disk_image, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test foremost with file type filters."""
        with patch('src.mcp_servers.forensic_server._parse_foremost_output') as mock_parse:
            mock_parse.return_value = {
                "status": "completed",
                "carved_files": {"jpg": 10},
                "total_carved": 10
            }

            result = await foremost_carve(
                image_file=mock_disk_image,
                file_types=["jpg", "png"],
                ctx=mock_context
            )

        assert result["status"] == "completed"
        assert result["file_types"] == ["jpg", "png"]

    @pytest.mark.asyncio
    async def test_strings_encoding_options(
        self, mock_binary_file, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test strings with different encoding options."""
        mock_subprocess.return_value.stdout = "test string\n"

        # Test unicode encoding
        result = await strings_extract(
            file_path=mock_binary_file,
            encoding="unicode",
        )

        assert result["status"] == "completed"
        assert result["encoding"] == "unicode"


# ============================================================================
# EDGE CASES AND BOUNDARY TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_volatility_multiple_plugins(
        self, mock_memory_dump, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test volatility with multiple plugins."""
        result = await volatility_analyze(
            memory_dump=mock_memory_dump,
            plugins=["windows.pslist", "windows.netscan", "windows.filescan"],
            ctx=mock_context
        )

        assert result["status"] == "completed"
        assert len(result["plugins"]) == 3
        assert "windows.pslist" in result["plugins"]
        assert "windows.netscan" in result["plugins"]
        assert "windows.filescan" in result["plugins"]

    @pytest.mark.asyncio
    async def test_tshark_empty_pcap(
        self, mock_pcap_file, mock_context, patch_tool_paths
    ):
        """Test tshark with empty PCAP file."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = ""

            result = await tshark_analyze(
                pcap_file=mock_pcap_file,
                ctx=mock_context
            )

        assert result["status"] == "completed"
        assert result["packet_count"] == 0

    @pytest.mark.asyncio
    async def test_strings_large_output_truncation(
        self, mock_binary_file, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test strings output truncation for large results."""
        # Create output with > 1000 strings
        large_output = "\n".join([f"string_{i}" for i in range(2000)])
        mock_subprocess.return_value.stdout = large_output

        result = await strings_extract(
            file_path=mock_binary_file,
        )

        assert result["status"] == "completed"
        assert len(result["strings"]) == 1000
        assert result["truncated"] is True

    def test_tshark_protocol_counting(self):
        """Test protocol counting in tshark output."""
        json_output = json.dumps([
            {
                "_source": {
                    "layers": {"frame": {}, "ip": {}, "tcp": {}}
                }
            },
            {
                "_source": {
                    "layers": {"frame": {}, "ip": {}, "udp": {}}
                }
            },
            {
                "_source": {
                    "layers": {"frame": {}, "ip": {}}
                }
            }
        ])

        result = _parse_tshark_output(json_output)

        assert result["protocols"]["frame"] == 3
        assert result["protocols"]["ip"] == 3
        assert result["protocols"]["tcp"] == 1
        assert result["protocols"]["udp"] == 1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test integration scenarios."""

    @pytest.mark.asyncio
    async def test_volatility_with_profile(
        self, mock_memory_dump, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test volatility with explicit profile."""
        result = await volatility_analyze(
            memory_dump=mock_memory_dump,
            profile="Win7SP1x64",
            plugins=["windows.pslist"],
            ctx=mock_context
        )

        assert result["status"] == "completed"
        assert result["profile"] == "Win7SP1x64"

    @pytest.mark.asyncio
    async def test_binwalk_multiple_analysis_options(
        self, mock_firmware_file, mock_context, mock_subprocess, patch_tool_paths
    ):
        """Test binwalk with multiple analysis options."""
        with patch('src.mcp_servers.forensic_server._parse_binwalk_output') as mock_parse:
            mock_parse.return_value = {"status": "completed", "signatures": []}

            result = await binwalk_analyze(
                firmware_file=mock_firmware_file,
                extract=True,
                signature=True,
                entropy=True,
                ctx=mock_context
            )

        assert result["status"] == "completed"
        assert result["options"]["extract"] is True
        assert result["options"]["signature"] is True
        assert result["options"]["entropy"] is True

    @pytest.mark.asyncio
    async def test_tshark_with_field_extraction(
        self, mock_pcap_file, mock_context, tshark_json_output, mock_subprocess, patch_tool_paths
    ):
        """Test tshark with field extraction."""
        mock_subprocess.return_value.stdout = tshark_json_output

        result = await tshark_analyze(
            pcap_file=mock_pcap_file,
            fields=["frame.time", "ip.src", "ip.dst", "tcp.srcport"],
            ctx=mock_context
        )

        assert result["status"] == "completed"
        assert result["packet_count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
