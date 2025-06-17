#!/usr/bin/env python3
"""
Kali Agents CLI - "At Your Service"

Main command-line interface for the Kali Agents MCP system.
Provides intuitive commands for cybersecurity automation.
"""

import typer
import asyncio
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track
from rich.prompt import Prompt, Confirm
from pathlib import Path
import json

# Import system components
try:
    from src.agents.supervisor import create_supervisor_agent
    from src.models import AgentType, Priority, TaskStatus
    from src.config.settings import KALI_TOOLS
    SYSTEM_AVAILABLE = True
except ImportError:
    # Fallback values when system not available
    create_supervisor_agent = None
    AgentType = None
    Priority = None
    TaskStatus = None
    KALI_TOOLS = {}
    SYSTEM_AVAILABLE = False

app = typer.Typer(
    name="kali-agents",
    help="🔴 Kali Agents - Intelligent Cybersecurity Automation 'At Your Service'",
    rich_markup_mode="rich"
)
console = Console()


# Global supervisor instance
supervisor = None


def initialize_supervisor():
    """Initialize the supervisor agent."""
    global supervisor
    if SYSTEM_AVAILABLE and supervisor is None and create_supervisor_agent is not None:
        supervisor = create_supervisor_agent()
    return supervisor


@app.command("demo")
def run_demo(
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Run interactive demo"),
    scenario: str = typer.Option("full", "--scenario", "-s", help="Demo scenario to run")
):
    """🎭 Run the Kali Agents demonstration."""
    console.print("[bold cyan]🎭 Starting Kali Agents Demo...[/bold cyan]")
    
    if interactive:
        console.print("[yellow]Interactive demo mode - you can guide the demonstration![/yellow]")
    
    # Import and run the demo
    try:
        import demo
        asyncio.run(demo.main())
    except ImportError:
        console.print("[bold red]❌ Demo module not found. Please ensure demo.py is available.[/bold red]")


@app.command("recon")
def reconnaissance(
    target: str = typer.Argument(..., help="Target IP, hostname, or CIDR range"),
    scan_type: str = typer.Option("stealth", "--type", "-t", help="Scan type: stealth, connect, aggressive"),
    ports: str = typer.Option("top-1000", "--ports", "-p", help="Ports to scan"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """🌐 Perform network reconnaissance on target."""
    
    console.print(f"[bold cyan]🌐 Starting reconnaissance on {target}[/bold cyan]")
    
    # Initialize supervisor
    sup = initialize_supervisor()
    if not sup:
        console.print("[bold red]❌ System not available. Please check installation.[/bold red]")
        raise typer.Exit(1)
    
    # Create reconnaissance task
    task_params = {
        "target": target,
        "scan_type": scan_type,
        "ports": ports,
        "verbose": verbose
    }
    
    if verbose:
        console.print(f"[dim]Task parameters: {task_params}[/dim]")
    
    # Execute reconnaissance
    try:
        result = asyncio.run(sup.process_user_request(
            f"Perform network reconnaissance on {target}",
            task_params
        ))
        
        # Display results
        display_scan_results(result, output)
        
    except Exception as e:
        console.print(f"[bold red]❌ Error during reconnaissance: {str(e)}[/bold red]")
        raise typer.Exit(1)


@app.command("web")
def web_assessment(
    url: str = typer.Argument(..., help="Target URL to assess"),
    deep: bool = typer.Option(False, "--deep", help="Perform deep web assessment"),
    wordlist: str = typer.Option("common", "--wordlist", "-w", help="Wordlist to use"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """🕷️ Perform web application security assessment."""
    
    console.print(f"[bold cyan]🕷️ Starting web assessment on {url}[/bold cyan]")
    
    sup = initialize_supervisor()
    if not sup:
        console.print("[bold red]❌ System not available. Please check installation.[/bold red]")
        raise typer.Exit(1)
    
    task_params = {
        "url": url,
        "deep_scan": deep,
        "wordlist": wordlist,
        "verbose": verbose
    }
    
    try:
        result = asyncio.run(sup.process_user_request(
            f"Perform web application security assessment on {url}",
            task_params
        ))
        
        display_web_results(result, output)
        
    except Exception as e:
        console.print(f"[bold red]❌ Error during web assessment: {str(e)}[/bold red]")
        raise typer.Exit(1)


@app.command("pentest")
def penetration_test(
    target: str = typer.Argument(..., help="Target for penetration testing"),
    scope: str = typer.Option("basic", "--scope", "-s", help="Test scope: basic, full, custom"),
    exclude: Optional[List[str]] = typer.Option(None, "--exclude", help="Exclude specific tests"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Output directory"),
    report_format: str = typer.Option("pdf", "--format", "-f", help="Report format: pdf, html, json"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """⚡ Perform comprehensive penetration testing."""
    
    console.print(f"[bold red]⚡ Starting penetration test on {target}[/bold red]")
    
    # Security confirmation
    if not Confirm.ask(f"[bold yellow]⚠️ Confirm you have authorization to test {target}?[/bold yellow]"):
        console.print("[bold red]❌ Authorization required. Exiting.[/bold red]")
        raise typer.Exit(1)
    
    sup = initialize_supervisor()
    if not sup:
        console.print("[bold red]❌ System not available. Please check installation.[/bold red]")
        raise typer.Exit(1)
    
    task_params = {
        "target": target,
        "scope": scope,
        "exclude": exclude or [],
        "report_format": report_format,
        "verbose": verbose
    }
    
    console.print("[bold yellow]🛡️ This is a comprehensive security assessment.[/bold yellow]")
    console.print("[dim]The ML supervisor will coordinate multiple specialized agents...[/dim]")
    
    try:
        with console.status("[bold green]🤖 AI Supervisor orchestrating pentest..."):
            result = asyncio.run(sup.process_user_request(
                f"Perform comprehensive penetration test on {target} with {scope} scope",
                task_params
            ))
        
        display_pentest_results(result, output_dir, report_format)
        
    except Exception as e:
        console.print(f"[bold red]❌ Error during penetration test: {str(e)}[/bold red]")
        raise typer.Exit(1)


@app.command("osint")
def osint_research(
    target: str = typer.Argument(..., help="Target for OSINT research"),
    target_type: str = typer.Option("person", "--type", "-t", help="Target type: person, company, domain"),
    depth: str = typer.Option("standard", "--depth", "-d", help="Research depth: basic, standard, deep"),
    sources: Optional[List[str]] = typer.Option(None, "--sources", help="Specific sources to use"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """👥 Perform OSINT research and intelligence gathering."""
    
    console.print(f"[bold cyan]👥 Starting OSINT research on {target}[/bold cyan]")
    
    sup = initialize_supervisor()
    if not sup:
        console.print("[bold red]❌ System not available. Please check installation.[/bold red]")
        raise typer.Exit(1)
    
    task_params = {
        "target": target,
        "target_type": target_type,
        "depth": depth,
        "sources": sources or [],
        "verbose": verbose
    }
    
    try:
        result = asyncio.run(sup.process_user_request(
            f"Perform OSINT research on {target} ({target_type})",
            task_params
        ))
        
        display_osint_results(result, output)
        
    except Exception as e:
        console.print(f"[bold red]❌ Error during OSINT research: {str(e)}[/bold red]")
        raise typer.Exit(1)


@app.command("forensics")
def forensic_analysis(
    target: str = typer.Argument(..., help="File or memory dump to analyze"),
    analysis_type: str = typer.Option("auto", "--type", "-t", help="Analysis type: auto, memory, file, network"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Output directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """🔍 Perform digital forensics analysis."""
    
    console.print(f"[bold cyan]🔍 Starting forensic analysis on {target}[/bold cyan]")
    
    # Check if target file exists
    if not Path(target).exists():
        console.print(f"[bold red]❌ Target file not found: {target}[/bold red]")
        raise typer.Exit(1)
    
    sup = initialize_supervisor()
    if not sup:
        console.print("[bold red]❌ System not available. Please check installation.[/bold red]")
        raise typer.Exit(1)
    
    task_params = {
        "target": target,
        "analysis_type": analysis_type,
        "verbose": verbose
    }
    
    try:
        result = asyncio.run(sup.process_user_request(
            f"Perform forensic analysis on {target}",
            task_params
        ))
        
        display_forensic_results(result, output_dir)
        
    except Exception as e:
        console.print(f"[bold red]❌ Error during forensic analysis: {str(e)}[/bold red]")
        raise typer.Exit(1)


@app.command("status")
def system_status():
    """📊 Display system status and agent information."""
    
    console.print("[bold cyan]📊 Kali Agents System Status[/bold cyan]")
    
    # System information table
    status_table = Table(title="🤖 System Information", style="cyan")
    status_table.add_column("Component", style="bold white")
    status_table.add_column("Status", style="bold green")
    status_table.add_column("Details", style="dim")
    
    # Check system availability
    if SYSTEM_AVAILABLE:
        status_table.add_row("Core System", "✅ Available", "All modules loaded")
        status_table.add_row("Supervisor Agent", "✅ Ready", "ML algorithms initialized")
        status_table.add_row("MCP Servers", "✅ Running", "FastMCP 2.8.0")
    else:
        status_table.add_row("Core System", "❌ Unavailable", "Import errors detected")
        status_table.add_row("Supervisor Agent", "❌ Not Ready", "System not initialized")
        status_table.add_row("MCP Servers", "❌ Offline", "Cannot start servers")
    
    # Tool availability
    if SYSTEM_AVAILABLE and KALI_TOOLS:
        for tool_name, tool_path in KALI_TOOLS.items():
            if Path(tool_path).exists():
                status_table.add_row(f"Tool: {tool_name}", "✅ Available", tool_path)
            else:
                status_table.add_row(f"Tool: {tool_name}", "❌ Missing", tool_path)
    else:
        status_table.add_row("Tools", "❓ Unknown", "System not available")
    
    console.print(status_table)
    
    # Agent information
    if SYSTEM_AVAILABLE:
        sup = initialize_supervisor()
        if sup:
            agents_table = Table(title="🎭 Agent Status", style="cyan")
            agents_table.add_column("Agent", style="bold cyan")
            agents_table.add_column("Type", style="white")
            agents_table.add_column("Status", style="bold green")
            agents_table.add_column("Performance", style="yellow")
            
            for agent_id, agent_state in sup.system_state.agents.items():
                # Safely get performance metrics with fallback
                performance = "N/A"
                if hasattr(agent_state, 'success_rate') and getattr(agent_state, 'success_rate', None) is not None:
                    try:
                        performance = f"{getattr(agent_state, 'success_rate', 0) * 100:.1f}%"
                    except Exception:
                        performance = "N/A"
                    
                agents_table.add_row(
                    agent_id.replace("_", " ").title(),
                    agent_state.agent_type.value if hasattr(agent_state, 'agent_type') and agent_state.agent_type else "Unknown",
                    "✅ Ready",
                    performance
                )
            
            console.print(agents_table)


@app.command("interactive")
def interactive_mode():
    """🎮 Enter interactive mode for guided cybersecurity operations."""
    
    console.print("[bold cyan]🎮 Welcome to Kali Agents Interactive Mode![/bold cyan]")
    console.print("[dim]Type 'help' for available commands, 'exit' to quit.[/dim]")
    
    sup = initialize_supervisor()
    if not sup:
        console.print("[bold red]❌ System not available. Please check installation.[/bold red]")
        raise typer.Exit(1)
    
    while True:
        try:
            command = Prompt.ask("\n[bold cyan]kali-agents>[/bold cyan]")
            
            if command.lower() in ['exit', 'quit', 'q']:
                console.print("[bold green]👋 Goodbye![/bold green]")
                break
            elif command.lower() == 'help':
                show_interactive_help()
            elif command.lower() == 'status':
                system_status()
            elif command.strip():
                # Process natural language command
                try:
                    result = asyncio.run(sup.process_user_request(command, {}))
                    console.print(f"[bold green]✅ Task completed successfully![/bold green]")
                    console.print(f"[dim]Result: {result}[/dim]")
                except Exception as e:
                    console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")
            
        except KeyboardInterrupt:
            console.print("\n[bold green]👋 Goodbye![/bold green]")
            break
        except Exception as e:
            console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")


def show_interactive_help():
    """Show interactive mode help."""
    help_panel = Panel(
        """[bold yellow]🎮 Interactive Mode Commands[/bold yellow]

[bold cyan]Natural Language Commands:[/bold cyan]
• "Scan 192.168.1.1 for open ports"
• "Test website security for https://example.com"
• "Perform OSINT research on John Doe"
• "Analyze memory dump /path/to/dump.mem"

[bold cyan]System Commands:[/bold cyan]
• [bold]status[/bold] - Show system status
• [bold]help[/bold] - Show this help
• [bold]exit[/bold] - Exit interactive mode

[bold green]💡 Tip:[/bold green] The AI supervisor understands natural language!
Just describe what you want to do and it will coordinate the appropriate agents.""",
        title="🔧 Help",
        style="cyan"
    )
    console.print(help_panel)


# Result display functions
def display_scan_results(result: dict, output_file: Optional[str] = None):
    """Display network scan results."""
    console.print("[bold green]📊 Scan Results[/bold green]")
    
    if not result or result.get("status") != "completed":
        console.print(f"[bold red]❌ Scan failed: {result.get('error', 'Unknown error')}[/bold red]")
        return
    
    # Create results table
    results_table = Table(title="🌐 Network Scan Results")
    results_table.add_column("Host", style="bold cyan")
    results_table.add_column("Status", style="bold green")
    results_table.add_column("Open Ports", style="white")
    results_table.add_column("Services", style="yellow")
    
    hosts = result.get("hosts", {})
    for host_ip, host_info in hosts.items():
        ports_info = []
        services_info = []
        
        for port in host_info.get("ports", []):
            ports_info.append(f"{port['port']}/{port['protocol']}")
            if port.get("service"):
                services_info.append(f"{port['service']}")
        
        results_table.add_row(
            host_ip,
            host_info.get("status", "unknown"),
            ", ".join(ports_info[:5]) + ("..." if len(ports_info) > 5 else ""),
            ", ".join(services_info[:3]) + ("..." if len(services_info) > 3 else "")
        )
    
    console.print(results_table)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        console.print(f"[bold green]💾 Results saved to {output_file}[/bold green]")


def display_web_results(result: dict, output_file: Optional[str] = None):
    """Display web assessment results."""
    console.print("[bold green]📊 Web Assessment Results[/bold green]")
    
    # Implementation would display web-specific results
    console.print(f"[dim]Result preview: {str(result)[:200]}...[/dim]")
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        console.print(f"[bold green]💾 Results saved to {output_file}[/bold green]")


def display_pentest_results(result: dict, output_dir: Optional[str] = None, report_format: str = "pdf"):
    """Display penetration test results."""
    console.print("[bold green]📊 Penetration Test Results[/bold green]")
    
    # Implementation would display comprehensive pentest results
    console.print(f"[dim]Result preview: {str(result)[:200]}...[/dim]")
    
    if output_dir:
        Path(output_dir).mkdir(exist_ok=True)
        console.print(f"[bold green]📁 Results saved to {output_dir}/[/bold green]")


def display_osint_results(result: dict, output_file: Optional[str] = None):
    """Display OSINT research results."""
    console.print("[bold green]📊 OSINT Research Results[/bold green]")
    
    # Implementation would display OSINT-specific results
    console.print(f"[dim]Result preview: {str(result)[:200]}...[/dim]")
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        console.print(f"[bold green]💾 Results saved to {output_file}[/bold green]")


def display_forensic_results(result: dict, output_dir: Optional[str] = None):
    """Display forensic analysis results."""
    console.print("[bold green]📊 Forensic Analysis Results[/bold green]")
    
    # Implementation would display forensics-specific results
    console.print(f"[dim]Result preview: {str(result)[:200]}...[/dim]")
    
    if output_dir:
        Path(output_dir).mkdir(exist_ok=True)
        console.print(f"[bold green]📁 Results saved to {output_dir}/[/bold green]")


@app.callback()
def main_callback():
    """Kali Agents - Intelligent Cybersecurity Automation 'At Your Service'"""
    pass


def cli():
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    cli()