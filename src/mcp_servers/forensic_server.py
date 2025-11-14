"""
Forensic Agent MCP Server - "Digital Forensics at Your Service"

This server provides digital forensics and malware analysis tools for the Kali Agents system.
It exposes volatility, binwalk, tshark, foremost, and strings as MCP tools.

⚠️ AUTHORIZED USE ONLY ⚠️
These forensic tools must only be used on systems and files you own or have explicit permission to analyze.
"""

import subprocess
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio
import tempfile

from fastmcp import FastMCP, Context
from src.config.settings import NETWORK_CONFIG


# Create the MCP server instance
mcp = FastMCP("ForensicAgent")


@mcp.tool
async def volatility_analyze(
    memory_dump: str,
    profile: Optional[str] = None,
    plugins: Optional[List[str]] = None,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Analyze memory dumps using Volatility 3.

    ⚠️ AUTHORIZED FORENSICS ONLY

    Args:
        memory_dump: Path to memory dump file (must exist and be readable)
        profile: OS profile (auto-detected in Volatility 3 if not specified)
        plugins: List of plugins to run (e.g., ["pslist", "netscan", "filescan"])
                 Default: ["windows.pslist", "windows.netscan"]

    Returns:
        Dictionary containing analysis results from each plugin

    Security:
        - Path validation prevents directory traversal
        - File existence checked before analysis
        - No shell=True in subprocess
        - Timeout enforced to prevent DoS
    """
    if ctx:
        await ctx.info(f"🔍 Starting Volatility analysis on {memory_dump}")

    # Security: Validate file path exists and is absolute
    dump_path = Path(memory_dump)
    if not dump_path.is_absolute():
        return {
            "status": "failed",
            "error": "Memory dump path must be absolute",
            "dump": memory_dump
        }

    if not dump_path.exists():
        return {
            "status": "failed",
            "error": f"Memory dump file not found: {memory_dump}",
            "dump": memory_dump
        }

    if not dump_path.is_file():
        return {
            "status": "failed",
            "error": "Path must be a file, not a directory",
            "dump": memory_dump
        }

    # Default plugins if none specified
    if plugins is None:
        plugins = ["windows.pslist", "windows.netscan"]

    # Check if volatility3 is available
    vol3_path = "/usr/bin/vol3"
    if not Path(vol3_path).exists():
        # Try alternate locations
        vol3_path = "/usr/local/bin/vol3"
        if not Path(vol3_path).exists():
            return {
                "status": "failed",
                "error": "volatility3 not found. Install with: pip install volatility3",
                "dump": memory_dump
            }

    results = {
        "status": "completed",
        "dump": str(dump_path),
        "profile": profile or "auto-detected",
        "plugins": {}
    }

    # Run each plugin
    for plugin in plugins:
        if ctx:
            await ctx.info(f"🔧 Running plugin: {plugin}")

        # Build volatility command (subprocess array, not string)
        vol_cmd = [vol3_path, "-f", str(dump_path), plugin]

        # Add profile if specified
        if profile:
            vol_cmd.extend(["--profile", profile])

        try:
            result = subprocess.run(
                vol_cmd,
                capture_output=True,
                text=True,
                timeout=NETWORK_CONFIG["default_timeout"] * 20  # 10 minutes for forensics
            )

            # Parse volatility output
            plugin_results = _parse_volatility_output(result.stdout, plugin)
            results["plugins"][plugin] = plugin_results

        except subprocess.TimeoutExpired:
            results["plugins"][plugin] = {
                "status": "timeout",
                "error": f"Plugin {plugin} exceeded timeout"
            }
        except Exception as e:
            results["plugins"][plugin] = {
                "status": "failed",
                "error": str(e)
            }

    if ctx:
        completed_count = sum(1 for p in results["plugins"].values() if p.get("status") == "completed")
        await ctx.info(f"✅ Analysis completed! {completed_count}/{len(plugins)} plugins succeeded")

    return results


@mcp.tool
async def binwalk_analyze(
    firmware_file: str,
    extract: bool = False,
    signature: bool = True,
    entropy: bool = False,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Analyze firmware and binary files using binwalk.

    Args:
        firmware_file: Path to firmware/binary file to analyze
        extract: Extract discovered filesystems and files
        signature: Perform signature scan (default: True)
        entropy: Calculate entropy analysis

    Returns:
        Dictionary containing discovered signatures, filesystems, and extracted files
    """
    if ctx:
        await ctx.info(f"🔍 Starting binwalk analysis on {firmware_file}")

    # Security: Validate file path
    file_path = Path(firmware_file)
    if not file_path.is_absolute():
        return {
            "status": "failed",
            "error": "Firmware file path must be absolute",
            "file": firmware_file
        }

    if not file_path.exists():
        return {
            "status": "failed",
            "error": f"Firmware file not found: {firmware_file}",
            "file": firmware_file
        }

    # Check if binwalk is available
    binwalk_path = "/usr/bin/binwalk"
    if not Path(binwalk_path).exists():
        return {
            "status": "failed",
            "error": "binwalk not found. Install with: apt-get install binwalk",
            "file": firmware_file
        }

    # Build binwalk command (subprocess array)
    binwalk_cmd = [binwalk_path]

    if extract:
        binwalk_cmd.append("-e")  # Extract
    if signature:
        binwalk_cmd.append("-B")  # Signature scan
    if entropy:
        binwalk_cmd.append("-E")  # Entropy analysis

    binwalk_cmd.append(str(file_path))

    try:
        if ctx:
            await ctx.info(f"🔧 Executing binwalk analysis")

        result = subprocess.run(
            binwalk_cmd,
            capture_output=True,
            text=True,
            timeout=NETWORK_CONFIG["default_timeout"] * 10  # 5 minutes
        )

        # Parse binwalk output
        scan_results = _parse_binwalk_output(result.stdout, file_path)
        scan_results["file"] = str(file_path)
        scan_results["options"] = {
            "extract": extract,
            "signature": signature,
            "entropy": entropy
        }

        if ctx:
            sig_count = len(scan_results.get("signatures", []))
            await ctx.info(f"✅ Binwalk analysis completed! Found {sig_count} signatures")

        return scan_results

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "error": "Binwalk analysis exceeded timeout",
            "file": firmware_file
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Binwalk analysis error: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "file": firmware_file
        }


@mcp.tool
async def tshark_analyze(
    pcap_file: str,
    display_filter: Optional[str] = None,
    read_filter: Optional[str] = None,
    fields: Optional[List[str]] = None,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Analyze network traffic using tshark (Wireshark CLI).

    Args:
        pcap_file: Path to pcap/pcapng file
        display_filter: Display filter (e.g., "http", "tcp.port == 80")
        read_filter: Read filter to apply during capture reading
        fields: Fields to extract (e.g., ["frame.time", "ip.src", "ip.dst"])

    Returns:
        Dictionary containing packet statistics and extracted data
    """
    if ctx:
        await ctx.info(f"🔍 Starting tshark analysis on {pcap_file}")

    # Security: Validate file path
    pcap_path = Path(pcap_file)
    if not pcap_path.is_absolute():
        return {
            "status": "failed",
            "error": "PCAP file path must be absolute",
            "file": pcap_file
        }

    if not pcap_path.exists():
        return {
            "status": "failed",
            "error": f"PCAP file not found: {pcap_file}",
            "file": pcap_file
        }

    # Check if tshark is available
    tshark_path = "/usr/bin/tshark"
    if not Path(tshark_path).exists():
        return {
            "status": "failed",
            "error": "tshark not found. Install with: apt-get install tshark",
            "file": pcap_file
        }

    # Build tshark command (subprocess array)
    tshark_cmd = [tshark_path, "-r", str(pcap_path), "-T", "json"]

    # Add display filter
    if display_filter:
        tshark_cmd.extend(["-Y", display_filter])

    # Add read filter
    if read_filter:
        tshark_cmd.extend(["-R", read_filter])

    # Add field extraction
    if fields:
        for field in fields:
            tshark_cmd.extend(["-e", field])

    try:
        if ctx:
            await ctx.info(f"🔧 Executing tshark analysis")

        result = subprocess.run(
            tshark_cmd,
            capture_output=True,
            text=True,
            timeout=NETWORK_CONFIG["default_timeout"] * 5  # 2.5 minutes
        )

        # Parse tshark JSON output
        scan_results = _parse_tshark_output(result.stdout)
        scan_results["file"] = str(pcap_path)
        scan_results["filters"] = {
            "display_filter": display_filter,
            "read_filter": read_filter
        }

        if ctx:
            packet_count = scan_results.get("packet_count", 0)
            await ctx.info(f"✅ Tshark analysis completed! Analyzed {packet_count} packets")

        return scan_results

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "error": "Tshark analysis exceeded timeout",
            "file": pcap_file
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Tshark analysis error: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "file": pcap_file
        }


@mcp.tool
async def foremost_carve(
    image_file: str,
    output_dir: Optional[str] = None,
    file_types: Optional[List[str]] = None,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Carve files from disk images using foremost.

    Args:
        image_file: Path to disk image file
        output_dir: Output directory for carved files (default: temp directory)
        file_types: File types to carve (e.g., ["jpg", "pdf", "doc"])
                    Default: all supported types

    Returns:
        Dictionary containing carved file statistics and locations
    """
    if ctx:
        await ctx.info(f"🔍 Starting foremost file carving on {image_file}")

    # Security: Validate file path
    image_path = Path(image_file)
    if not image_path.is_absolute():
        return {
            "status": "failed",
            "error": "Image file path must be absolute",
            "file": image_file
        }

    if not image_path.exists():
        return {
            "status": "failed",
            "error": f"Image file not found: {image_file}",
            "file": image_file
        }

    # Check if foremost is available
    foremost_path = "/usr/bin/foremost"
    if not Path(foremost_path).exists():
        return {
            "status": "failed",
            "error": "foremost not found. Install with: apt-get install foremost",
            "file": image_file
        }

    # Create output directory if not specified
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="foremost_")
    else:
        # Security: Validate output directory path
        output_path = Path(output_dir)
        if not output_path.is_absolute():
            return {
                "status": "failed",
                "error": "Output directory path must be absolute",
                "file": image_file
            }
        output_path.mkdir(parents=True, exist_ok=True)

    # Build foremost command (subprocess array)
    foremost_cmd = [foremost_path, "-i", str(image_path), "-o", output_dir]

    # Add file type filters
    if file_types:
        foremost_cmd.extend(["-t", ",".join(file_types)])

    try:
        if ctx:
            await ctx.info(f"🔧 Executing foremost file carving to {output_dir}")

        result = subprocess.run(
            foremost_cmd,
            capture_output=True,
            text=True,
            timeout=NETWORK_CONFIG["default_timeout"] * 30  # 15 minutes for large images
        )

        # Parse foremost output
        scan_results = _parse_foremost_output(output_dir)
        scan_results["image"] = str(image_path)
        scan_results["output_dir"] = output_dir
        scan_results["file_types"] = file_types or "all"

        if ctx:
            total_carved = scan_results.get("total_carved", 0)
            await ctx.info(f"✅ File carving completed! Recovered {total_carved} files")

        return scan_results

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "error": "Foremost carving exceeded timeout",
            "file": image_file,
            "output_dir": output_dir
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Foremost carving error: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "file": image_file
        }


@mcp.tool
async def strings_extract(
    file_path: str,
    min_length: int = 4,
    encoding: str = "ascii",
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Extract printable strings from binary files.

    Args:
        file_path: Path to file to analyze
        min_length: Minimum string length (default: 4)
        encoding: String encoding (ascii, unicode, utf-8)

    Returns:
        Dictionary containing extracted strings and statistics
    """
    if ctx:
        await ctx.info(f"🔍 Extracting strings from {file_path}")

    # Security: Validate file path
    target_path = Path(file_path)
    if not target_path.is_absolute():
        return {
            "status": "failed",
            "error": "File path must be absolute",
            "file": file_path
        }

    if not target_path.exists():
        return {
            "status": "failed",
            "error": f"File not found: {file_path}",
            "file": file_path
        }

    # Validate min_length
    if not (1 <= min_length <= 100):
        return {
            "status": "failed",
            "error": "Minimum length must be between 1-100",
            "file": file_path
        }

    # Validate encoding
    allowed_encodings = ["ascii", "unicode", "utf-8", "s", "S"]
    if encoding not in allowed_encodings:
        return {
            "status": "failed",
            "error": f"Invalid encoding. Allowed: {allowed_encodings}",
            "file": file_path
        }

    # Check if strings is available
    strings_path = "/usr/bin/strings"
    if not Path(strings_path).exists():
        return {
            "status": "failed",
            "error": "strings command not found",
            "file": file_path
        }

    # Build strings command (subprocess array)
    strings_cmd = [strings_path, "-n", str(min_length)]

    # Add encoding option
    if encoding == "unicode":
        strings_cmd.append("-e")
        strings_cmd.append("l")  # little-endian
    elif encoding == "utf-8":
        strings_cmd.append("-e")
        strings_cmd.append("S")

    strings_cmd.append(str(target_path))

    try:
        if ctx:
            await ctx.info(f"🔧 Extracting strings (min_length={min_length})")

        result = subprocess.run(
            strings_cmd,
            capture_output=True,
            text=True,
            timeout=NETWORK_CONFIG["default_timeout"] * 2  # 1 minute
        )

        # Parse strings output
        extracted_strings = result.stdout.strip().split("\n")
        # Filter empty strings
        extracted_strings = [s for s in extracted_strings if s.strip()]

        # Analyze strings for interesting patterns
        analysis = _analyze_strings(extracted_strings)

        return {
            "status": "completed",
            "file": str(target_path),
            "total_strings": len(extracted_strings),
            "min_length": min_length,
            "encoding": encoding,
            "strings": extracted_strings[:1000],  # Limit to first 1000
            "truncated": len(extracted_strings) > 1000,
            "analysis": analysis
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "error": "String extraction exceeded timeout",
            "file": file_path
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"❌ String extraction error: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "file": file_path
        }


# Output Parser Functions

def _parse_volatility_output(stdout: str, plugin: str) -> Dict[str, Any]:
    """Parse volatility plugin output."""
    result = {
        "status": "completed",
        "plugin": plugin,
        "data": []
    }

    lines = stdout.strip().split("\n")

    # Different plugins have different output formats
    if "pslist" in plugin.lower():
        # Parse process list
        for line in lines:
            if line.strip() and not line.startswith("Volatility"):
                # Simple parsing - real implementation would be more sophisticated
                parts = line.split()
                if len(parts) >= 4:
                    result["data"].append({
                        "type": "process",
                        "raw": line.strip()
                    })

    elif "netscan" in plugin.lower():
        # Parse network connections
        for line in lines:
            if line.strip() and not line.startswith("Volatility"):
                result["data"].append({
                    "type": "network",
                    "raw": line.strip()
                })
    else:
        # Generic parsing
        for line in lines:
            if line.strip() and not line.startswith("Volatility"):
                result["data"].append({"raw": line.strip()})

    return result


def _parse_binwalk_output(stdout: str, file_path: Path) -> Dict[str, Any]:
    """Parse binwalk signature scan output."""
    result = {
        "status": "completed",
        "signatures": []
    }

    lines = stdout.strip().split("\n")

    for line in lines:
        # Binwalk format: OFFSET    DESCRIPTION
        # Example: 0             Squashfs filesystem, little endian
        match = re.match(r"^(\d+)\s+(.+)$", line.strip())
        if match:
            offset = int(match.group(1))
            description = match.group(2).strip()

            result["signatures"].append({
                "offset": offset,
                "offset_hex": hex(offset),
                "description": description
            })

    return result


def _parse_tshark_output(stdout: str) -> Dict[str, Any]:
    """Parse tshark JSON output."""
    result = {
        "status": "completed",
        "packets": [],
        "packet_count": 0,
        "protocols": {}
    }

    if not stdout.strip():
        return result

    try:
        # Tshark outputs JSON array of packets
        packets = json.loads(stdout)

        result["packet_count"] = len(packets)
        result["packets"] = packets[:100]  # Limit to first 100 packets
        result["truncated"] = len(packets) > 100

        # Count protocols
        for packet in packets:
            if "_source" in packet and "layers" in packet["_source"]:
                layers = packet["_source"]["layers"]
                for protocol in layers.keys():
                    result["protocols"][protocol] = result["protocols"].get(protocol, 0) + 1

    except json.JSONDecodeError:
        result["status"] = "parse_error"
        result["error"] = "Failed to parse tshark JSON output"

    return result


def _parse_foremost_output(output_dir: str) -> Dict[str, Any]:
    """Parse foremost results from output directory."""
    result = {
        "status": "completed",
        "carved_files": {},
        "total_carved": 0
    }

    output_path = Path(output_dir)

    # Read foremost audit file
    audit_file = output_path / "audit.txt"
    if audit_file.exists():
        with open(audit_file, "r") as f:
            audit_content = f.read()
            result["audit"] = audit_content

    # Count carved files by type
    for item in output_path.iterdir():
        if item.is_dir():
            file_type = item.name
            file_count = len(list(item.glob("*")))
            result["carved_files"][file_type] = file_count
            result["total_carved"] += file_count

    return result


def _analyze_strings(strings_list: List[str]) -> Dict[str, Any]:
    """Analyze extracted strings for interesting patterns."""
    analysis = {
        "urls": [],
        "emails": [],
        "ip_addresses": [],
        "file_paths": [],
        "interesting_keywords": []
    }

    # Regex patterns
    url_pattern = re.compile(r"https?://[^\s]+")
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    ip_pattern = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    path_pattern = re.compile(r"[A-Za-z]:\\[\\\w\s\-.]+|/[\w/\-\.]+")

    # Interesting keywords
    keywords = ["password", "secret", "api_key", "token", "auth", "admin", "root", "key"]

    for string in strings_list:
        # URLs
        if url_pattern.search(string):
            analysis["urls"].append(string)

        # Emails
        if email_pattern.search(string):
            analysis["emails"].append(string)

        # IP addresses
        if ip_pattern.search(string):
            analysis["ip_addresses"].append(string)

        # File paths
        if path_pattern.search(string):
            analysis["file_paths"].append(string)

        # Keywords
        for keyword in keywords:
            if keyword.lower() in string.lower():
                analysis["interesting_keywords"].append(string)
                break

    # Limit results
    for key in analysis:
        if isinstance(analysis[key], list):
            analysis[key] = list(set(analysis[key]))[:50]  # Dedupe and limit

    return analysis


# Health check endpoint
@mcp.tool
async def health_check(ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Check forensic server health and tool availability."""
    tools_status = {}

    # Check volatility
    tools_status["volatility3"] = (
        Path("/usr/bin/vol3").exists() or
        Path("/usr/local/bin/vol3").exists()
    )

    # Check binwalk
    tools_status["binwalk"] = Path("/usr/bin/binwalk").exists()

    # Check tshark
    tools_status["tshark"] = Path("/usr/bin/tshark").exists()

    # Check foremost
    tools_status["foremost"] = Path("/usr/bin/foremost").exists()

    # Check strings
    tools_status["strings"] = Path("/usr/bin/strings").exists()

    all_available = all(tools_status.values())

    return {
        "status": "healthy" if all_available else "degraded",
        "tools": tools_status,
        "server": "ForensicAgent",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
