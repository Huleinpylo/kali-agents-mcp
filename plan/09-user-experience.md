# User Experience

**Status**: MEDIUM PRIORITY - Improves usability and adoption

**Target Timeline**: Weeks 11-14 (Phase 3)

---

## Overview

Enhance user experience through improved CLI, web interface, and overall usability.

### Priority: MEDIUM
**Effort**: Medium (3-4 weeks)
**Impact**: User satisfaction, adoption rate, ease of use

### Current State

```
UX Status:
✅ Basic CLI with Rich output
✅ API documentation
❌ No web UI
❌ Limited CLI interactivity
❌ No configuration wizard
❌ No interactive help
❌ Limited error messages
```

---

## 1. Enhanced CLI Experience

### Implementation Details

#### 1.1 Interactive Mode

**File**: `src/cli/interactive.py`

```python
"""Interactive CLI mode."""

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.syntax import Syntax

console = Console()

class InteractiveCLI:
    """Interactive command-line interface."""

    def __init__(self):
        self.session = PromptSession(
            history=FileHistory('.kali-agents-history')
        )
        self.commands = {
            'scan': self.scan,
            'list': self.list_scans,
            'report': self.generate_report,
            'help': self.show_help,
            'exit': self.exit
        }
        self.completer = WordCompleter(
            list(self.commands.keys()),
            ignore_case=True
        )

    async def run(self):
        """Run interactive session."""
        console.print("[bold blue]Kali Agents MCP Interactive Mode[/bold blue]")
        console.print("Type 'help' for available commands or 'exit' to quit.\n")

        while True:
            try:
                command = await self.session.prompt_async(
                    '> ',
                    completer=self.completer
                )

                if not command.strip():
                    continue

                await self.execute_command(command)

            except KeyboardInterrupt:
                continue
            except EOFError:
                break

    async def execute_command(self, command: str):
        """Execute command."""
        parts = command.split()
        cmd = parts[0].lower()

        if cmd in self.commands:
            await self.commands[cmd](*parts[1:])
        else:
            console.print(f"[red]Unknown command: {cmd}[/red]")
            console.print("Type 'help' for available commands.")

    async def scan(self, *args):
        """Execute scan command."""
        if not args:
            target = await self.session.prompt_async('Target: ')
            scan_type = await self.session.prompt_async(
                'Scan type (quick/full/custom): ',
                default='quick'
            )
        else:
            target = args[0]
            scan_type = args[1] if len(args) > 1 else 'quick'

        console.print(f"[green]Starting {scan_type} scan of {target}...[/green]")
        # Execute scan
```

#### 1.2 Configuration Wizard

**File**: `src/cli/wizard.py`

```python
"""Configuration wizard."""

from questionary import (
    text, password, select, checkbox, confirm
)
from pathlib import Path
import yaml

async def run_configuration_wizard():
    """Interactive configuration wizard."""
    console.print("[bold]Kali Agents MCP Configuration Wizard[/bold]\n")

    config = {}

    # API Keys
    console.print("[cyan]API Keys Configuration[/cyan]")
    config['openai_api_key'] = await password(
        "OpenAI API Key (optional):"
    ).ask_async()

    config['shodan_api_key'] = await password(
        "Shodan API Key (optional):"
    ).ask_async()

    # Scan Preferences
    console.print("\n[cyan]Scan Preferences[/cyan]")
    config['default_scan_type'] = await select(
        "Default scan type:",
        choices=['quick', 'full', 'stealth', 'aggressive']
    ).ask_async()

    config['max_concurrent_scans'] = await text(
        "Maximum concurrent scans:",
        default="5"
    ).ask_async()

    # Report Preferences
    console.print("\n[cyan]Report Preferences[/cyan]")
    config['default_report_format'] = await select(
        "Default report format:",
        choices=['pdf', 'html', 'json', 'markdown']
    ).ask_async()

    config['report_branding'] = await confirm(
        "Add custom branding to reports?"
    ).ask_async()

    if config['report_branding']:
        config['company_name'] = await text("Company name:").ask_async()
        config['logo_path'] = await text("Logo path (optional):").ask_async()

    # MCP Servers
    console.print("\n[cyan]MCP Servers[/cyan]")
    enabled_servers = await checkbox(
        "Select MCP servers to enable:",
        choices=[
            'Network', 'Web', 'Vulnerability',
            'Social', 'Forensic', 'Report'
        ]
    ).ask_async()

    config['enabled_servers'] = enabled_servers

    # Save configuration
    console.print("\n[cyan]Save Configuration[/cyan]")
    config_path = await text(
        "Configuration file path:",
        default="config.yaml"
    ).ask_async()

    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    console.print(f"\n[green]✓ Configuration saved to {config_path}[/green]")
```

#### 1.3 Better Error Messages

**File**: `src/cli/errors.py`

```python
"""User-friendly error messages."""

from rich.console import Console
from rich.panel import Panel

console = Console()

class UserFriendlyError:
    """Convert technical errors to user-friendly messages."""

    ERROR_MESSAGES = {
        'ToolNotFoundError': {
            'title': 'Required Tool Not Found',
            'template': '''
The tool "{tool_name}" is required but not installed.

To install:
{install_instructions}

After installation, try your command again.
            '''
        },
        'InvalidTargetError': {
            'title': 'Invalid Target',
            'template': '''
The target "{target}" is invalid.

Valid target formats:
• IP address: 192.168.1.1
• Hostname: example.com
• CIDR range: 192.168.1.0/24
• URL: https://example.com

Example: kali-agents scan 192.168.1.1
            '''
        },
        'RateLimitError': {
            'title': 'Rate Limit Exceeded',
            'template': '''
API rate limit exceeded for {service}.

Retry after: {retry_after} seconds

Consider:
• Reducing scan frequency
• Upgrading API plan
• Using different API key
            '''
        }
    }

    @classmethod
    def display_error(cls, error_type: str, **kwargs):
        """Display user-friendly error."""
        if error_type in cls.ERROR_MESSAGES:
            msg_config = cls.ERROR_MESSAGES[error_type]
            message = msg_config['template'].format(**kwargs)

            console.print(
                Panel(
                    message.strip(),
                    title=f"[red]{msg_config['title']}[/red]",
                    border_style="red"
                )
            )
        else:
            console.print(f"[red]Error: {error_type}[/red]")
```

### Acceptance Criteria
- [ ] Interactive mode working
- [ ] Configuration wizard complete
- [ ] Command auto-completion
- [ ] User-friendly error messages
- [ ] Command history support

**Effort Estimate**: 1 week

---

## 2. Web Dashboard

### Implementation Details

#### 2.1 React Frontend

**File**: `frontend/src/App.tsx`

```typescript
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Scans from './pages/Scans';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/scans" element={<Scans />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

#### 2.2 Real-time Updates

**File**: `frontend/src/hooks/useWebSocket.ts`

```typescript
import { useEffect, useState } from 'react';

export function useWebSocket(scanId: string) {
  const [progress, setProgress] = useState<any>(null);
  const [status, setStatus] = useState<string>('connecting');

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/scan/${scanId}`);

    ws.onopen = () => {
      setStatus('connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data);
    };

    ws.onerror = () => {
      setStatus('error');
    };

    ws.onclose = () => {
      setStatus('disconnected');
    };

    return () => ws.close();
  }, [scanId]);

  return { progress, status };
}
```

#### 2.3 Dashboard Components

**File**: `frontend/src/pages/Dashboard.tsx`

```typescript
import React from 'react';
import { Card, Grid, Progress, Badge } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';

export default function Dashboard() {
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: () => fetch('/api/stats').then(r => r.json())
  });

  return (
    <Grid>
      <Grid.Col span={3}>
        <Card>
          <h3>Total Scans</h3>
          <p>{stats?.total_scans || 0}</p>
        </Card>
      </Grid.Col>

      <Grid.Col span={3}>
        <Card>
          <h3>Active Scans</h3>
          <p>{stats?.active_scans || 0}</p>
        </Card>
      </Grid.Col>

      <Grid.Col span={3}>
        <Card>
          <h3>Vulnerabilities</h3>
          <Badge color="red">{stats?.critical_vulns || 0} Critical</Badge>
          <Badge color="orange">{stats?.high_vulns || 0} High</Badge>
        </Card>
      </Grid.Col>

      <Grid.Col span={3}>
        <Card>
          <h3>Success Rate</h3>
          <Progress value={stats?.success_rate || 0} />
        </Card>
      </Grid.Col>

      <Grid.Col span={12}>
        <Card>
          <h3>Recent Scans</h3>
          {/* Scan list */}
        </Card>
      </Grid.Col>
    </Grid>
  );
}
```

### Acceptance Criteria
- [ ] Web dashboard functional
- [ ] Real-time updates working
- [ ] Responsive design
- [ ] Scan management UI
- [ ] Report viewing

**Effort Estimate**: 2 weeks

---

## 3. Improved Documentation and Help

### Implementation Details

#### 3.1 Contextual Help

**File**: `src/cli/help.py`

```python
"""Enhanced help system."""

from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

console = Console()

HELP_CONTENT = {
    'scan': '''
# Scan Command

Execute security scans against targets.

## Usage
```
kali-agents scan [OPTIONS] TARGET
```

## Options
- `--type`: Scan type (quick, full, stealth, aggressive)
- `--ports`: Port specification (e.g., 80,443 or 1-1000)
- `--timeout`: Scan timeout in seconds

## Examples

Quick scan:
```
kali-agents scan example.com
```

Full port scan:
```
kali-agents scan --type full 192.168.1.1
```

Stealth scan on specific ports:
```
kali-agents scan --type stealth --ports 80,443,8080 target.com
```
    ''',
    'report': '''
# Report Command

Generate professional security reports.

## Usage
```
kali-agents report [OPTIONS] SCAN_ID
```

## Options
- `--format`: Output format (pdf, html, json, markdown)
- `--template`: Report template (executive, technical, compliance)
- `--output`: Output file path

## Examples

Generate PDF report:
```
kali-agents report --format pdf --output report.pdf scan_123
```

Executive summary:
```
kali-agents report --template executive scan_123
```
    '''
}

def show_contextual_help(command: str):
    """Show contextual help for command."""
    if command in HELP_CONTENT:
        md = Markdown(HELP_CONTENT[command])
        console.print(md)
    else:
        console.print(f"[yellow]No help available for: {command}[/yellow]")
```

#### 3.2 Examples and Tutorials

**File**: `src/cli/examples.py`

```python
"""Built-in examples and tutorials."""

from rich.console import Console
from rich.syntax import Syntax

console = Console()

EXAMPLES = {
    'basic_scan': {
        'title': 'Basic Network Scan',
        'description': 'Scan a target for open ports and services',
        'commands': [
            'kali-agents scan 192.168.1.1',
            'kali-agents scans list',
            'kali-agents report <scan-id> --format pdf'
        ]
    },
    'web_assessment': {
        'title': 'Web Application Assessment',
        'description': 'Comprehensive web application security scan',
        'commands': [
            'kali-agents scan web --target https://example.com',
            'kali-agents scan vuln --target example.com',
            'kali-agents report --template executive <scan-id>'
        ]
    }
}

def show_examples():
    """Show interactive examples."""
    console.print("[bold]Examples and Tutorials[/bold]\n")

    for key, example in EXAMPLES.items():
        console.print(f"[cyan]{example['title']}[/cyan]")
        console.print(example['description'])
        console.print()

        for cmd in example['commands']:
            syntax = Syntax(cmd, "bash", theme="monokai")
            console.print(syntax)

        console.print()
```

### Acceptance Criteria
- [ ] Contextual help for all commands
- [ ] Built-in examples
- [ ] Interactive tutorials
- [ ] Command suggestions
- [ ] Error recovery hints

**Effort Estimate**: 3-4 days

---

## 4. Progress Visualization

### Implementation Details

**File**: `src/cli/visualization.py`

```python
"""CLI visualization tools."""

from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.columns import Columns

console = Console()

def display_scan_tree(scan_results):
    """Display scan results as tree."""
    tree = Tree(f"[bold]Scan Results: {scan_results['target']}[/bold]")

    # Network findings
    network = tree.add("[cyan]Network[/cyan]")
    for port in scan_results.get('ports', []):
        network.add(f"Port {port['port']}: {port['service']}")

    # Vulnerabilities
    vulns = tree.add("[red]Vulnerabilities[/red]")
    for vuln in scan_results.get('vulnerabilities', []):
        vulns.add(f"{vuln['severity']}: {vuln['title']}")

    console.print(tree)

def display_comparison(scan1, scan2):
    """Display scan comparison."""
    columns = Columns([
        Panel(render_scan(scan1), title="Scan 1"),
        Panel(render_scan(scan2), title="Scan 2")
    ])
    console.print(columns)
```

### Acceptance Criteria
- [ ] Rich visualizations
- [ ] Tree views for results
- [ ] Progress bars
- [ ] Color-coded outputs
- [ ] ASCII charts

**Effort Estimate**: 2-3 days

---

## 5. Onboarding Experience

### Implementation Details

**File**: `src/cli/onboarding.py`

```python
"""First-time user onboarding."""

from rich.console import Console
from rich.panel import Panel

console = Console()

async def run_onboarding():
    """Run first-time user onboarding."""
    console.print(Panel.fit(
        """
[bold blue]Welcome to Kali Agents MCP![/bold blue]

A multi-agent cybersecurity platform powered by AI.

This wizard will help you get started.
        """,
        border_style="blue"
    ))

    # Check system requirements
    console.print("\n[cyan]Checking system requirements...[/cyan]")
    await check_requirements()

    # Run configuration wizard
    console.print("\n[cyan]Setting up configuration...[/cyan]")
    from src.cli.wizard import run_configuration_wizard
    await run_configuration_wizard()

    # Run test scan
    console.print("\n[cyan]Running test scan...[/cyan]")
    await run_test_scan()

    console.print(
        Panel.fit(
            """
[green]✓ Setup complete![/green]

Next steps:
• View documentation: kali-agents docs
• Run your first scan: kali-agents scan scanme.nmap.org
• Explore examples: kali-agents examples

Need help? Run: kali-agents help
            """,
            border_style="green"
        )
    )
```

### Acceptance Criteria
- [ ] First-run wizard
- [ ] System requirements check
- [ ] Guided setup
- [ ] Test scan
- [ ] Quick start guide

**Effort Estimate**: 2-3 days

---

## Related Issues

- GitHub issues with label `ux` or `ui`
- Milestone: Phase 3 - User Experience

---

## Success Metrics

### Usability Metrics
- [ ] Setup time < 5 minutes
- [ ] Error resolution rate > 90%
- [ ] User satisfaction score > 4/5
- [ ] Documentation clarity score > 4/5

### Adoption Metrics
- [ ] First scan completion rate > 80%
- [ ] Return user rate > 60%
- [ ] Feature discovery rate > 70%

**Total Effort Estimate**: 3-4 weeks
