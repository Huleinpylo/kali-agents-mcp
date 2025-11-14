"""
Network Agent MCP Server - "Network Recon at Your Service"

This server provides network reconnaissance tools for the Kali Agents system.
It exposes nmap, masscan, and other network discovery tools as MCP tools.
"""

import subprocess
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio
import ipaddress
import re

from fastmcp import FastMCP, Context
from src.config.settings import KALI_TOOLS, NETWORK_CONFIG


# Create the MCP server instance used for tool registration
_mcp_app = FastMCP("NetworkAgent")


@_mcp_app.tool
async def nmap_scan(
    target: str,
    scan_type: str = "stealth",
    ports: str = "top-1000",
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Perform network reconnaissance using nmap.
    
    Args:
        target: Target IP address, hostname, or CIDR range
        scan_type: Type of scan (stealth, connect, udp, version, aggressive)
        ports: Ports to scan (top-1000, all, specific range like 1-1000)
        
    Returns:
        Dictionary containing scan results, open ports, and service information
    """
    if ctx:
        await ctx.info(f"? Starting nmap scan on {target}")
    
    # Build nmap command based on scan type
    nmap_cmd = [KALI_TOOLS["nmap"]]
    
    # Add scan type options
    if scan_type == "stealth":
        nmap_cmd.extend(["-sS", "-sV"])
    elif scan_type == "connect":
        nmap_cmd.extend(["-sT", "-sV"])
    elif scan_type == "udp":
        nmap_cmd.extend(["-sU"])
    elif scan_type == "version":
        nmap_cmd.extend(["-sV", "-sC"])
    elif scan_type == "aggressive":
        nmap_cmd.extend(["-A"])
    else:
        nmap_cmd.extend(["-sS"])  # Default to stealth
    
    # Add port specification
    if ports == "top-1000":
        nmap_cmd.append("--top-ports=1000")
    elif ports == "all":
        nmap_cmd.extend(["-p", "1-65535"])
    elif "-" in ports or "," in ports:
        nmap_cmd.extend(["-p", ports])
    
    # Add output format and timing
    nmap_cmd.extend(["-oX", "-", "-T4", target])
    
    try:
        # Execute nmap command
        if ctx:
            await ctx.info(f"? Executing: {' '.join(nmap_cmd)}")
        
        result = subprocess.run(
            nmap_cmd,
            capture_output=True,
            text=True,
            timeout=NETWORK_CONFIG["default_timeout"] * 10  # Extended timeout for nmap
        )
        
        if result.returncode != 0:
            if ctx:
                await ctx.error(f"? nmap scan failed: {result.stderr}")
            return {
                "status": "failed",
                "error": result.stderr,
                "target": target
            }
        
        # Parse XML output
        scan_results = _parse_nmap_xml(result.stdout)
        scan_results["scan_type"] = scan_type
        scan_results["ports_scanned"] = ports
        
        if ctx:
            open_ports = len(scan_results.get("hosts", {}).get(target, {}).get("ports", []))
            await ctx.info(f"? Scan completed! Found {open_ports} open ports")
        
        return scan_results
        
    except subprocess.TimeoutExpired:
        if ctx:
            await ctx.error("? nmap scan timed out")
        return {
            "status": "timeout",
            "error": "Scan timed out",
            "target": target
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"? Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "target": target
        }


@_mcp_app.tool
async def masscan_ports(
    target: str,
    ports: str = "1-1000",
    rate: int = 1000,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Perform high-speed port scanning using masscan.
    
    Args:
        target: Target IP address or CIDR range
        ports: Port range to scan (e.g., "1-1000", "80,443,22")
        rate: Scan rate in packets per second
        
    Returns:
        Dictionary containing scan results and open ports
    """
    if ctx:
        await ctx.info(f"? Starting masscan on {target} (rate: {rate} pps)")
    
    masscan_cmd = [
        KALI_TOOLS["masscan"],
        target,
        "-p", ports,
        "--rate", str(rate),
        "--open-only",
        "--output-format", "json"
    ]
    
    try:
        if ctx:
            await ctx.info(f"? Executing: {' '.join(masscan_cmd)}")
        
        result = subprocess.run(
            masscan_cmd,
            capture_output=True,
            text=True,
            timeout=NETWORK_CONFIG["default_timeout"] * 5
        )
        
        if result.returncode != 0:
            if ctx:
                await ctx.error(f"? masscan failed: {result.stderr}")
            return {
                "status": "failed",
                "error": result.stderr,
                "target": target
            }
        
        # Parse masscan JSON output
        open_ports = []
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        port_data = json.loads(line)
                        open_ports.append(port_data)
                    except json.JSONDecodeError:
                        continue
        
        scan_results = {
            "status": "completed",
            "target": target,
            "ports_scanned": ports,
            "scan_rate": rate,
            "open_ports": open_ports,
            "total_open": len(open_ports)
        }
        
        if ctx:
            await ctx.info(f"? Masscan completed! Found {len(open_ports)} open ports")
        
        return scan_results
        
    except subprocess.TimeoutExpired:
        if ctx:
            await ctx.error("? masscan timed out")
        return {
            "status": "timeout",
            "error": "Scan timed out",
            "target": target
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"? Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "target": target
        }


@_mcp_app.tool
async def network_discovery(
    network: str,
    method: str = "ping",
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Discover live hosts on a network.
    
    Args:
        network: Network range to scan (e.g., "192.168.1.0/24")
        method: Discovery method (ping, arp)
        
    Returns:
        Dictionary containing discovered hosts
    """
    if ctx:
        await ctx.info(f"? Discovering hosts on {network} using {method}")
    
    if method == "ping":
        # Use nmap for ping discovery
        cmd = [KALI_TOOLS["nmap"], "-sn", network]
    elif method == "arp":
        # Use arp-scan if available, fallback to nmap
        cmd = ["arp-scan", network] if Path("/usr/bin/arp-scan").exists() else [KALI_TOOLS["nmap"], "-sn", network]
    else:
        cmd = [KALI_TOOLS["nmap"], "-sn", network]
    
    try:
        if ctx:
            await ctx.info(f"? Executing: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=NETWORK_CONFIG["default_timeout"]
        )
        
        if result.returncode != 0:
            if ctx:
                await ctx.error(f"? Network discovery failed: {result.stderr}")
            return {
                "status": "failed",
                "error": result.stderr,
                "network": network
            }
        
        # Parse output to extract live hosts
        live_hosts = _parse_discovery_output(result.stdout)
        
        discovery_results = {
            "status": "completed",
            "network": network,
            "method": method,
            "live_hosts": live_hosts,
            "total_hosts": len(live_hosts)
        }
        
        if ctx:
            await ctx.info(f"? Discovery completed! Found {len(live_hosts)} live hosts")
        
        return discovery_results
        
    except subprocess.TimeoutExpired:
        if ctx:
            await ctx.error("? Network discovery timed out")
        return {
            "status": "timeout",
            "error": "Discovery timed out",
            "network": network
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"? Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "network": network
        }


def _parse_nmap_xml(xml_output: str) -> Dict[str, Any]:
    """Parse nmap XML output and extract relevant information."""
    try:
        root = ET.fromstring(xml_output)
        results = {
            "status": "completed",
            "hosts": {}
        }
        
        for host in root.findall(".//host"):
            # Get host address
            address_elem = host.find(".//address[@addrtype='ipv4']")
            if address_elem is None:
                continue
            
            host_ip = address_elem.get("addr")
            host_info = {
                "status": "unknown",
                "ports": [],
                "os": None,
                "hostnames": []
            }
            
            # Get host status
            status_elem = host.find("status")
            if status_elem is not None:
                host_info["status"] = status_elem.get("state", "unknown")
            
            # Get hostnames
            for hostname in host.findall(".//hostname"):
                host_info["hostnames"].append({
                    "name": hostname.get("name"),
                    "type": hostname.get("type")
                })
            
            # Get open ports
            for port in host.findall(".//port"):
                state_elem = port.find("state")
                if state_elem is not None and state_elem.get("state") == "open":
                    port_info = {
                        "port": int(port.get("portid") or 0),
                        "protocol": port.get("protocol"),
                        "state": state_elem.get("state"),
                        "service": None,
                        "version": None
                    }
                    
                    # Get service information
                    service_elem = port.find("service")
                    if service_elem is not None:
                        port_info["service"] = service_elem.get("name")
                        port_info["version"] = service_elem.get("version")
                        port_info["product"] = service_elem.get("product")
                    
                    host_info["ports"].append(port_info)
            
            # Get OS information
            os_elem = host.find(".//osmatch")
            if os_elem is not None:
                host_info["os"] = {
                    "name": os_elem.get("name"),
                    "accuracy": os_elem.get("accuracy")
                }
            
            results["hosts"][host_ip] = host_info
        
        return results
        
    except ET.ParseError:
        return {
            "status": "parse_error",
            "error": "Failed to parse nmap XML output"
        }


def _parse_discovery_output(output: str) -> List[Dict[str, str]]:
    """Parse network discovery output to extract live hosts."""
    hosts = []
    lines = output.split('\n')
    
    for line in lines:
        line = line.strip()
        if "Nmap scan report for" in line:
            # Extract IP address
            if "(" in line and ")" in line:
                # Format: Nmap scan report for hostname (192.168.1.1)
                ip = line.split("(")[1].split(")")[0]
                hostname = line.split("for ")[1].split(" (")[0]
            else:
                # Format: Nmap scan report for 192.168.1.1
                ip = line.split("for ")[1]
                hostname = ip
            
            hosts.append({
                "ip": ip,
                "hostname": hostname,
                "status": "up"
            })
    
    return hosts


class NetworkServer:
    """Lightweight wrapper that mirrors the MCP network tools for direct invocation."""

    def __init__(self, app: Optional[FastMCP] = None):
        self.app = app or _mcp_app
        self.tools = getattr(self.app, "tools", {})

    def _validate_ip(self, value: str) -> bool:
        """Validate IPv4/IPv6 addresses."""
        try:
            ipaddress.ip_network(value, strict=False)
            return True
        except ValueError:
            return False

    def _validate_port_range(self, value: str) -> bool:
        """Validate common port specifications (80, 1-1000, 80,443)."""
        if not value:
            return False
        segments = [segment.strip() for segment in value.split(",") if segment.strip()]
        if not segments:
            return False
        for segment in segments:
            if "-" in segment:
                try:
                    start, end = segment.split("-", 1)
                    start_port = int(start)
                    end_port = int(end)
                except ValueError:
                    return False
                if start_port < 1 or end_port > 65535 or start_port > end_port:
                    return False
            else:
                try:
                    port = int(segment)
                except ValueError:
                    return False
                if port < 1 or port > 65535:
                    return False
        return True

    def _sanitize_target(self, target: str) -> str:
        """Remove shell metacharacters to guard subprocess executions."""
        return re.sub(r"[^A-Za-z0-9._:/-]", "", target)

    async def _execute_nmap_scan(
        self,
        target: str,
        ports: str = "top-1000",
        scan_type: str = "stealth",
        ctx: Optional[Context] = None,
    ) -> Dict[str, Any]:
        return await nmap_scan(target=target, scan_type=scan_type, ports=ports, ctx=ctx)

    async def _execute_network_discovery(
        self,
        network: str,
        ports: str = "top-1000",
        ctx: Optional[Context] = None,
    ) -> Dict[str, Any]:
        return await self._execute_nmap_scan(network, ports=ports, ctx=ctx)

    async def _execute_port_scan(
        self,
        target: str,
        ports: str,
        protocol: str = "tcp",
        ctx: Optional[Context] = None,
    ) -> Dict[str, Any]:
        scan_type = "udp" if protocol.lower() == "udp" else "stealth"
        return await self._execute_nmap_scan(target, ports=ports, scan_type=scan_type, ctx=ctx)

    async def _execute_masscan(
        self,
        target: str,
        ports: str = "1-1000",
        rate: int = 1000,
        ctx: Optional[Context] = None,
    ) -> Dict[str, Any]:
        return await masscan_ports(target=target, ports=ports, rate=rate, ctx=ctx)

    async def _execute_os_detection(self, target: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
        return await self._execute_nmap_scan(target, scan_type="aggressive", ctx=ctx)

    async def _execute_service_detection(
        self,
        target: str,
        ports: str = "top-1000",
        ctx: Optional[Context] = None,
    ) -> Dict[str, Any]:
        return await self._execute_nmap_scan(target, ports=ports, scan_type="version", ctx=ctx)

    async def _execute_zmap(
        self,
        target: str,
        ports: str = "1-1000",
        rate: int = 1000,
        ctx: Optional[Context] = None,
    ) -> Dict[str, Any]:
        return self._not_implemented("zmap_scan", target=target, ports=ports, rate=rate)

    async def _execute_arp_scan(self, network: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
        return self._not_implemented("arp_scan", network=network)

    async def _execute_netdiscover(self, network: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
        return self._not_implemented("netdiscover", network=network)

    @staticmethod
    def _not_implemented(tool: str, **extra: Any) -> Dict[str, Any]:
        return {"status": "not_implemented", "tool": tool, **extra}


# Export the class under the historical `mcp` name so tests importing
# `mcp as NetworkServer` continue to receive a usable type, while the actual
# FastMCP instance remains available as `_mcp_app`.
mcp = NetworkServer
network_mcp_app = _mcp_app


__all__ = ["NetworkServer", "mcp", "network_mcp_app", "nmap_scan", "masscan_ports", "network_discovery"]


if __name__ == "__main__":
    # Run the MCP server
    network_mcp_app.run()
