# Features and Functionality

**Status**: MEDIUM-HIGH PRIORITY - Expands capabilities

**Target Timeline**: Weeks 9-16 (Phase 3)

---

## Overview

Expand core functionality with new features, enhanced capabilities, and improved user experience.

### Priority: MEDIUM-HIGH
**Effort**: High (6-8 weeks)
**Impact**: User value, competitive advantage, market differentiation

### Current State

```
Feature Status:
✅ Basic network scanning
✅ Basic web scanning
✅ ML-based orchestration
✅ CLI interface
❌ Advanced scanning features
❌ Real-time progress monitoring
❌ Scan scheduling
❌ WebSocket support
❌ Plugin system
❌ Advanced reporting
```

---

## 1. Real-time Scan Progress

### Current State

Scans run to completion without progress updates. Users don't know what's happening.

### Implementation Details

#### 1.1 WebSocket Support

**File**: `src/api/websockets.py`

```python
"""WebSocket support for real-time updates."""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json

class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, scan_id: str, websocket: WebSocket):
        """Connect client to scan updates."""
        await websocket.accept()
        if scan_id not in self.active_connections:
            self.active_connections[scan_id] = set()
        self.active_connections[scan_id].add(websocket)

    def disconnect(self, scan_id: str, websocket: WebSocket):
        """Disconnect client."""
        if scan_id in self.active_connections:
            self.active_connections[scan_id].discard(websocket)
            if not self.active_connections[scan_id]:
                del self.active_connections[scan_id]

    async def send_progress(self, scan_id: str, message: dict):
        """Send progress update to all connected clients."""
        if scan_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[scan_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.add(connection)

            # Clean up dead connections
            for conn in dead_connections:
                self.disconnect(scan_id, conn)

manager = ConnectionManager()

@router.websocket("/ws/scan/{scan_id}")
async def websocket_scan_progress(websocket: WebSocket, scan_id: str):
    """WebSocket endpoint for scan progress."""
    await manager.connect(scan_id, websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(scan_id, websocket)
```

#### 1.2 Progress Tracking in Agents

**File**: `src/agents/base.py`

```python
"""Base agent with progress tracking."""

from typing import Optional, Callable, Dict, Any
from enum import Enum

class ScanStatus(str, Enum):
    """Scan status enum."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BaseAgent:
    """Base agent with progress tracking."""

    def __init__(self, name: str):
        self.name = name
        self.progress_callback: Optional[Callable] = None

    async def emit_progress(
        self,
        scan_id: str,
        status: ScanStatus,
        progress: float,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Emit progress update."""
        event = {
            "scan_id": scan_id,
            "agent": self.name,
            "status": status.value,
            "progress": progress,  # 0.0 to 1.0
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }

        if self.progress_callback:
            await self.progress_callback(event)

        # Also send via WebSocket
        from src.api.websockets import manager
        await manager.send_progress(scan_id, event)

    async def scan(self, target: str, scan_id: str, **options):
        """Execute scan with progress tracking."""
        await self.emit_progress(
            scan_id,
            ScanStatus.RUNNING,
            0.0,
            f"Starting {self.name} scan"
        )

        try:
            # Scan logic here
            await self.emit_progress(
                scan_id,
                ScanStatus.RUNNING,
                0.5,
                "Scan in progress..."
            )

            # Complete
            await self.emit_progress(
                scan_id,
                ScanStatus.COMPLETED,
                1.0,
                "Scan completed"
            )

        except Exception as e:
            await self.emit_progress(
                scan_id,
                ScanStatus.FAILED,
                1.0,
                f"Scan failed: {str(e)}"
            )
            raise
```

#### 1.3 CLI Progress Display

**File**: `src/cli/progress.py`

```python
"""CLI progress display using Rich."""

from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn
)
from rich.live import Live
from rich.table import Table
import asyncio

class ScanProgressDisplay:
    """Display scan progress in CLI."""

    def __init__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
        )
        self.tasks = {}
        self.table = Table(show_header=True)
        self.table.add_column("Agent")
        self.table.add_column("Status")
        self.table.add_column("Progress")

    async def start_agent(self, agent_name: str):
        """Start tracking agent progress."""
        task_id = self.progress.add_task(
            f"[cyan]{agent_name}",
            total=100
        )
        self.tasks[agent_name] = task_id

    async def update_progress(self, event: dict):
        """Update progress from event."""
        agent = event["agent"]
        progress = event["progress"] * 100

        if agent in self.tasks:
            self.progress.update(
                self.tasks[agent],
                completed=progress,
                description=f"[cyan]{agent}: {event['message']}"
            )

    async def display(self):
        """Display progress."""
        with Live(self.progress, refresh_per_second=10):
            # Progress updates happen via update_progress()
            await asyncio.sleep(0)
```

### Acceptance Criteria
- [ ] WebSocket endpoint for real-time updates
- [ ] Progress tracking in all agents
- [ ] CLI progress bars using Rich
- [ ] Web UI progress indicators
- [ ] Progress events logged

**Effort Estimate**: 1 week

---

## 2. Scan Scheduling and Automation

### Implementation Details

#### 2.1 Background Task Queue

**File**: `src/tasks/scheduler.py`

```python
"""Task scheduling using Celery."""

from celery import Celery
from celery.schedules import crontab
from datetime import datetime
from typing import Dict, Any

celery_app = Celery(
    'kali_agents',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.beat_schedule = {
    'scheduled-scan-daily': {
        'task': 'src.tasks.scheduler.scheduled_scan',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
        'args': (),
    },
}

@celery_app.task(bind=True, max_retries=3)
def execute_scan(self, target: str, scan_type: str, options: Dict[str, Any]):
    """Execute scan in background."""
    from src.agents.supervisor import SupervisorAgent

    try:
        supervisor = SupervisorAgent()
        result = asyncio.run(
            supervisor.orchestrate_scan(
                {"host": target},
                scan_type=scan_type,
                **options
            )
        )
        return result
    except Exception as e:
        # Retry on failure
        self.retry(exc=e, countdown=60)

@celery_app.task
def scheduled_scan():
    """Execute scheduled scans."""
    from src.db.models import ScheduledScan

    # Get all active scheduled scans
    scans = ScheduledScan.query.filter_by(active=True).all()

    for scan in scans:
        if scan.should_run():
            execute_scan.delay(
                target=scan.target,
                scan_type=scan.scan_type,
                options=scan.options
            )
            scan.last_run = datetime.utcnow()
            scan.save()
```

#### 2.2 Scheduled Scan Management

**File**: `src/api/routers/schedules.py`

```python
"""Scheduled scan management API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/schedules", tags=["schedules"])

class ScheduleCreate(BaseModel):
    """Create scheduled scan."""
    name: str
    target: str
    scan_type: str
    cron_expression: str
    options: Optional[Dict[str, Any]] = None
    active: bool = True

class ScheduleResponse(BaseModel):
    """Scheduled scan response."""
    id: str
    name: str
    target: str
    scan_type: str
    cron_expression: str
    next_run: Optional[datetime]
    last_run: Optional[datetime]
    active: bool

@router.post("/", response_model=ScheduleResponse)
async def create_schedule(schedule: ScheduleCreate):
    """Create new scheduled scan."""
    # Validate cron expression
    try:
        from croniter import croniter
        croniter(schedule.cron_expression)
    except:
        raise HTTPException(400, "Invalid cron expression")

    # Create schedule
    db_schedule = ScheduledScan(**schedule.dict())
    db_schedule.save()

    return db_schedule

@router.get("/", response_model=List[ScheduleResponse])
async def list_schedules():
    """List all scheduled scans."""
    return ScheduledScan.query.all()

@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """Delete scheduled scan."""
    schedule = ScheduledScan.query.get(schedule_id)
    if not schedule:
        raise HTTPException(404, "Schedule not found")

    schedule.delete()
    return {"status": "deleted"}

@router.post("/{schedule_id}/run")
async def trigger_schedule(schedule_id: str):
    """Manually trigger scheduled scan."""
    schedule = ScheduledScan.query.get(schedule_id)
    if not schedule:
        raise HTTPException(404, "Schedule not found")

    from src.tasks.scheduler import execute_scan
    task = execute_scan.delay(
        target=schedule.target,
        scan_type=schedule.scan_type,
        options=schedule.options
    )

    return {"task_id": task.id, "status": "queued"}
```

#### 2.3 CLI Scheduling

**File**: `src/cli/commands/schedule.py`

```python
"""CLI commands for scheduling."""

import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
def schedule():
    """Manage scheduled scans."""
    pass

@schedule.command()
@click.option('--name', required=True, help='Schedule name')
@click.option('--target', required=True, help='Target to scan')
@click.option('--cron', required=True, help='Cron expression')
@click.option('--type', 'scan_type', default='comprehensive', help='Scan type')
def create(name: str, target: str, cron: str, scan_type: str):
    """Create scheduled scan."""
    # API call to create schedule
    console.print(f"[green]✓[/green] Created schedule: {name}")

@schedule.command()
def list():
    """List scheduled scans."""
    # API call to list schedules
    table = Table(title="Scheduled Scans")
    table.add_column("Name")
    table.add_column("Target")
    table.add_column("Schedule")
    table.add_column("Next Run")
    table.add_column("Status")

    # Add rows...
    console.print(table)

@schedule.command()
@click.argument('schedule_id')
def delete(schedule_id: str):
    """Delete scheduled scan."""
    # API call to delete
    console.print(f"[red]✗[/red] Deleted schedule: {schedule_id}")
```

### Acceptance Criteria
- [ ] Celery task queue configured
- [ ] Scheduled scan API endpoints
- [ ] Cron expression support
- [ ] CLI schedule management
- [ ] Background task monitoring

**Effort Estimate**: 1.5 weeks

---

## 3. Plugin System

### Implementation Details

#### 3.1 Plugin Architecture

**File**: `src/plugins/base.py`

```python
"""Plugin system base."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class PluginMetadata(BaseModel):
    """Plugin metadata."""
    name: str
    version: str
    author: str
    description: str
    dependencies: List[str] = []

class Plugin(ABC):
    """Base plugin class."""

    def __init__(self):
        self.metadata: Optional[PluginMetadata] = None

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize plugin."""
        pass

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass

class ScanPlugin(Plugin):
    """Base class for scan plugins."""

    @abstractmethod
    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scan."""
        pass

class ReportPlugin(Plugin):
    """Base class for report plugins."""

    @abstractmethod
    async def generate_report(self, data: Dict[str, Any]) -> str:
        """Generate report."""
        pass
```

#### 3.2 Plugin Manager

**File**: `src/plugins/manager.py`

```python
"""Plugin manager."""

import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Type
from .base import Plugin, PluginMetadata

class PluginManager:
    """Manage plugins."""

    def __init__(self, plugin_dir: Path = Path("plugins")):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_classes: Dict[str, Type[Plugin]] = {}

    def discover_plugins(self) -> List[PluginMetadata]:
        """Discover available plugins."""
        plugins = []

        if not self.plugin_dir.exists():
            return plugins

        # Scan plugin directory
        for _, name, is_pkg in pkgutil.iter_modules([str(self.plugin_dir)]):
            if is_pkg:
                try:
                    module = importlib.import_module(f"plugins.{name}")
                    if hasattr(module, 'metadata'):
                        plugins.append(module.metadata)
                except Exception as e:
                    print(f"Error loading plugin {name}: {e}")

        return plugins

    async def load_plugin(self, name: str) -> Plugin:
        """Load and initialize plugin."""
        if name in self.plugins:
            return self.plugins[name]

        try:
            # Import plugin module
            module = importlib.import_module(f"plugins.{name}")

            # Get plugin class
            plugin_class = getattr(module, 'Plugin')

            # Instantiate and initialize
            plugin = plugin_class()
            await plugin.initialize()

            self.plugins[name] = plugin
            return plugin

        except Exception as e:
            raise RuntimeError(f"Failed to load plugin {name}: {e}")

    async def execute_plugin(
        self,
        name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute plugin."""
        plugin = await self.load_plugin(name)
        return await plugin.execute(context)

    async def unload_plugin(self, name: str) -> None:
        """Unload plugin."""
        if name in self.plugins:
            await self.plugins[name].cleanup()
            del self.plugins[name]

# Global plugin manager
plugin_manager = PluginManager()
```

#### 3.3 Example Plugin

**File**: `plugins/custom_scanner/plugin.py`

```python
"""Example custom scanner plugin."""

from src.plugins.base import ScanPlugin, PluginMetadata
from typing import Dict, Any

metadata = PluginMetadata(
    name="custom_scanner",
    version="1.0.0",
    author="Security Team",
    description="Custom security scanner"
)

class Plugin(ScanPlugin):
    """Custom scanner plugin."""

    def __init__(self):
        super().__init__()
        self.metadata = metadata

    async def initialize(self):
        """Initialize plugin."""
        print("Custom scanner initialized")

    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom scan."""
        # Custom scan logic
        return {
            "target": target,
            "findings": [],
            "status": "completed"
        }

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin."""
        return await self.scan(
            context.get("target", ""),
            context.get("options", {})
        )

    async def cleanup(self):
        """Cleanup resources."""
        print("Custom scanner cleaned up")
```

#### 3.4 Plugin API

**File**: `src/api/routers/plugins.py`

```python
"""Plugin management API."""

from fastapi import APIRouter, HTTPException
from typing import List
from src.plugins.manager import plugin_manager
from src.plugins.base import PluginMetadata

router = APIRouter(prefix="/plugins", tags=["plugins"])

@router.get("/", response_model=List[PluginMetadata])
async def list_plugins():
    """List available plugins."""
    return plugin_manager.discover_plugins()

@router.post("/{plugin_name}/load")
async def load_plugin(plugin_name: str):
    """Load plugin."""
    try:
        plugin = await plugin_manager.load_plugin(plugin_name)
        return {"status": "loaded", "metadata": plugin.metadata}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/{plugin_name}/execute")
async def execute_plugin(plugin_name: str, context: dict):
    """Execute plugin."""
    try:
        result = await plugin_manager.execute_plugin(plugin_name, context)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/{plugin_name}/unload")
async def unload_plugin(plugin_name: str):
    """Unload plugin."""
    await plugin_manager.unload_plugin(plugin_name)
    return {"status": "unloaded"}
```

### Acceptance Criteria
- [ ] Plugin base classes defined
- [ ] Plugin manager implemented
- [ ] Plugin discovery works
- [ ] Example plugins created
- [ ] Plugin API functional
- [ ] Plugin documentation

**Effort Estimate**: 2 weeks

---

## 4. Advanced Reporting

### Implementation Details

#### 4.1 Report Templates

**File**: `src/reporting/templates/executive.py`

```python
"""Executive report template."""

from typing import Dict, Any, List
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

class ExecutiveReportTemplate:
    """Professional executive report."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.styles = getSampleStyleSheet()

    def generate_pdf(self, output_path: str) -> str:
        """Generate PDF report."""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []

        # Title page
        story.extend(self._generate_title_page())

        # Executive summary
        story.extend(self._generate_executive_summary())

        # Findings summary
        story.extend(self._generate_findings_summary())

        # Detailed findings
        story.extend(self._generate_detailed_findings())

        # Recommendations
        story.extend(self._generate_recommendations())

        # Build PDF
        doc.build(story)
        return output_path

    def _generate_title_page(self) -> List:
        """Generate title page."""
        elements = []

        # Title
        title = Paragraph(
            "Security Assessment Report",
            self.styles['Title']
        )
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Client info
        client_info = f"""
        <b>Client:</b> {self.data.get('client', 'N/A')}<br/>
        <b>Assessment Date:</b> {self.data.get('date', datetime.now().strftime('%Y-%m-%d'))}<br/>
        <b>Assessor:</b> Kali Agents MCP
        """
        elements.append(Paragraph(client_info, self.styles['Normal']))

        return elements

    def _generate_executive_summary(self) -> List:
        """Generate LLM-powered executive summary."""
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate

        # Use LLM to generate summary
        prompt = PromptTemplate(
            input_variables=["findings"],
            template="""
            Generate a professional executive summary for a security assessment
            with the following findings:

            {findings}

            The summary should be 2-3 paragraphs, highlighting the most critical
            issues and overall security posture.
            """
        )

        # Generate summary
        summary = "Executive summary here..."

        return [
            Paragraph("Executive Summary", self.styles['Heading1']),
            Paragraph(summary, self.styles['Normal']),
            Spacer(1, 12)
        ]

    def _generate_findings_summary(self) -> List:
        """Generate findings summary table."""
        # Implementation
        pass

    def _generate_detailed_findings(self) -> List:
        """Generate detailed findings."""
        # Implementation
        pass

    def _generate_recommendations(self) -> List:
        """Generate recommendations."""
        # Implementation
        pass
```

#### 4.2 Report Customization

**File**: `src/reporting/customizer.py`

```python
"""Report customization engine."""

from typing import Dict, Any
from jinja2 import Template

class ReportCustomizer:
    """Customize report appearance and content."""

    def __init__(self):
        self.custom_sections = {}
        self.branding = {}

    def add_custom_section(
        self,
        name: str,
        template: str,
        position: str = "end"
    ):
        """Add custom section to report."""
        self.custom_sections[name] = {
            "template": Template(template),
            "position": position
        }

    def set_branding(
        self,
        logo_path: str,
        company_name: str,
        colors: Dict[str, str]
    ):
        """Set custom branding."""
        self.branding = {
            "logo": logo_path,
            "company": company_name,
            "colors": colors
        }

    def apply_customizations(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply customizations to report data."""
        # Add custom sections
        for name, section in self.custom_sections.items():
            rendered = section["template"].render(**report_data)
            report_data["custom_sections"] = report_data.get("custom_sections", {})
            report_data["custom_sections"][name] = rendered

        # Apply branding
        report_data["branding"] = self.branding

        return report_data
```

### Acceptance Criteria
- [ ] Multiple report templates
- [ ] LLM-generated summaries
- [ ] Custom section support
- [ ] Branding customization
- [ ] Charts and graphs
- [ ] Multi-format export

**Effort Estimate**: 2 weeks

---

## 5. Scan Comparison and Trending

### Implementation Details

**File**: `src/analysis/comparison.py`

```python
"""Scan comparison and trending analysis."""

from typing import List, Dict, Any
from datetime import datetime, timedelta

class ScanComparator:
    """Compare scans and identify trends."""

    async def compare_scans(
        self,
        scan_id_1: str,
        scan_id_2: str
    ) -> Dict[str, Any]:
        """Compare two scans."""
        scan1 = await self.get_scan(scan_id_1)
        scan2 = await self.get_scan(scan_id_2)

        comparison = {
            "added_vulnerabilities": [],
            "removed_vulnerabilities": [],
            "changed_ports": [],
            "risk_score_delta": 0.0,
            "summary": ""
        }

        # Compare vulnerabilities
        vulns1 = set(v["id"] for v in scan1.get("vulnerabilities", []))
        vulns2 = set(v["id"] for v in scan2.get("vulnerabilities", []))

        comparison["added_vulnerabilities"] = list(vulns2 - vulns1)
        comparison["removed_vulnerabilities"] = list(vulns1 - vulns2)

        # Compare ports
        # ... implementation

        return comparison

    async def analyze_trends(
        self,
        target: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Analyze security trends over time."""
        # Get scans for target over time period
        scans = await self.get_scans_for_target(
            target,
            start_date=datetime.now() - timedelta(days=days)
        )

        trends = {
            "vulnerability_trend": [],
            "risk_score_trend": [],
            "port_changes": [],
            "recommendations": []
        }

        # Analyze trends
        for scan in scans:
            trends["vulnerability_trend"].append({
                "date": scan["timestamp"],
                "count": len(scan.get("vulnerabilities", []))
            })

        return trends
```

### Acceptance Criteria
- [ ] Scan comparison functionality
- [ ] Trend analysis
- [ ] Visual charts
- [ ] Automated insights
- [ ] Email alerts for changes

**Effort Estimate**: 1 week

---

## Related Issues

- GitHub issues with label `feature` or `enhancement`
- Milestone: Phase 3 - Features

---

## Success Metrics

### Feature Adoption
- [ ] Real-time progress used in 80% of scans
- [ ] 10+ scheduled scans configured
- [ ] 5+ plugins created by community
- [ ] Advanced reports generated

### User Satisfaction
- [ ] Positive feedback on new features
- [ ] Feature requests addressed
- [ ] Documentation complete

**Total Effort Estimate**: 6-8 weeks
