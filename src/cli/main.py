"""
Kali Agents CLI Interface - "At Your Service"

Rich terminal interface for interacting with the intelligent supervisor agent.
"""

import asyncio
import click
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from datetime import datetime
from typing import Dict, Any, Optional

from src.agents.supervisor import create_supervisor_agent
from src.models import AgentType, TaskStatus, Priority


console = Console()


class KaliAgentsCLI:
    """Rich CLI interface for Kali Agents system."""
    
    def __init__(self):
        self.supervisor = None
        self.console = Console()
        self.active_session = False
    
    async def initialize(self):
        """Initialize the supervisor agent."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("? Initializing Kali Agents...", total=None)
            
            try:
                self.supervisor = create_supervisor_agent()
                progress.update(task, description="? Supervisor Agent initialized")
                await asyncio.sleep(0.5)  # Visual delay
                
                progress.update(task, description="? Loading ML algorithms...")
                await asyncio.sleep(0.5)
                
                progress.update(task, description="? Connecting to MCP servers...")
                await asyncio.sleep(0.5)
                
                progress.update(task, description="? Kali Agents ready!")
                await asyncio.sleep(0.5)
                
            except Exception as e:
                progress.update(task, description=f"? Initialization failed: {str(e)}")
                raise
    
    def display_banner(self):
        """Display the Kali Agents banner."""
        banner = """
[bold red]????????????????????????????????????????????????????????????????[/bold red]
[bold red]?                    ? KALI AGENTS ?                         ?[/bold red]
[bold red]?                   "At Your Service"                          ?[/bold red]
[bold red]?                                                              ?[/bold red]
[bold red]?  Intelligent Cybersecurity Orchestration System             ?[/bold red]
[bold red]?  ML-Driven ? Adaptive ? Self-Learning                       ?[/bold red]
[bold red]????????????????????????????????????????????????????????????????[/bold red]

[bold cyan]? Supervisor Agent:[/bold cyan] [green]Online[/green]
[bold cyan]? ML Algorithms:[/bold cyan] [green]Fuzzy Logic ? Genetic Algorithm ? Q-Learning[/green]
[bold cyan]? MCP Servers:[/bold cyan] [green]Network ? Web ? Vulnerability ? Forensic ? Social ? Report[/green]
"""
        self.console.print(Panel(banner, style="bold blue"))
    
    def display_help(self):
        """Display help information."""
        help_text = """
[bold yellow]? AVAILABLE COMMANDS:[/bold yellow]

[bold cyan]pentest <target>[/bold cyan]     - Perform comprehensive penetration test
[bold cyan]scan <target>[/bold cyan]        - Quick network scan  
[bold cyan]web <target>[/bold cyan]         - Web application assessment
[bold cyan]recon <target>[/bold cyan]       - Reconnaissance and discovery
[bold cyan]osint <target>[/bold cyan]       - OSINT gathering
[bold cyan]status[/bold cyan]               - Show system status
[bold cyan]agents[/bold cyan]               - List all agents and their status
[bold cyan]history[/bold cyan]              - Show recent tasks
[bold cyan]help[/bold cyan]                 - Show this help
[bold cyan]exit[/bold cyan]                 - Exit Kali Agents

[bold yellow]? EXAMPLES:[/bold yellow]
[dim]pentest example.com[/dim]
[dim]scan 192.168.1.0/24[/dim]  
[dim]web https://target.com[/dim]
[dim]recon company.com[/dim]

[bold green]? TIP:[/bold green] The supervisor uses ML algorithms to optimize each task!
"""
        self.console.print(Panel(help_text, title="? Kali Agents Help", style="bold blue"))
    
    async def process_command(self, command: str) -> bool:
        """Process a user command."""
        parts = command.strip().split()
        if not parts:
            return True
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in ['exit', 'quit', 'q']:
            return False
        elif cmd == 'help':
            self.display_help()
        elif cmd == 'status':
            await self.show_status()
        elif cmd == 'agents':
            await self.show_agents()
        elif cmd == 'history':
            await self.show_history()
        elif cmd in ['pentest', 'scan', 'web', 'recon', 'osint']:
            if not args:
                self.console.print("[red]? Error: Please specify a target[/red]")
                return True
            
            target = args[0]
            await self.execute_task(cmd, target)
        else:
            self.console.print(f"[red]? Unknown command: {cmd}[/red]")
            self.console.print("[yellow]? Type 'help' for available commands[/yellow]")
        
        return True
    
    async def execute_task(self, task_type: str, target: str):
        """Execute a task using the supervisor agent."""
        # Map command to request
        request_mapping = {
            'pentest': f'Perform a comprehensive penetration test on {target}',
            'scan': f'Perform a network scan on {target}',
            'web': f'Perform web application assessment on {target}',
            'recon': f'Perform reconnaissance on {target}',
            'osint': f'Gather OSINT information on {target}'
        }
        
        request = request_mapping.get(task_type, f'Analyze {target}')
        
        # Show task initiation
        task_panel = Panel(
            f"[bold cyan]? Task:[/bold cyan] {request}\n"
            f"[bold cyan]? Target:[/bold cyan] {target}\n"
            f"[bold cyan]? Mode:[/bold cyan] Intelligent ML Orchestration",
            title="? Initiating Task",
            style="bold green"
        )
        self.console.print(task_panel)
        
        # Execute with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            
            # Create progress task
            progress_task = progress.add_task("? Supervisor analyzing request...", total=None)
            
            try:
                # Execute the task
                result = await self.supervisor.process_user_request(
                    request, 
                    {"target": target, "task_type": task_type}
                )
                
                # Update progress
                progress.update(progress_task, description="? Task completed!")
                await asyncio.sleep(0.5)
                
                # Display results
                await self.display_task_results(result)
                
            except Exception as e:
                progress.update(progress_task, description=f"? Task failed: {str(e)}")
                self.console.print(f"[red]? Error executing task: {str(e)}[/red]")
    
    async def display_task_results(self, result: Dict[str, Any]):
        """Display task execution results in a formatted way."""
        task_id = result.get("task_id", "unknown")
        status = result.get("status", "unknown")
        execution_results = result.get("results", {})
        performance = result.get("performance", {})
        
        # Create results table
        results_table = Table(title="? Task Execution Results")
        results_table.add_column("Metric", style="bold cyan")
        results_table.add_column("Value", style="bold green")
        
        results_table.add_row("Task ID", task_id)
        results_table.add_row("Status", status.upper())
        results_table.add_row("Execution Time", f"{execution_results.get('execution_time', 0):.2f}s")
        results_table.add_row("Steps Completed", str(len(execution_results.get('steps_completed', []))))
        results_table.add_row("Findings", str(len(execution_results.get('findings', []))))
        results_table.add_row("Errors", str(len(execution_results.get('errors', []))))
        
        # Performance metrics
        if performance:
            results_table.add_row("Success Rate", f"{performance.get('success_rate', 0):.2%}")
            results_table.add_row("Confidence", f"{performance.get('confidence_score', 0):.2%}")
        
        self.console.print(results_table)
        
        # Display findings if any
        findings = execution_results.get('findings', [])
        if findings:
            findings_table = Table(title="? Security Findings")
            findings_table.add_column("Type", style="bold yellow")
            findings_table.add_column("Details", style="white")
            findings_table.add_column("Severity", style="bold red")
            
            for finding in findings[:10]:  # Show first 10 findings
                findings_table.add_row(
                    finding.get('type', 'unknown'),
                    str(finding.get('description', finding.get('path', finding.get('host', 'N/A')))),
                    finding.get('severity', 'info').upper()
                )
            
            if len(findings) > 10:
                findings_table.add_row("...", f"And {len(findings) - 10} more findings", "")
            
            self.console.print(findings_table)
        
        # Display errors if any
        errors = execution_results.get('errors', [])
        if errors:
            error_panel = Panel(
                "\n".join([f"? {error.get('error', str(error))}" for error in errors]),
                title="??  Errors",
                style="bold red"
            )
            self.console.print(error_panel)
        
        # Show learning insights
        learning_panel = Panel(
            "[bold green]? ML Learning:[/bold green] Supervisor adapted strategies based on execution\n"
            "[bold cyan]? Adaptation:[/bold cyan] Performance data added to training set\n"
            "[bold yellow]? Improvement:[/bold yellow] Future tasks will benefit from this experience",
            title="? Intelligent Learning",
            style="bold blue"
        )
        self.console.print(learning_panel)
    
    async def show_status(self):
        """Show current system status."""
        if not self.supervisor:
            self.console.print("[red]? Supervisor not initialized[/red]")
            return
        
        status = self.supervisor.get_system_status()
        
        # Create status table
        status_table = Table(title="??  System Status")
        status_table.add_column("Component", style="bold cyan")
        status_table.add_column("Status", style="bold green")
        
        status_table.add_row("Supervisor ID", status.get('supervisor_id', 'N/A'))
        status_table.add_row("Active Tasks", str(status.get('active_tasks', 0)))
        status_table.add_row("Completed Tasks", str(status.get('completed_tasks', 0)))
        status_table.add_row("Total Decisions", str(status.get('total_decisions', 0)))
        
        # ML Algorithms status
        algorithms = status.get('learning_algorithms', [])
        status_table.add_row("ML Algorithms", f"{len(algorithms)} active")
        
        self.console.print(status_table)
        
        # Show ML algorithms details
        if algorithms:
            ml_table = Table(title="? ML Algorithms")
            ml_table.add_column("Algorithm", style="bold cyan")
            ml_table.add_column("Status", style="bold green")
            
            for algo in algorithms:
                ml_table.add_row(algo.replace('_', ' ').title(), "? Active")
            
            self.console.print(ml_table)
    
    async def show_agents(self):
        """Show all agents and their status."""
        if not self.supervisor:
            self.console.print("[red]? Supervisor not initialized[/red]")
            return
        
        status = self.supervisor.get_system_status()
        agents = status.get('agents', {})
        
        # Create agents table
        agents_table = Table(title="? Agent Status")
        agents_table.add_column("Agent ID", style="bold cyan")
        agents_table.add_column("Type", style="bold yellow")
        agents_table.add_column("Status", style="bold green")
        agents_table.add_column("Capabilities", style="white")
        
        for agent_id, agent_status in agents.items():
            agent_type = agent_id.replace('_agent', '').title()
            capabilities = self._get_agent_capabilities(agent_id)
            
            agents_table.add_row(
                agent_id,
                agent_type,
                agent_status.title(),
                capabilities
            )
        
        self.console.print(agents_table)
    
    def _get_agent_capabilities(self, agent_id: str) -> str:
        """Get agent capabilities description."""
        capability_map = {
            'network_agent': 'nmap, masscan, network discovery',
            'web_agent': 'gobuster, nikto, sqlmap, whatweb',
            'vulnerability_agent': 'searchsploit, nuclei, exploits',
            'forensic_agent': 'volatility, binwalk, file analysis',
            'social_agent': 'theHarvester, OSINT, recon-ng',
            'report_agent': 'PDF generation, templates'
        }
        return capability_map.get(agent_id, 'Various security tools')
    
    async def show_history(self):
        """Show recent task history."""
        # This would show completed tasks from the supervisor
        history_panel = Panel(
            "[bold yellow]? Task History Feature[/bold yellow]\n\n"
            "[dim]This feature will show recent completed tasks, their performance metrics,\n"
            "and learning outcomes. Currently in development.[/dim]\n\n"
            "[bold cyan]? Tip:[/bold cyan] Use 'status' to see current system state",
            title="? History",
            style="bold blue"
        )
        self.console.print(history_panel)
    
    async def run_interactive_session(self):
        """Run the main interactive CLI session."""
        self.active_session = True
        
        try:
            # Initialize the system
            await self.initialize()
            
            # Display banner
            self.display_banner()
            
            # Show initial help
            self.console.print("\n[bold green]? Welcome to Kali Agents![/bold green]")
            self.console.print("[yellow]? Type 'help' for available commands or try 'pentest example.com'[/yellow]\n")
            
            # Main command loop
            while self.active_session:
                try:
                    # Get user input
                    command = Prompt.ask(
                        "[bold red]kali-agents[/bold red]",
                        console=self.console
                    )
                    
                    # Process command
                    if command.strip():
                        continue_session = await self.process_command(command)
                        if not continue_session:
                            break
                
                except KeyboardInterrupt:
                    if Confirm.ask("\n[yellow]Are you sure you want to exit?[/yellow]"):
                        break
                    else:
                        self.console.print("[green]Continuing...[/green]")
                
                except Exception as e:
                    self.console.print(f"[red]? Error: {str(e)}[/red]")
        
        finally:
            # Cleanup
            self.console.print("\n[bold blue]? Thank you for using Kali Agents![/bold blue]")
            self.console.print("[green]Stay secure! ?[/green]")


# Click CLI commands
@click.group()
def cli():
    """Kali Agents - Intelligent Cybersecurity Orchestration System"""
    pass


@cli.command()
def interactive():
    """Start interactive CLI session"""
    cli_interface = KaliAgentsCLI()
    asyncio.run(cli_interface.run_interactive_session())


@cli.command()
@click.argument('target')
@click.option('--type', 'task_type', default='pentest', 
              type=click.Choice(['pentest', 'scan', 'web', 'recon', 'osint']),
              help='Type of assessment to perform')
def run(target, task_type):
    """Run a single task against a target"""
    async def execute_single_task():
        cli_interface = KaliAgentsCLI()
        await cli_interface.initialize()
        await cli_interface.execute_task(task_type, target)
    
    asyncio.run(execute_single_task())


@cli.command()
def demo():
    """Run a demonstration of Kali Agents capabilities"""
    async def run_demo():
        cli_interface = KaliAgentsCLI()
        
        # Initialize
        console.print("[bold green]? Starting Kali Agents Demo...[/bold green]")
        await cli_interface.initialize()
        cli_interface.display_banner()
        
        # Demo scenarios
        demo_scenarios = [
            ("Network Scan", "scan", "scanme.nmap.org"),
            ("Web Assessment", "web", "example.com"),
            ("Quick Recon", "recon", "github.com")
        ]
        
        for scenario_name, task_type, target in demo_scenarios:
            console.print(f"\n[bold yellow]? Demo Scenario: {scenario_name}[/bold yellow]")
            
            if Confirm.ask(f"Execute {scenario_name} on {target}?"):
                await cli_interface.execute_task(task_type, target)
            
            console.print("\n" + "="*60)
        
        console.print("\n[bold green]? Demo completed![/bold green]")
        console.print("[yellow]? Try 'kali-agents interactive' for full experience[/yellow]")
    
    asyncio.run(run_demo())


if __name__ == "__main__":
    cli()
