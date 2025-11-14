"""
Social Agent MCP Server - "Social Engineering & OSINT at Your Service"

This server provides OSINT (Open Source Intelligence) gathering and reconnaissance
tools for the Kali Agents system. It exposes theHarvester, Shodan, recon-ng,
and SpiderFoot as MCP tools.

⚠️ AUTHORIZED USE ONLY ⚠️
OSINT tools must be used responsibly and ethically. Respect privacy laws and
obtain proper authorization before gathering intelligence on individuals or organizations.
"""

import subprocess
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio

from fastmcp import FastMCP, Context
from src.config.settings import NETWORK_CONFIG, OSINT_CONFIG


# Create the MCP server instance
mcp = FastMCP("SocialAgent")


@mcp.tool
async def theharvester_search(
    domain: str,
    sources: Optional[List[str]] = None,
    limit: int = 500,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Perform OSINT gathering using theHarvester.

    ⚠️ ETHICAL USE ONLY - Respect privacy and applicable laws

    Args:
        domain: Target domain to investigate (e.g., "example.com")
        sources: Data sources to use (e.g., ["google", "bing", "linkedin"])
                 Default: ["google", "bing", "yahoo"]
        limit: Maximum results per source (default: 500)

    Returns:
        Dictionary containing emails, hosts, IPs, and URLs discovered

    Security:
        - Domain validation prevents command injection
        - Source whitelist enforced
        - No shell=True in subprocess
    """
    if ctx:
        await ctx.info(f"🔍 Starting theHarvester search for domain: {domain}")

    # Security: Validate domain format (basic validation)
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-\.]+[a-zA-Z0-9]$', domain):
        return {
            "status": "failed",
            "error": "Invalid domain format",
            "domain": domain
        }

    # Security: No special characters that could enable injection
    if any(char in domain for char in [";", "|", "&", "`", "$", "(", ")", " "]):
        return {
            "status": "failed",
            "error": "Invalid characters in domain",
            "domain": domain
        }

    # Validate limit
    if not (1 <= limit <= 10000):
        return {
            "status": "failed",
            "error": "Limit must be between 1-10000",
            "domain": domain
        }

    # Default sources
    if sources is None:
        sources = ["google", "bing", "yahoo"]

    # Security: Whitelist allowed sources
    allowed_sources = [
        "baidu", "bing", "bingapi", "certspotter", "crtsh", "dnsdumpster",
        "duckduckgo", "github", "google", "hunter", "intelx", "linkedin",
        "otx", "securityTrails", "threatcrowd", "trello", "twitter",
        "vhost", "virustotal", "yahoo"
    ]

    # Validate sources
    for source in sources:
        if source not in allowed_sources:
            return {
                "status": "failed",
                "error": f"Invalid source: {source}. Allowed: {allowed_sources}",
                "domain": domain
            }

    # Check if theHarvester is available
    harvester_path = "/usr/bin/theHarvester"
    if not Path(harvester_path).exists():
        # Try alternate location
        harvester_path = "/usr/local/bin/theHarvester"
        if not Path(harvester_path).exists():
            return {
                "status": "failed",
                "error": "theHarvester not found. Install with: apt-get install theharvester",
                "domain": domain
            }

    results = {
        "status": "completed",
        "domain": domain,
        "emails": [],
        "hosts": [],
        "ips": [],
        "urls": [],
        "sources_used": sources
    }

    # Run theHarvester for each source
    for source in sources:
        if ctx:
            await ctx.info(f"🔧 Querying source: {source}")

        # Build theHarvester command (subprocess array, not string)
        harvester_cmd = [
            harvester_path,
            "-d", domain,
            "-b", source,
            "-l", str(limit)
        ]

        try:
            result = subprocess.run(
                harvester_cmd,
                capture_output=True,
                text=True,
                timeout=NETWORK_CONFIG["default_timeout"] * 5  # 2.5 minutes per source
            )

            # Parse theHarvester output
            source_results = _parse_harvester_output(result.stdout)

            # Aggregate results
            results["emails"].extend(source_results.get("emails", []))
            results["hosts"].extend(source_results.get("hosts", []))
            results["ips"].extend(source_results.get("ips", []))
            results["urls"].extend(source_results.get("urls", []))

        except subprocess.TimeoutExpired:
            if ctx:
                await ctx.error(f"⏰ Timeout for source: {source}")
        except Exception as e:
            if ctx:
                await ctx.error(f"❌ Error with source {source}: {str(e)}")

    # Deduplicate results
    results["emails"] = list(set(results["emails"]))
    results["hosts"] = list(set(results["hosts"]))
    results["ips"] = list(set(results["ips"]))
    results["urls"] = list(set(results["urls"]))

    # Count totals
    results["total_emails"] = len(results["emails"])
    results["total_hosts"] = len(results["hosts"])
    results["total_ips"] = len(results["ips"])
    results["total_urls"] = len(results["urls"])

    if ctx:
        await ctx.info(f"✅ Search completed! Found {results['total_emails']} emails, "
                      f"{results['total_hosts']} hosts, {results['total_ips']} IPs")

    return results


@mcp.tool
async def shodan_search(
    query: str,
    limit: int = 100,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Search Shodan for Internet-connected devices.

    Requires: SHODAN_API_KEY in environment

    Args:
        query: Shodan search query (e.g., "apache", "port:22 country:US")
        limit: Maximum results to return (default: 100, max: 1000)

    Returns:
        Dictionary containing search results with IP, port, banner information
    """
    if ctx:
        await ctx.info(f"🔍 Searching Shodan for: {query}")

    # Check if Shodan API key is configured
    api_key = OSINT_CONFIG.get("shodan_api_key")
    if not api_key or api_key == "CHANGE_ME":
        return {
            "status": "failed",
            "error": "Shodan API key not configured. Set SHODAN_API_KEY in .env",
            "query": query
        }

    # Validate limit
    if not (1 <= limit <= 1000):
        return {
            "status": "failed",
            "error": "Limit must be between 1-1000",
            "query": query
        }

    try:
        # Use shodan CLI if available, otherwise use Python API
        shodan_path = "/usr/bin/shodan"

        if Path(shodan_path).exists():
            # Use Shodan CLI
            shodan_cmd = [
                shodan_path,
                "search",
                "--fields", "ip_str,port,org,data",
                "--limit", str(limit),
                query
            ]

            result = subprocess.run(
                shodan_cmd,
                capture_output=True,
                text=True,
                timeout=60,
                env={"SHODAN_API_KEY": api_key}
            )

            # Parse Shodan CLI output
            search_results = _parse_shodan_cli_output(result.stdout)

        else:
            # Use Python shodan library
            try:
                import shodan
                api = shodan.Shodan(api_key)
                results = api.search(query, limit=limit)

                search_results = {
                    "status": "completed",
                    "query": query,
                    "total": results.get("total", 0),
                    "results": [
                        {
                            "ip": r.get("ip_str"),
                            "port": r.get("port"),
                            "organization": r.get("org", ""),
                            "banner": r.get("data", "")[:200],  # Limit banner size
                            "hostnames": r.get("hostnames", []),
                            "location": {
                                "country": r.get("location", {}).get("country_name"),
                                "city": r.get("location", {}).get("city")
                            }
                        }
                        for r in results.get("matches", [])
                    ]
                }
            except ImportError:
                return {
                    "status": "failed",
                    "error": "Shodan library not installed. Install with: pip install shodan",
                    "query": query
                }

        search_results["limit"] = limit

        if ctx:
            result_count = len(search_results.get("results", []))
            await ctx.info(f"✅ Shodan search completed! Found {result_count} results")

        return search_results

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "error": "Shodan search exceeded timeout",
            "query": query
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Shodan search error: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "query": query
        }


@mcp.tool
async def shodan_host(
    ip: str,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific IP from Shodan.

    Args:
        ip: IP address to lookup (e.g., "8.8.8.8")

    Returns:
        Dictionary containing detailed host information, open ports, services
    """
    if ctx:
        await ctx.info(f"🔍 Looking up Shodan info for IP: {ip}")

    # Validate IP address format
    import ipaddress
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return {
            "status": "failed",
            "error": "Invalid IP address format",
            "ip": ip
        }

    # Check API key
    api_key = OSINT_CONFIG.get("shodan_api_key")
    if not api_key or api_key == "CHANGE_ME":
        return {
            "status": "failed",
            "error": "Shodan API key not configured",
            "ip": ip
        }

    try:
        import shodan
        api = shodan.Shodan(api_key)
        host_info = api.host(ip)

        result = {
            "status": "completed",
            "ip": ip,
            "organization": host_info.get("org", ""),
            "operating_system": host_info.get("os"),
            "ports": host_info.get("ports", []),
            "hostnames": host_info.get("hostnames", []),
            "location": {
                "country": host_info.get("country_name"),
                "city": host_info.get("city"),
                "region": host_info.get("region_code")
            },
            "services": [
                {
                    "port": service.get("port"),
                    "protocol": service.get("transport"),
                    "service": service.get("product"),
                    "version": service.get("version")
                }
                for service in host_info.get("data", [])
            ],
            "tags": host_info.get("tags", []),
            "vulns": host_info.get("vulns", [])
        }

        if ctx:
            port_count = len(result["ports"])
            await ctx.info(f"✅ Host lookup completed! Found {port_count} open ports")

        return result

    except ImportError:
        return {
            "status": "failed",
            "error": "Shodan library not installed",
            "ip": ip
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Shodan host lookup error: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "ip": ip
        }


@mcp.tool
async def reconng_search(
    domain: str,
    modules: Optional[List[str]] = None,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Perform reconnaissance using recon-ng framework.

    Args:
        domain: Target domain to investigate
        modules: Recon-ng modules to run (default: basic OSINT modules)

    Returns:
        Dictionary containing reconnaissance results
    """
    if ctx:
        await ctx.info(f"🔍 Starting recon-ng search for: {domain}")

    # Validate domain
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-\.]+[a-zA-Z0-9]$', domain):
        return {
            "status": "failed",
            "error": "Invalid domain format",
            "domain": domain
        }

    # Check if recon-ng is available
    reconng_path = "/usr/bin/recon-ng"
    if not Path(reconng_path).exists():
        return {
            "status": "failed",
            "error": "recon-ng not found. Install with: apt-get install recon-ng",
            "domain": domain
        }

    # Default modules if none specified
    if modules is None:
        modules = [
            "recon/domains-hosts/google_site_web",
            "recon/domains-hosts/bing_domain_web",
            "recon/hosts-hosts/resolve"
        ]

    # Note: recon-ng requires interactive setup or pre-configured workspace
    # This is a simplified implementation
    return {
        "status": "not_implemented",
        "error": "recon-ng requires interactive setup and workspace configuration",
        "domain": domain,
        "note": "Use recon-ng CLI directly for full functionality"
    }


@mcp.tool
async def spiderfoot_scan(
    target: str,
    scan_type: str = "all",
    modules: Optional[List[str]] = None,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Perform OSINT automation using SpiderFoot.

    Args:
        target: Target to investigate (domain, IP, email, etc.)
        scan_type: Type of scan (all, passive, footprint)
        modules: Specific modules to use (optional)

    Returns:
        Dictionary containing OSINT findings from SpiderFoot
    """
    if ctx:
        await ctx.info(f"🔍 Starting SpiderFoot scan for: {target}")

    # Validate scan_type
    allowed_scan_types = ["all", "passive", "footprint"]
    if scan_type not in allowed_scan_types:
        return {
            "status": "failed",
            "error": f"Invalid scan_type. Allowed: {allowed_scan_types}",
            "target": target
        }

    # Check if SpiderFoot is available
    sf_path = "/usr/bin/spiderfoot"
    if not Path(sf_path).exists():
        # Try alternate location
        sf_path = "/opt/spiderfoot/sf.py"
        if not Path(sf_path).exists():
            return {
                "status": "failed",
                "error": "SpiderFoot not found. Install from: https://github.com/smicallef/spiderfoot",
                "target": target
            }

    # Note: SpiderFoot is typically used via web interface
    # CLI usage is limited
    return {
        "status": "not_implemented",
        "error": "SpiderFoot is best used via its web interface",
        "target": target,
        "note": "Start SpiderFoot web UI with: python sf.py -l 127.0.0.1:5001"
    }


# Output Parser Functions

def _parse_harvester_output(stdout: str) -> Dict[str, List[str]]:
    """Parse theHarvester output to extract emails, hosts, IPs, URLs."""
    result = {
        "emails": [],
        "hosts": [],
        "ips": [],
        "urls": []
    }

    lines = stdout.strip().split("\n")

    current_section = None
    for line in lines:
        line = line.strip()

        # Detect sections
        if "emails" in line.lower():
            current_section = "emails"
            continue
        elif "hosts" in line.lower():
            current_section = "hosts"
            continue
        elif "ips" in line.lower() or "addresses" in line.lower():
            current_section = "ips"
            continue
        elif "urls" in line.lower():
            current_section = "urls"
            continue

        # Skip headers and separators
        if not line or line.startswith("[") or line.startswith("-") or line.startswith("="):
            continue

        # Add to current section
        if current_section == "emails" and "@" in line:
            result["emails"].append(line)
        elif current_section == "hosts":
            result["hosts"].append(line)
        elif current_section == "ips":
            # Validate IP format
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', line):
                result["ips"].append(line)
        elif current_section == "urls" and ("http://" in line or "https://" in line):
            result["urls"].append(line)

    return result


def _parse_shodan_cli_output(stdout: str) -> Dict[str, Any]:
    """Parse Shodan CLI output."""
    result = {
        "status": "completed",
        "results": []
    }

    lines = stdout.strip().split("\n")

    for line in lines:
        # Shodan CLI format: IP:PORT ORG DATA
        parts = line.split("\t")
        if len(parts) >= 2:
            ip_port = parts[0].split(":")
            result["results"].append({
                "ip": ip_port[0] if len(ip_port) > 0 else "",
                "port": int(ip_port[1]) if len(ip_port) > 1 else 0,
                "organization": parts[1] if len(parts) > 1 else "",
                "banner": parts[2] if len(parts) > 2 else ""
            })

    return result


# Health check endpoint
@mcp.tool
async def health_check(ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Check social server health and tool availability."""
    tools_status = {}

    # Check theHarvester
    tools_status["theharvester"] = (
        Path("/usr/bin/theHarvester").exists() or
        Path("/usr/local/bin/theHarvester").exists()
    )

    # Check Shodan (library)
    try:
        import shodan
        tools_status["shodan"] = True
    except ImportError:
        tools_status["shodan"] = False

    # Check recon-ng
    tools_status["reconng"] = Path("/usr/bin/recon-ng").exists()

    # Check SpiderFoot
    tools_status["spiderfoot"] = (
        Path("/usr/bin/spiderfoot").exists() or
        Path("/opt/spiderfoot/sf.py").exists()
    )

    # Check API keys
    shodan_key = OSINT_CONFIG.get("shodan_api_key")
    tools_status["shodan_api_configured"] = shodan_key and shodan_key != "CHANGE_ME"

    all_available = all([
        tools_status["theharvester"],
        tools_status["shodan"]
    ])

    return {
        "status": "healthy" if all_available else "degraded",
        "tools": tools_status,
        "server": "SocialAgent",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
