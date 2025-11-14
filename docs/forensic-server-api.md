# Forensic Server API Documentation

**Server**: ForensicAgent
**Version**: 1.0.0
**Protocol**: FastMCP
**Port**: 5004 (default)

⚠️ **AUTHORIZED USE ONLY**: Digital forensics tools must only be used on systems and files you own or have explicit permission to analyze.

---

## Overview

The Forensic Server provides digital forensics and malware analysis capabilities through integration with industry-standard forensic tools.

### Supported Tools

- **Volatility 3** - Memory forensics and dump analysis
- **Binwalk** - Firmware and binary analysis with signature detection
- **TShark** - Network traffic PCAP analysis (Wireshark CLI)
- **Foremost** - File carving from disk images
- **Strings** - Printable string extraction with pattern analysis

### Quality & Testing

- **Test Suite**: 56 tests with `@pytest.mark.security`, `@pytest.mark.asyncio`, path validation, and parser coverage
- **Coverage**: 90%+ for `src/mcp_servers/forensic_server.py`
- **Security**: No `shell=True`, absolute path validation, file existence checks, timeout guards (10m volatility, 5m binwalk, 2.5m tshark, 15m foremost, 1m strings)

---

## API Reference

### volatility_analyze

Analyze memory dumps using Volatility 3.

**Parameters:**
- `memory_dump` (str, required): Absolute path to memory dump file
- `profile` (str, optional): OS profile (auto-detected if not specified)
- `plugins` (List[str], optional): Plugins to run (default: ["windows.pslist", "windows.netscan"])

**Returns:**
```json
{
  "status": "completed",
  "dump": "/path/to/memory.dmp",
  "profile": "auto-detected",
  "plugins": {
    "windows.pslist": {"status": "completed", "data": [...]},
    "windows.netscan": {"status": "completed", "data": [...]}
  }
}
```

**Security:** Absolute path required, file existence checked, 10-minute timeout

---

### binwalk_analyze

Analyze firmware and binary files using binwalk.

**Parameters:**
- `firmware_file` (str, required): Absolute path to firmware/binary file
- `extract` (bool, optional): Extract discovered filesystems (default: False)
- `signature` (bool, optional): Perform signature scan (default: True)
- `entropy` (bool, optional): Calculate entropy analysis (default: False)

**Returns:**
```json
{
  "status": "completed",
  "file": "/path/to/firmware.bin",
  "options": {"extract": false, "signature": true, "entropy": false},
  "signatures": [
    {"offset": 0, "offset_hex": "0x0", "description": "ELF 64-bit LSB executable"}
  ]
}
```

**Security:** Absolute path required, 5-minute timeout

---

### tshark_analyze

Analyze network traffic using tshark (Wireshark CLI).

**Parameters:**
- `pcap_file` (str, required): Absolute path to pcap/pcapng file
- `display_filter` (str, optional): Display filter (e.g., "http", "tcp.port == 80")
- `read_filter` (str, optional): Read filter during capture reading
- `fields` (List[str], optional): Fields to extract (e.g., ["frame.time", "ip.src", "ip.dst"])

**Returns:**
```json
{
  "status": "completed",
  "file": "/path/to/capture.pcapng",
  "packet_count": 1523,
  "packets": [...],
  "protocols": {"tcp": 1200, "udp": 200, "http": 123},
  "truncated": true
}
```

**Security:** Absolute path required, 2.5-minute timeout

---

### foremost_carve

Carve files from disk images using foremost.

**Parameters:**
- `image_file` (str, required): Absolute path to disk image file
- `output_dir` (str, optional): Output directory for carved files (default: temp directory)
- `file_types` (List[str], optional): File types to carve (e.g., ["jpg", "pdf", "doc"]) (default: all)

**Returns:**
```json
{
  "status": "completed",
  "image": "/path/to/image.dd",
  "output_dir": "/tmp/foremost_xyz123",
  "total_carved": 42,
  "carved_files": {"jpg": 25, "pdf": 10, "doc": 7},
  "audit": "Foremost version..."
}
```

**Security:** Absolute paths required, 15-minute timeout for large images

---

### strings_extract

Extract printable strings from binary files.

**Parameters:**
- `file_path` (str, required): Absolute path to file to analyze
- `min_length` (int, optional): Minimum string length 1-100 (default: 4)
- `encoding` (str, optional): String encoding: ascii, unicode, utf-8 (default: ascii)

**Returns:**
```json
{
  "status": "completed",
  "file": "/path/to/binary",
  "total_strings": 5432,
  "strings": ["string1", "string2", ...],
  "truncated": true,
  "analysis": {
    "urls": ["http://example.com"],
    "emails": ["admin@example.com"],
    "ip_addresses": ["192.168.1.1"],
    "file_paths": ["C:\\Windows\\System32"],
    "interesting_keywords": ["password=secret123"]
  }
}
```

**Security:** Absolute path required, min_length 1-100 validated, encoding whitelist enforced, 1-minute timeout

---

### health_check

Check server health and tool availability.

**Returns:**
```json
{
  "status": "healthy",
  "tools": {
    "volatility3": true,
    "binwalk": true,
    "tshark": true,
    "foremost": true,
    "strings": true
  },
  "server": "ForensicAgent",
  "version": "1.0.0"
}
```

---

## Usage Examples

### Python Client

```python
from mcp_client import MCPClient

async def forensic_analysis(memory_dump_path, pcap_path):
    client = MCPClient("forensic-server")

    # 1. Memory dump analysis
    vol_results = await client.call_tool("volatility_analyze", {
        "memory_dump": memory_dump_path,
        "plugins": ["windows.pslist", "windows.netscan", "windows.cmdline"]
    })

    # 2. Network traffic analysis
    tshark_results = await client.call_tool("tshark_analyze", {
        "pcap_file": pcap_path,
        "display_filter": "http or dns"
    })

    # 3. Extract strings from binary
    strings_results = await client.call_tool("strings_extract", {
        "file_path": "/path/to/malware.exe",
        "min_length": 6
    })

    return {
        "memory": vol_results,
        "network": tshark_results,
        "strings": strings_results
    }
```

---

## Installation

```bash
# Install required tools on Kali Linux
sudo apt-get install -y volatility3 binwalk wireshark-common foremost

# Or individual tools
sudo apt-get install -y tshark foremost binutils
```

### Environment Variables

```bash
# Server Configuration
FORENSIC_SERVER_PORT=5004
DEFAULT_TIMEOUT=30
```

### Starting the Server

```bash
python -m src.mcp_servers.forensic_server
```

---

## Testing

```bash
# Run all tests (56 tests)
pytest tests/test_forensic_server.py -v

# Security tests only
pytest tests/test_forensic_server.py -m security -v

# Coverage report
pytest tests/test_forensic_server.py \
    --cov=src.mcp_servers.forensic_server \
    --cov-report=term-missing
```

---

## Security Considerations

### Path Validation
- All file paths must be absolute (no relative paths accepted)
- File existence verified before processing
- Directory vs file type checked
- No directory traversal attempts (`../`, `../../`)

### Timeout Protection
- Volatility: 10 minutes
- Binwalk: 5 minutes
- TShark: 2.5 minutes
- Foremost: 15 minutes (for large disk images)
- Strings: 1 minute

### Subprocess Security
- **Never uses `shell=True`**
- All commands built as arrays: `["tool", "arg1", "arg2"]`
- Proper exception handling for all subprocess calls

---

## Legal Notice

⚠️ Digital forensics tools must be used responsibly:
- Obtain proper authorization before analyzing systems/files
- Follow chain of custody procedures
- Maintain evidence integrity
- Comply with applicable laws (ECPA, CFAA, local regulations)
- Document all forensic activities

---

**Last Updated**: 2024-11-13
**Version**: 1.0.0
**Maintainer**: Kali Agents Development Team
