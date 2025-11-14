# Maintenance and Operations

**Status**: ONGOING - Continuous improvement

**Target Timeline**: Ongoing / All Phases

---

## Overview

Establish processes and automation for long-term maintenance, monitoring, and operational excellence.

### Priority: MEDIUM (Ongoing)
**Effort**: Low-Medium (ongoing)
**Impact**: Long-term sustainability, reliability, security

### Current State

```
Operations Status:
✅ Basic CI/CD
✅ Security scanning
❌ No monitoring dashboard
❌ No alerting system
❌ No backup strategy
❌ No disaster recovery
❌ No runbook documentation
❌ Limited logging
```

---

## 1. Monitoring and Alerting

### Implementation Details

#### 1.1 Health Monitoring

**File**: `src/monitoring/health.py`

```python
"""Comprehensive health monitoring."""

from typing import Dict, Any
from datetime import datetime
import psutil

class HealthMonitor:
    """Monitor system health."""

    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "checks": {
                "api": await self.check_api(),
                "database": await self.check_database(),
                "redis": await self.check_redis(),
                "mcp_servers": await self.check_mcp_servers(),
                "disk": self.check_disk(),
                "memory": self.check_memory(),
                "cpu": self.check_cpu()
            }
        }

    async def check_api(self) -> Dict[str, Any]:
        """Check API health."""
        return {
            "status": "up",
            "response_time_ms": 12.3,
            "requests_per_minute": 150
        }

    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            # Check connection
            # Check query performance
            return {
                "status": "up",
                "connection_pool": "80% utilized",
                "query_time_ms": 8.5
            }
        except Exception as e:
            return {"status": "down", "error": str(e)}

    def check_disk(self) -> Dict[str, Any]:
        """Check disk usage."""
        usage = psutil.disk_usage('/')
        return {
            "status": "ok" if usage.percent < 90 else "warning",
            "used_percent": usage.percent,
            "free_gb": usage.free / (1024**3)
        }

    def check_memory(self) -> Dict[str, Any]:
        """Check memory usage."""
        mem = psutil.virtual_memory()
        return {
            "status": "ok" if mem.percent < 90 else "warning",
            "used_percent": mem.percent,
            "available_gb": mem.available / (1024**3)
        }

    def check_cpu(self) -> Dict[str, Any]:
        """Check CPU usage."""
        cpu_percent = psutil.cpu_percent(interval=1)
        return {
            "status": "ok" if cpu_percent < 80 else "warning",
            "usage_percent": cpu_percent,
            "load_average": psutil.getloadavg()
        }
```

#### 1.2 Alerting System

**File**: `src/monitoring/alerts.py`

```python
"""Alerting system for critical events."""

from enum import Enum
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertManager:
    """Manage alerts and notifications."""

    def __init__(self):
        self.handlers = []

    async def send_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        details: Optional[dict] = None
    ):
        """Send alert through all configured handlers."""
        alert = {
            "severity": severity,
            "title": title,
            "message": message,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }

        for handler in self.handlers:
            await handler.send(alert)

class EmailAlertHandler:
    """Send alerts via email."""

    def __init__(self, smtp_config: dict):
        self.smtp_config = smtp_config

    async def send(self, alert: dict):
        """Send email alert."""
        msg = MIMEText(f"""
Severity: {alert['severity']}
Title: {alert['title']}

{alert['message']}

Details: {alert['details']}

Timestamp: {alert['timestamp']}
        """)

        msg['Subject'] = f"[{alert['severity'].upper()}] {alert['title']}"
        msg['From'] = self.smtp_config['from']
        msg['To'] = self.smtp_config['to']

        # Send email
        # Implementation...

class SlackAlertHandler:
    """Send alerts to Slack."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, alert: dict):
        """Send Slack alert."""
        import httpx

        color_map = {
            "info": "#36a64f",
            "warning": "#ff9800",
            "error": "#f44336",
            "critical": "#d32f2f"
        }

        payload = {
            "attachments": [{
                "color": color_map[alert['severity']],
                "title": alert['title'],
                "text": alert['message'],
                "fields": [
                    {"title": "Severity", "value": alert['severity'].upper()},
                    {"title": "Timestamp", "value": alert['timestamp']}
                ]
            }]
        }

        async with httpx.AsyncClient() as client:
            await client.post(self.webhook_url, json=payload)
```

#### 1.3 Monitoring Dashboard

**File**: `grafana/dashboards/kali-agents.json`

```json
{
  "dashboard": {
    "title": "Kali Agents MCP",
    "panels": [
      {
        "title": "Active Scans",
        "targets": [
          {
            "expr": "kali_agents_active_scans"
          }
        ]
      },
      {
        "title": "Scan Success Rate",
        "targets": [
          {
            "expr": "rate(kali_agents_scans_total{status=\"success\"}[5m])"
          }
        ]
      },
      {
        "title": "API Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(kali_agents_errors_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### Acceptance Criteria
- [ ] Health checks implemented
- [ ] Alert system functional
- [ ] Email/Slack notifications
- [ ] Grafana dashboard
- [ ] PagerDuty integration

**Effort Estimate**: 1 week

---

## 2. Backup and Recovery

### Implementation Details

#### 2.1 Database Backups

**File**: `scripts/backup_database.sh`

```bash
#!/bin/bash
set -e

BACKUP_DIR="/backups/database"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="kali_agents"

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump $DB_NAME | gzip > "$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
if [ ! -z "$AWS_S3_BUCKET" ]; then
    aws s3 cp "$BACKUP_DIR/backup_$TIMESTAMP.sql.gz" \
        "s3://$AWS_S3_BUCKET/backups/database/"
fi

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
```

#### 2.2 Backup Automation

**File**: `.github/workflows/backup.yml`

```yaml
name: Automated Backups

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Backup Database
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          ./scripts/backup_database.sh

      - name: Verify Backup
        run: |
          ./scripts/verify_backup.sh

      - name: Upload to Artifact
        uses: actions/upload-artifact@v4
        with:
          name: database-backup
          path: /backups/database/
          retention-days: 30
```

#### 2.3 Disaster Recovery

**File**: `docs/operations/disaster-recovery.md`

```markdown
# Disaster Recovery Plan

## Recovery Time Objective (RTO)
- **Critical Services**: 1 hour
- **Non-critical Services**: 4 hours

## Recovery Point Objective (RPO)
- **Database**: 24 hours (daily backups)
- **Configuration**: 0 (version controlled)

## Recovery Procedures

### Database Recovery
```bash
# Download latest backup
aws s3 cp s3://bucket/backups/database/latest.sql.gz .

# Restore database
gunzip latest.sql.gz
psql kali_agents < latest.sql
```

### Full System Recovery
```bash
# 1. Provision infrastructure
terraform apply

# 2. Deploy application
kubectl apply -f k8s/

# 3. Restore database
./scripts/restore_database.sh

# 4. Verify health
curl https://api.kali-agents.com/health
```

## Testing
- Monthly disaster recovery drills
- Automated backup verification
- Recovery time tracking
```

### Acceptance Criteria
- [ ] Automated daily backups
- [ ] Backup verification
- [ ] S3/cloud storage integration
- [ ] Recovery procedures documented
- [ ] Regular DR testing

**Effort Estimate**: 3-4 days

---

## 3. Log Management

### Implementation Details

#### 3.1 Centralized Logging

**File**: `src/logging/config.py`

```python
"""Centralized logging configuration."""

import logging
import logging.handlers
from pathlib import Path

def setup_logging(
    log_dir: Path = Path("logs"),
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 10
):
    """Configure centralized logging."""

    log_dir.mkdir(exist_ok=True)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    root_logger.addHandler(console_handler)

    # File handlers with rotation
    handlers = {
        'app': log_dir / 'app.log',
        'security': log_dir / 'security.log',
        'audit': log_dir / 'audit.log',
        'errors': log_dir / 'errors.log'
    }

    for name, log_file in handlers.items():
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        if name == 'errors':
            handler.setLevel(logging.ERROR)

        root_logger.addHandler(handler)
```

#### 2 Log Aggregation

**File**: `promtail.yml`

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: kali-agents
    static_configs:
      - targets:
          - localhost
        labels:
          job: kali-agents
          __path__: /var/log/kali-agents/*.log
```

### Acceptance Criteria
- [ ] Centralized logging
- [ ] Log rotation configured
- [ ] Loki/Elasticsearch integration
- [ ] Log retention policy
- [ ] Log analysis tools

**Effort Estimate**: 2-3 days

---

## 4. Maintenance Automation

### Implementation Details

#### 4.1 Automated Cleanup

**File**: `scripts/cleanup.sh`

```bash
#!/bin/bash
# Automated cleanup script

# Remove old scan data (>90 days)
psql -c "DELETE FROM scans WHERE timestamp < NOW() - INTERVAL '90 days'"

# Clean old logs
find /var/log/kali-agents -name "*.log.*" -mtime +30 -delete

# Clean Docker images
docker image prune -a --filter "until=168h" -f

# Clean cache
redis-cli FLUSHDB

echo "Cleanup completed"
```

#### 4.2 Dependency Updates

**File**: `.github/workflows/dependency-updates.yml`

```yaml
name: Monthly Dependency Updates

on:
  schedule:
    - cron: '0 0 1 * *'  # First day of month
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Update dependencies
        run: |
          pip-compile --upgrade requirements.in
          pip-compile --upgrade requirements-dev.in

      - name: Run tests
        run: |
          pip install -r requirements-dev.txt
          pytest

      - name: Create PR
        uses: peter-evans/create-pull-request@v6
        with:
          title: 'chore: Monthly dependency updates'
          body: 'Automated dependency updates'
          branch: deps/monthly-updates
          labels: dependencies
```

### Acceptance Criteria
- [ ] Automated cleanup scripts
- [ ] Scheduled maintenance tasks
- [ ] Dependency update automation
- [ ] Resource optimization

**Effort Estimate**: 2-3 days

---

## 5. Runbooks and Documentation

### Implementation Details

**File**: `docs/operations/runbooks/incident-response.md`

```markdown
# Incident Response Runbook

## High CPU Usage

### Symptoms
- CPU usage > 80% for 5+ minutes
- Slow API responses
- Alert: "High CPU Usage"

### Investigation
```bash
# Check top processes
top -c

# Check specific service
systemctl status kali-agents

# View logs
tail -f /var/log/kali-agents/app.log
```

### Resolution
1. Identify resource-intensive scans
2. Pause non-critical scans
3. Scale up resources if needed
4. Monitor for improvement

### Prevention
- Implement scan throttling
- Set resource limits
- Enable auto-scaling

## Database Connection Errors

### Symptoms
- "Cannot connect to database" errors
- 500 errors from API
- Alert: "Database Down"

### Investigation
```bash
# Check database status
systemctl status postgresql

# Check connections
psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check logs
tail -f /var/log/postgresql/postgresql.log
```

### Resolution
1. Restart database service
2. Check connection pool settings
3. Verify network connectivity
4. Restore from backup if corrupted

---

More runbooks for common scenarios...
```

**File**: `docs/operations/runbooks/deployment.md`

```markdown
# Deployment Runbook

## Pre-deployment Checklist
- [ ] All tests passing
- [ ] Security scans clean
- [ ] Backup completed
- [ ] Changelog updated
- [ ] Rollback plan ready

## Deployment Steps

### 1. Backup Current State
```bash
./scripts/backup_database.sh
kubectl get all -n kali-agents -o yaml > backup.yaml
```

### 2. Deploy New Version
```bash
# Update image tag
kubectl set image deployment/kali-agents api=kali-agents:v1.2.0

# Watch rollout
kubectl rollout status deployment/kali-agents
```

### 3. Verify Deployment
```bash
# Health check
curl https://api.kali-agents.com/health

# Run smoke tests
./scripts/smoke_test.sh
```

### 4. Monitor
- Watch error rates
- Check response times
- Monitor resource usage

## Rollback Procedure
```bash
# Rollback deployment
kubectl rollout undo deployment/kali-agents

# Verify
kubectl rollout status deployment/kali-agents
```
```

### Acceptance Criteria
- [ ] Runbooks for common incidents
- [ ] Deployment procedures documented
- [ ] Troubleshooting guides
- [ ] On-call playbooks

**Effort Estimate**: 1 week

---

## 6. Performance Monitoring

### Implementation Details

**File**: `scripts/performance_report.py`

```python
"""Generate performance reports."""

from datetime import datetime, timedelta
import psycopg2

def generate_weekly_report():
    """Generate weekly performance report."""

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    report = {
        "period": f"{start_date.date()} to {end_date.date()}",
        "scans": {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "avg_duration": 0
        },
        "performance": {
            "avg_response_time": 0,
            "p95_response_time": 0,
            "error_rate": 0
        },
        "resources": {
            "avg_cpu": 0,
            "avg_memory": 0,
            "peak_concurrent_scans": 0
        }
    }

    # Query metrics from database
    # Generate report

    return report
```

### Acceptance Criteria
- [ ] Performance reports generated
- [ ] Trend analysis
- [ ] Capacity planning data
- [ ] SLA monitoring

**Effort Estimate**: 2-3 days

---

## Related Issues

- GitHub issues with label `operations` or `maintenance`
- Milestone: Ongoing Operations

---

## Success Metrics

### Reliability Metrics
- [ ] Uptime > 99.9%
- [ ] Mean time to recovery < 1 hour
- [ ] Successful backup rate 100%
- [ ] Alert response time < 15 minutes

### Operational Metrics
- [ ] Automated maintenance tasks > 80%
- [ ] Manual interventions < 5/month
- [ ] Documentation coverage > 90%
- [ ] Incident resolution time decreasing

**Total Effort Estimate**: 2-3 weeks (initial) + ongoing
