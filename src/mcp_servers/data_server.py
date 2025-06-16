"""Data MCP Server - handles scan data storage."""

import json
from typing import Any, Dict, List, Optional

from fastmcp import Context, FastMCP
from db.connection import execute_query, init_db

mcp = FastMCP("DataServer")


SCHEMA = """
CREATE TABLE IF NOT EXISTS scan_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    agent TEXT,
    target TEXT,
    scan_type TEXT,
    result TEXT
)
"""

init_db(SCHEMA)


@mcp.tool
async def create_record(
    table: str, data: Dict[str, Any], ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Insert a record into the specified table."""
    keys = ",".join(data.keys())
    placeholders = ",".join("?" for _ in data)
    values = list(data.values())

    record_id = execute_query(
        f"INSERT INTO {table} ({keys}) VALUES ({placeholders})",
        values,
    )

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

    rows = execute_query(query, params, fetch_all=True)

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

    execute_query(
        f"UPDATE {table} SET {assignments} WHERE id = ?",
        values,
    )

    if ctx:
        await ctx.info(f"? Updated {table} id {record_id}")
    return {"status": "updated", "id": record_id}


@mcp.tool
async def delete_record(
    table: str, record_id: int, ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Delete a record from a table."""
    execute_query(
        f"DELETE FROM {table} WHERE id = ?",
        (record_id,),
    )

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
    return await create_record.run("scan_results", data, ctx)


@mcp.tool
async def get_scan_history(
    target: str, limit: int = 10, ctx: Optional[Context] = None
) -> List[Dict[str, Any]]:
    """Retrieve scan history for a target."""
    records = await read_records.run("scan_results", {"target": target}, limit, ctx)
    for rec in records:
        if rec.get("result"):
            try:
                rec["result"] = json.loads(rec["result"])
            except json.JSONDecodeError:
                pass
    return records


if __name__ == "__main__":
    mcp.run()
