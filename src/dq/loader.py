from __future__ import annotations

import csv
import io
from pathlib import Path

from .config import ORDER_SOURCES, PAYMENTS_FILE
from .csv_utils import decode_csv, sniff_delimiter
from .schema import ORDER_FIELDS, PAYMENT_FIELDS
from .normalize import (
    normalize_amount,
    normalize_channel,
    normalize_date,
    normalize_id,
    normalize_status,
)


def read_rows(path: Path):
    text, _, _ = decode_csv(Path(path).read_bytes())
    delimiter = sniff_delimiter(text)
    yield from csv.DictReader(io.StringIO(text), delimiter=delimiter)


ORDER_ALIASES = {field["name"]: field["aliases"] for field in ORDER_FIELDS}
PAYMENT_ALIASES = {field["name"]: field["aliases"] for field in PAYMENT_FIELDS}


def _first(row: dict, *keys):
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return None


def _iso(value):
    parsed = normalize_date(value)
    return parsed.isoformat() if parsed else None


def load_orders(raw_dir: Path):
    orders: list[dict] = []
    rejected: list[dict] = []

    for filename, default_channel in ORDER_SOURCES.items():
        path = Path(raw_dir) / filename
        if not path.exists():
            raise FileNotFoundError(f"File sumber tidak ditemukan: {path}")

        for line, row in enumerate(read_rows(path), start=2):
            order_id = normalize_id(_first(row, *ORDER_ALIASES["order_id"]))
            if not order_id:
                rejected.append(
                    {
                        "source_file": filename,
                        "line": line,
                        "reason": "order_id kosong",
                    }
                )
                continue

            raw_date = _first(row, *ORDER_ALIASES["order_date"])
            raw_amount = _first(row, *ORDER_ALIASES["amount"])
            orders.append(
                {
                    "order_id": order_id,
                    "customer_id": normalize_id(
                        _first(row, *ORDER_ALIASES["customer_id"])
                    ),
                    "order_date": _iso(raw_date),
                    "amount": normalize_amount(raw_amount),
                    "status": normalize_status(_first(row, *ORDER_ALIASES["status"])),
                    "channel": normalize_channel(
                        _first(row, *ORDER_ALIASES["channel"]), default_channel
                    ),
                    "source_file": filename,
                    "raw_order_date": raw_date,
                    "raw_amount": raw_amount,
                }
            )

    return orders, rejected


def load_payments(raw_dir: Path):
    path = Path(raw_dir) / PAYMENTS_FILE
    if not path.exists():
        raise FileNotFoundError(f"File sumber tidak ditemukan: {path}")

    payments: list[dict] = []
    rejected: list[dict] = []

    for line, row in enumerate(read_rows(path), start=2):
        payment_id = normalize_id(_first(row, *PAYMENT_ALIASES["payment_id"]))
        order_id = normalize_id(_first(row, *PAYMENT_ALIASES["order_id"]))
        if not payment_id or not order_id:
            rejected.append(
                {
                    "source_file": PAYMENTS_FILE,
                    "line": line,
                    "reason": "payment_id atau order_id kosong",
                }
            )
            continue

        raw_paid_at = _first(row, *PAYMENT_ALIASES["paid_at"])
        raw_paid_amount = _first(row, *PAYMENT_ALIASES["paid_amount"])
        payments.append(
            {
                "payment_id": payment_id,
                "order_id": order_id,
                "paid_at": _iso(raw_paid_at),
                "paid_amount": normalize_amount(raw_paid_amount),
                "method": (_first(row, *PAYMENT_ALIASES["method"]) or "UNKNOWN").upper(),
                "status": normalize_status(_first(row, *PAYMENT_ALIASES["status"])),
                "source_file": PAYMENTS_FILE,
                "raw_paid_at": raw_paid_at,
                "raw_paid_amount": raw_paid_amount,
            }
        )

    return payments, rejected

