"""Data MCP Server - handles scan data storage."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import Context, FastMCP
from src.config.settings import DATABASE_CONFIG

mcp = FastMCP("DataServer")
DB_PATH = Path(DATABASE_CONFIG["path"])


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def _init_db() -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                agent TEXT,
                target TEXT,
                scan_type TEXT,
                result TEXT
            )
            """
        )
        conn.commit()


def _dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> Dict[str, Any]:
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


_init_db()


@mcp.tool
async def create_record(
    table: str, data: Dict[str, Any], ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Insert a record into the specified table."""
    keys = ",".join(data.keys())
    placeholders = ",".join("?" for _ in data)
    values = list(data.values())

    with _get_conn() as conn:
        cur = conn.execute(
            f"INSERT INTO {table} ({keys}) VALUES ({placeholders})", values
        )
        conn.commit()
        record_id = cur.lastrowid

    if ctx:
        await ctx.info(f"? Inserted into {table} id {record_id}")
    return {"status": "created", "id": record_id}


@mcp.tool
async def read_records(
    table: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    ctx: Optional[Context] = None,
) -> List[Dict[str, Any]]:
    """Retrieve records from a table with optional filters."""
    query = f"SELECT * FROM {table}"
    params: List[Any] = []
    if filters:
        clauses = [f"{k} = ?" for k in filters]
        params.extend(filters.values())
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    with _get_conn() as conn:
        conn.row_factory = _dict_factory
        cur = conn.execute(query, params)
        rows = cur.fetchall()

    if ctx:
        await ctx.info(f"? Retrieved {len(rows)} rows from {table}")
    return rows


@mcp.tool
async def update_record(
    table: str, record_id: int, data: Dict[str, Any], ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Update a record in the specified table."""
    assignments = ", ".join(f"{k} = ?" for k in data)
    values = list(data.values()) + [record_id]

    with _get_conn() as conn:
        conn.execute(f"UPDATE {table} SET {assignments} WHERE id = ?", values)
        conn.commit()

    if ctx:
        await ctx.info(f"? Updated {table} id {record_id}")
    return {"status": "updated", "id": record_id}


@mcp.tool
async def delete_record(
    table: str, record_id: int, ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Delete a record from a table."""
    with _get_conn() as conn:
        conn.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
        conn.commit()

    if ctx:
        await ctx.info(f"? Deleted from {table} id {record_id}")
    return {"status": "deleted", "id": record_id}


@mcp.tool
async def store_scan_result(
    agent: str,
    target: str,
    scan_type: str,
    result: Dict[str, Any],
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """Store a scan result in the database."""
    data = {
        "agent": agent,
        "target": target,
        "scan_type": scan_type,
        "result": json.dumps(result),
    }
    return await create_record("scan_results", data, ctx)


@mcp.tool
async def get_scan_history(
    target: str, limit: int = 10, ctx: Optional[Context] = None
) -> List[Dict[str, Any]]:
    """Retrieve scan history for a target."""
    records = await read_records("scan_results", {"target": target}, limit, ctx)
    for rec in records:
        if rec.get("result"):
            try:
                rec["result"] = json.loads(rec["result"])
            except json.JSONDecodeError:
                pass
    return records


if __name__ == "__main__":
    mcp.run()
