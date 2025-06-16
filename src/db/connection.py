from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Sequence

from src.config.settings import DATABASE_CONFIG

DB_PATH = Path(DATABASE_CONFIG["path"])


def init_db(schema_sql: str) -> None:
    """Initialize the SQLite database using the provided schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema_sql)
        conn.commit()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Context manager yielding a SQLite connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def execute_query(
    query: str,
    params: Sequence[Any] | None = None,
    *,
    fetch_one: bool = False,
    fetch_all: bool = False,
) -> Any:
    """Execute a SQL query with optional fetching of results."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, params or [])
        if fetch_one:
            row = cur.fetchone()
            return dict(row) if row else None
        if fetch_all:
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        conn.commit()
        return cur.lastrowid
