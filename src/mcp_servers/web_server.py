"""
Web Agent MCP Server - "Web Hacking at Your Service"

This server provides web application testing tools for the Kali Agents system.
It exposes gobuster, nikto, sqlmap, and other web security tools as MCP tools.
"""

import subprocess
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio
from urllib.parse import urlparse

from fastmcp import FastMCP, Context
from src.config.settings import KALI_TOOLS, WORDLISTS, NETWORK_CONFIG


# Create the MCP server instance
mcp = FastMCP("WebAgent")


@mcp.tool
async def gobuster_directory(
    url: str,
    wordlist: str = "common",
    extensions: str = "php,html,txt,js,css",
    threads: int = 10,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Perform directory and file enumeration using gobuster.
    
    Args:
        url: Target URL to scan
        wordlist: Wordlist to use (common, big, or custom path)
        extensions: File extensions to search for
        threads: Number of concurrent threads
        
    Returns:
        Dictionary containing discovered directories and files
    """
    if ctx:
        await ctx.info(f"? Starting directory enumeration on {url}")
    
    # Select wordlist
    if wordlist == "common":
        wordlist_path = WORDLISTS["common"]
    elif wordlist == "big":
        wordlist_path = WORDLISTS["big"]
    else:
        wordlist_path = wordlist  # Custom path
    
    # Validate wordlist exists
    if not Path(wordlist_path).exists():
        if ctx:
            await ctx.error(f"? Wordlist not found: {wordlist_path}")
        return {
            "status": "failed",
            "error": f"Wordlist not found: {wordlist_path}",
            "url": url
        }
    
    gobuster_cmd = [
        KALI_TOOLS["gobuster"],
        "dir",
        "-u", url,
        "-w", wordlist_path,
        "-x", extensions,
        "-t", str(threads),
        "-q",  # Quiet mode
        "--no-error"
    ]
    
    try:
        if ctx:
            await ctx.info(f"? Executing: gobuster with {wordlist} wordlist")
        
        result = subprocess.run(
            gobuster_cmd,
            capture_output=True,
            text=True,
            timeout=NETWORK_CONFIG["default_timeout"] * 10
        )
        
        # Parse gobuster output
        discovered_paths = _parse_gobuster_output(result.stdout)
        
        scan_results = {
            "status": "completed",
            "url": url,
            "wordlist_used": wordlist_path,
            "extensions": extensions,
            "threads": threads,
            "discovered_paths": discovered_paths,
            "total_found": len(discovered_paths)
        }
        
        if ctx:
            await ctx.info(f"? Directory enumeration completed! Found {len(discovered_paths)} paths")
        
        return scan_results
        
    except subprocess.TimeoutExpired:
        if ctx:
            await ctx.error("? Gobuster scan timed out")
        return {
            "status": "timeout",
            "error": "Scan timed out",
            "url": url
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"? Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "url": url
        }


@mcp.tool
async def nikto_scan(
    url: str,
    options: str = "-C all",
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Perform web vulnerability scanning using nikto.
    
    Args:
        url: Target URL to scan
        options: Additional nikto options
        
    Returns:
        Dictionary containing vulnerability scan results
    """
    if ctx:
        await ctx.info(f"? Starting nikto vulnerability scan on {url}")
    
    nikto_cmd = [
        KALI_TOOLS["nikto"],
        "-h", url,
        "-Format", "json",
        "-ask", "no"  # Don't prompt for user input
    ]
    
    # Add additional options
    if options:
        nikto_cmd.extend(options.split())
    
    try:
        if ctx:
            await ctx.info(f"? Executing: nikto scan")
        
        result = subprocess.run(
            nikto_cmd,
            capture_output=True,
            text=True,
            timeout=NETWORK_CONFIG["default_timeout"] * 15
        )
        
        # Parse nikto output
        vulnerabilities = _parse_nikto_output(result.stdout)
        
        scan_results = {
            "status": "completed",
            "url": url,
            "vulnerabilities": vulnerabilities,
            "total_vulnerabilities": len(vulnerabilities),
            "scan_options": options
        }
        
        if ctx:
            vuln_count = len(vulnerabilities)
            await ctx.info(f"? Nikto scan completed! Found {vuln_count} potential vulnerabilities")
        
        return scan_results
        
    except subprocess.TimeoutExpired:
        if ctx:
            await ctx.error("? Nikto scan timed out")
        return {
            "status": "timeout",
            "error": "Scan timed out",
            "url": url
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"? Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "url": url
        }


@mcp.tool
async def sqlmap_test(
    url: str,
    data: Optional[str] = None,
    technique: str = "BEUSTQ",
    level: int = 1,
    risk: int = 1,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Test for SQL injection vulnerabilities using sqlmap.
    
    Args:
        url: Target URL to test
        data: POST data (for POST requests)
        technique: SQL injection techniques to use
        level: Level of tests to perform (1-5)
        risk: Risk of tests to perform (1-3)
        
    Returns:
        Dictionary containing SQL injection test results
    """
    if ctx:
        await ctx.info(f"? Starting SQL injection test on {url}")
    
    sqlmap_cmd = [
        KALI_TOOLS["sqlmap"],
        "-u", url,
        "--batch",  # Never ask for user input
        "--technique", technique,
        "--level", str(level),
        "--risk", str(risk),
        "--output-dir", "/tmp/sqlmap_output"
    ]
    
    # Add POST data if provided
    if data:
        sqlmap_cmd.extend(["--data", data])
    
    try:
        if ctx:
            await ctx.info(f"? Executing: sqlmap with level {level}, risk {risk}")
        
        result = subprocess.run(
            sqlmap_cmd,
            capture_output=True,
            text=True,
            timeout=NETWORK_CONFIG["default_timeout"] * 20
        )
        
        # Parse sqlmap output
        injection_results = _parse_sqlmap_output(result.stdout)
        
        scan_results = {
            "status": "completed",
            "url": url,
            "injection_points": injection_results,
            "vulnerable": len(injection_results) > 0,
            "technique": technique,
            "level": level,
            "risk": risk
        }
        
        if ctx:
            if len(injection_results) > 0:
                await ctx.info(f"? SQL injection vulnerabilities found!")
            else:
                await ctx.info(f"? No SQL injection vulnerabilities detected")
        
        return scan_results
        
    except subprocess.TimeoutExpired:
        if ctx:
            await ctx.error("? SQLmap test timed out")
        return {
            "status": "timeout",
            "error": "Test timed out",
            "url": url
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"? Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "url": url
        }


@mcp.tool
async def web_technology_detection(
    url: str,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Detect web technologies used by a website using whatweb.
    
    Args:
        url: Target URL to analyze
        
    Returns:
        Dictionary containing detected technologies and frameworks
    """
    if ctx:
        await ctx.info(f"? Detecting web technologies on {url}")
    
    whatweb_cmd = [
        "whatweb",
        "--log-json", "-",
        "-a", "3",  # Aggressive level 3
        url
    ]
    
    try:
        if ctx:
            await ctx.info(f"? Executing: whatweb technology detection")
        
        result = subprocess.run(
            whatweb_cmd,
            capture_output=True,
            text=True,
            timeout=NETWORK_CONFIG["default_timeout"]
        )
        
        if result.returncode != 0:
            # Try alternative approach with curl + manual detection
            return await _manual_tech_detection(url, ctx)
        
        # Parse whatweb JSON output
        technologies = _parse_whatweb_output(result.stdout)
        
        scan_results = {
            "status": "completed",
            "url": url,
            "technologies": technologies,
            "total_technologies": len(technologies)
        }
        
        if ctx:
            tech_count = len(technologies)
            await ctx.info(f"? Technology detection completed! Found {tech_count} technologies")
        
        return scan_results
        
    except subprocess.TimeoutExpired:
        if ctx:
            await ctx.error("? Technology detection timed out")
        return {
            "status": "timeout",
            "error": "Detection timed out",
            "url": url
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"? Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "url": url
        }


async def _manual_tech_detection(url: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Fallback manual technology detection using curl."""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                headers = dict(response.headers)
                content = await response.text()
                
                technologies = []
                
                # Check server header
                if 'Server' in headers:
                    technologies.append({
                        "name": "Web Server",
                        "value": headers['Server'],
                        "confidence": "High"
                    })
                
                # Check for common frameworks in content
                framework_patterns = {
                    "WordPress": r'wp-content|wp-includes|wordpress',
                    "Drupal": r'drupal|sites/default',
                    "Joomla": r'joomla|option=com_',
                    "Laravel": r'laravel_session|csrf-token',
                    "React": r'react|__REACT_DEVTOOLS_GLOBAL_HOOK__',
                    "Vue.js": r'vue\.js|__VUE__',
                    "Angular": r'angular|ng-version'
                }
                
                for tech, pattern in framework_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        technologies.append({
                            "name": tech,
                            "confidence": "Medium"
                        })
                
                return {
                    "status": "completed",
                    "url": url,
                    "technologies": technologies,
                    "total_technologies": len(technologies),
                    "method": "manual_detection"
                }
                
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "url": url
        }


def _parse_gobuster_output(output: str) -> List[Dict[str, Any]]:
    """Parse gobuster output to extract discovered paths."""
    paths = []
    lines = output.split('\n')
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('=') and '/' in line:
            # Parse gobuster output format: /path (Status: 200) [Size: 1234]
            parts = line.split()
            if len(parts) >= 3:
                path = parts[0]
                status_match = re.search(r'Status: (\d+)', line)
                size_match = re.search(r'Size: (\d+)', line)
                
                path_info = {
                    "path": path,
                    "status_code": int(status_match.group(1)) if status_match else None,
                    "size": int(size_match.group(1)) if size_match else None
                }
                paths.append(path_info)
    
    return paths


def _parse_nikto_output(output: str) -> List[Dict[str, Any]]:
    """Parse nikto JSON output to extract vulnerabilities."""
    vulnerabilities = []
    
    try:
        # Nikto can output multiple JSON objects, parse each line
        for line in output.split('\n'):
            line = line.strip()
            if line and line.startswith('{'):
                try:
                    data = json.loads(line)
                    if 'vulnerabilities' in data:
                        for vuln in data['vulnerabilities']:
                            vulnerabilities.append({
                                "id": vuln.get('id'),
                                "msg": vuln.get('msg'),
                                "uri": vuln.get('uri'),
                                "method": vuln.get('method'),
                                "OSVDB": vuln.get('OSVDB'),
                                "severity": _classify_nikto_severity(vuln.get('msg', ''))
                            })
                except json.JSONDecodeError:
                    continue
    except Exception:
        # Fallback: parse text output
        vulnerabilities = _parse_nikto_text_output(output)
    
    return vulnerabilities


def _parse_nikto_text_output(output: str) -> List[Dict[str, Any]]:
    """Parse nikto text output as fallback."""
    vulnerabilities = []
    lines = output.split('\n')
    
    for line in lines:
        if '+ ' in line and ('OSVDB' in line or 'CVE' in line or 'error' in line.lower()):
            vulnerabilities.append({
                "id": "NIKTO-TEXT",
                "msg": line.strip().replace('+ ', ''),
                "severity": _classify_nikto_severity(line)
            })
    
    return vulnerabilities


def _classify_nikto_severity(message: str) -> str:
    """Classify nikto finding severity based on message content."""
    message_lower = message.lower()
    
    if any(keyword in message_lower for keyword in ['sql', 'injection', 'xss', 'command', 'execute']):
        return "high"
    elif any(keyword in message_lower for keyword in ['disclosure', 'expose', 'leak', 'password']):
        return "medium"
    elif any(keyword in message_lower for keyword in ['header', 'version', 'banner']):
        return "low"
    else:
        return "info"


def _parse_sqlmap_output(output: str) -> List[Dict[str, Any]]:
    """Parse sqlmap output to extract injection points."""
    injection_points = []
    lines = output.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Look for injection indicators
        if 'Parameter:' in line and 'is vulnerable' in line:
            param_match = re.search(r'Parameter: (\w+)', line)
            if param_match:
                injection_points.append({
                    "parameter": param_match.group(1),
                    "type": "SQL Injection",
                    "severity": "high"
                })
        
        # Look for specific injection types
        elif 'boolean-based blind' in line.lower():
            injection_points.append({
                "type": "Boolean-based blind SQL injection",
                "severity": "high",
                "technique": "boolean"
            })
        elif 'time-based blind' in line.lower():
            injection_points.append({
                "type": "Time-based blind SQL injection", 
                "severity": "high",
                "technique": "time"
            })
        elif 'union query' in line.lower():
            injection_points.append({
                "type": "UNION query SQL injection",
                "severity": "critical",
                "technique": "union"
            })
    
    return injection_points


def _parse_whatweb_output(output: str) -> List[Dict[str, Any]]:
    """Parse whatweb JSON output to extract technologies."""
    technologies = []
    
    try:
        for line in output.split('\n'):
            line = line.strip()
            if line and line.startswith('{'):
                try:
                    data = json.loads(line)
                    if 'plugins' in data:
                        for plugin_name, plugin_data in data['plugins'].items():
                            if isinstance(plugin_data, dict):
                                tech_info = {
                                    "name": plugin_name,
                                    "confidence": "Medium"
                                }
                                
                                # Extract version if available
                                if 'version' in plugin_data:
                                    tech_info["version"] = plugin_data['version']
                                
                                # Extract additional info
                                if 'string' in plugin_data:
                                    tech_info["details"] = plugin_data['string']
                                
                                technologies.append(tech_info)
                                
                except json.JSONDecodeError:
                    continue
    except Exception:
        # If JSON parsing fails, return empty list
        pass
    
    return technologies


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
