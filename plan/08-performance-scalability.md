# Performance and Scalability

**Status**: MEDIUM PRIORITY - Important for growth

**Target Timeline**: Weeks 13-16 (Phase 3)

---

## Overview

Optimize performance and enable horizontal scalability for handling large-scale security assessments.

### Priority: MEDIUM
**Effort**: Medium (3-4 weeks)
**Impact**: Scalability, response times, resource efficiency

### Current State

```
Performance Status:
✅ Basic async operations
✅ Single-server deployment
❌ No performance benchmarks
❌ No horizontal scaling
❌ No caching layer
❌ No load balancing
❌ Database not optimized
❌ No query optimization
```

---

## 1. Database Optimization

### Implementation Details

#### 1.1 Add Database Indexes

**File**: `migrations/add_indexes.sql`

```sql
-- Scans table indexes
CREATE INDEX idx_scans_target ON scans(target);
CREATE INDEX idx_scans_timestamp ON scans(timestamp DESC);
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_scans_target_timestamp ON scans(target, timestamp DESC);

-- Results table indexes
CREATE INDEX idx_results_scan_id ON scan_results(scan_id);
CREATE INDEX idx_results_severity ON scan_results(severity);

-- Vulnerabilities table indexes
CREATE INDEX idx_vulns_scan_id ON vulnerabilities(scan_id);
CREATE INDEX idx_vulns_severity ON vulnerabilities(severity);
CREATE INDEX idx_vulns_cve ON vulnerabilities(cve_id);

-- Composite indexes for common queries
CREATE INDEX idx_scans_target_status_timestamp
    ON scans(target, status, timestamp DESC);
```

#### 1.2 Query Optimization

**File**: `src/db/optimized_queries.py`

```python
"""Optimized database queries."""

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

async def get_recent_scans_optimized(limit: int = 100):
    """Get recent scans with optimized loading."""
    query = (
        select(Scan)
        .options(
            selectinload(Scan.results),
            selectinload(Scan.vulnerabilities)
        )
        .order_by(Scan.timestamp.desc())
        .limit(limit)
    )
    return await session.execute(query)

async def get_scan_summary_optimized(target: str):
    """Get scan summary without loading all data."""
    query = (
        select(
            Scan.id,
            Scan.timestamp,
            Scan.status,
            func.count(Vulnerability.id).label('vuln_count')
        )
        .outerjoin(Vulnerability)
        .where(Scan.target == target)
        .group_by(Scan.id)
        .order_by(Scan.timestamp.desc())
    )
    return await session.execute(query)
```

#### 1.3 Connection Pooling

**File**: `src/db/pool.py`

```python
"""Database connection pooling."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # Connection pool size
    max_overflow=10,        # Max overflow connections
    pool_pre_ping=True,     # Verify connections
    pool_recycle=3600,      # Recycle connections every hour
    echo=False
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

### Acceptance Criteria
- [ ] All indexes created
- [ ] Query performance improved by 50%+
- [ ] Connection pooling configured
- [ ] Database benchmarks documented

**Effort Estimate**: 3-4 days

---

## 2. Caching Layer

### Implementation Details

#### 2.1 Redis Caching

**File**: `src/cache/redis_cache.py`

```python
"""Redis caching implementation."""

import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
from redis.asyncio import Redis

class CacheManager:
    """Manage Redis cache."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = Redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL."""
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )

    async def delete(self, key: str):
        """Delete key from cache."""
        await self.redis.delete(key)

    async def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

cache = CacheManager()

def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching function results."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator

# Usage
@cached(ttl=600, key_prefix="scans")
async def get_scan_results(scan_id: str):
    """Get scan results with caching."""
    # Database query
    pass
```

#### 2.2 Cache Invalidation

**File**: `src/cache/invalidation.py`

```python
"""Cache invalidation strategies."""

from typing import List

class CacheInvalidator:
    """Handle cache invalidation."""

    def __init__(self, cache: CacheManager):
        self.cache = cache

    async def invalidate_scan(self, scan_id: str):
        """Invalidate all cache entries for a scan."""
        patterns = [
            f"scans:get_scan_results:{scan_id}:*",
            f"scans:get_scan_summary:{scan_id}:*",
            f"reports:*:{scan_id}:*"
        ]

        for pattern in patterns:
            await self.cache.clear_pattern(pattern)

    async def invalidate_target(self, target: str):
        """Invalidate all cache entries for a target."""
        await self.cache.clear_pattern(f"*:{target}:*")

# Hook into database updates
async def on_scan_update(scan_id: str):
    """Called when scan is updated."""
    invalidator = CacheInvalidator(cache)
    await invalidator.invalidate_scan(scan_id)
```

### Acceptance Criteria
- [ ] Redis caching implemented
- [ ] Cache decorator working
- [ ] Cache invalidation strategy
- [ ] Cache hit rate > 70%
- [ ] Response time improved

**Effort Estimate**: 3-4 days

---

## 3. Horizontal Scaling

### Implementation Details

#### 3.1 Load Balancer Configuration

**File**: `nginx-lb.conf`

```nginx
upstream api_servers {
    least_conn;  # Use least connections algorithm
    server api1:8000 weight=1 max_fails=3 fail_timeout=30s;
    server api2:8000 weight=1 max_fails=3 fail_timeout=30s;
    server api3:8000 weight=1 max_fails=3 fail_timeout=30s;

    # Health check
    check interval=3000 rise=2 fall=3 timeout=1000;
}

server {
    listen 80;
    server_name api.kali-agents.local;

    location / {
        proxy_pass http://api_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        access_log off;
        proxy_pass http://api_servers/health;
    }
}
```

#### 3.2 Distributed Task Queue

**File**: `src/tasks/distributed.py`

```python
"""Distributed task processing."""

from celery import Celery
from kombu import Queue

celery_app = Celery(
    'kali_agents',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Configure multiple queues
celery_app.conf.task_queues = (
    Queue('scans', routing_key='scans'),
    Queue('reports', routing_key='reports'),
    Queue('priority', routing_key='priority'),
)

# Task routing
celery_app.conf.task_routes = {
    'src.tasks.scans.*': {'queue': 'scans'},
    'src.tasks.reports.*': {'queue': 'reports'},
}

# Worker configuration
celery_app.conf.update(
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
```

#### 3.3 Session Management

**File**: `src/api/session.py`

```python
"""Distributed session management."""

from starlette.middleware.sessions import SessionMiddleware
from redis import Redis
import json

class RedisSessionBackend:
    """Redis-backed session storage."""

    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url)

    async def get(self, session_id: str) -> dict:
        """Get session data."""
        data = self.redis.get(f"session:{session_id}")
        if data:
            return json.loads(data)
        return {}

    async def set(self, session_id: str, data: dict, ttl: int = 3600):
        """Set session data."""
        self.redis.setex(
            f"session:{session_id}",
            ttl,
            json.dumps(data)
        )

    async def delete(self, session_id: str):
        """Delete session."""
        self.redis.delete(f"session:{session_id}")
```

### Acceptance Criteria
- [ ] Load balancer configured
- [ ] Multiple API instances running
- [ ] Distributed task queue working
- [ ] Session management works across instances
- [ ] Health checks functional

**Effort Estimate**: 1 week

---

## 4. Async Optimization

### Implementation Details

**File**: `src/utils/async_helpers.py`

```python
"""Async optimization utilities."""

import asyncio
from typing import List, Callable, Any

async def run_parallel(tasks: List[Callable], max_concurrent: int = 10):
    """Run tasks in parallel with concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded_task(task):
        async with semaphore:
            return await task()

    return await asyncio.gather(*[bounded_task(t) for t in tasks])

async def batch_process(
    items: List[Any],
    processor: Callable,
    batch_size: int = 100
):
    """Process items in batches."""
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = await asyncio.gather(*[processor(item) for item in batch])
        results.extend(batch_results)
    return results
```

### Acceptance Criteria
- [ ] Parallel execution optimized
- [ ] Concurrency limits enforced
- [ ] Resource usage controlled
- [ ] Performance benchmarks met

**Effort Estimate**: 2-3 days

---

## 5. Performance Monitoring

### Implementation Details

**File**: `src/monitoring/performance.py`

```python
"""Performance monitoring."""

from prometheus_client import Histogram, Counter
import time
from functools import wraps

# Metrics
request_duration = Histogram(
    'request_duration_seconds',
    'Request duration',
    ['endpoint', 'method']
)

scan_duration = Histogram(
    'scan_duration_seconds',
    'Scan duration',
    ['scan_type']
)

def monitor_performance(endpoint: str):
    """Decorator to monitor performance."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                request_duration.labels(
                    endpoint=endpoint,
                    method=func.__name__
                ).observe(duration)
        return wrapper
    return decorator
```

### Acceptance Criteria
- [ ] Performance metrics collected
- [ ] Bottlenecks identified
- [ ] Dashboard created
- [ ] Alerts configured

**Effort Estimate**: 3-4 days

---

## Related Issues

- GitHub issues with label `performance` or `scalability`
- Milestone: Phase 3 - Optimization

---

## Success Metrics

### Performance Targets
- [ ] API response time < 100ms (p95)
- [ ] Scan throughput > 100/hour
- [ ] Database query time < 50ms (p95)
- [ ] Cache hit rate > 70%

### Scalability Targets
- [ ] Support 1000+ concurrent scans
- [ ] Horizontal scaling working
- [ ] Linear performance scaling
- [ ] Resource usage optimized

**Total Effort Estimate**: 3-4 weeks
