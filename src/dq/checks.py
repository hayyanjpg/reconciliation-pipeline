from __future__ import annotations

import re
import sqlite3
from datetime import date
from pathlib import Path

from .config import AMOUNT_TOLERANCE, FRESHNESS_DAYS, LATE_PAYMENT_DAYS, SQL_DIR

HEADER_RE = re.compile(
    r"^--\s*(name|category|severity|table|description)\s*:\s*(.+)$", re.IGNORECASE
)


def parse_check_file(path: Path) -> dict:
    meta: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        match = HEADER_RE.match(stripped)
        if match:
            meta[match.group(1).lower()] = match.group(2).strip()
            continue
        if stripped and not stripped.startswith("--"):
            break
    return meta


def _table_totals(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def run_checks(conn: sqlite3.Connection, as_of: date) -> list[dict]:
    params = {
        "as_of": as_of.isoformat(),
        "tolerance": AMOUNT_TOLERANCE,
        "freshness_days": FRESHNESS_DAYS,
        "late_payment_days": LATE_PAYMENT_DAYS,
        "start_date": as_of.replace(day=1).isoformat(),
        "end_date": as_of.isoformat(),
        "channel": "ALL",
    }

    totals: dict[str, int] = {}
    results: list[dict] = []

    for path in sorted((SQL_DIR / "checks").glob("*.sql")):
        meta = parse_check_file(path)
        if not meta.get("name"):
            continue

        table = meta.get("table", "orders")
        if table not in totals:
            totals[table] = _table_totals(conn, table)

        try:
            cursor = conn.execute(path.read_text(encoding="utf-8"), params)
            rows = cursor.fetchall()
            columns = [item[0] for item in cursor.description] if cursor.description else []
        except sqlite3.Error as exc:
            results.append(
                {
                    **meta,
                    "failed_rows": None,
                    "total_rows": totals[table],
                    "status": "ERROR",
                    "error": str(exc),
                    "sample": [],
                }
            )
            continue

        failed_rows = len(rows)
        results.append(
            {
                **meta,
                "failed_rows": failed_rows,
                "total_rows": totals[table],
                "status": "FAIL" if failed_rows else "PASS",
                "error": None,
                "sample": [dict(zip(columns, row)) for row in rows[:3]],
            }
        )

    return results
