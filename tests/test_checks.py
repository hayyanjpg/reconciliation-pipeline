import sqlite3
from datetime import date
from pathlib import Path

from dq.checks import run_checks
from dq.config import SQL_DIR

ORDER_COLUMNS = [
    "order_id",
    "customer_id",
    "order_date",
    "amount",
    "status",
    "channel",
    "source_file",
    "raw_order_date",
    "raw_amount",
]

PAYMENT_COLUMNS = [
    "payment_id",
    "order_id",
    "paid_at",
    "paid_amount",
    "method",
    "status",
    "source_file",
    "raw_paid_at",
    "raw_paid_amount",
]


def build_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript((SQL_DIR / "schema.sql").read_text(encoding="utf-8"))
    return conn


def insert_order(conn, **overrides):
    row = {
        "order_id": "ORD-1",
        "customer_id": "CUST-001",
        "order_date": "2026-10-30",
        "amount": 100000,
        "status": "COMPLETED",
        "channel": "WEB",
        "source_file": "orders_web.csv",
        "raw_order_date": "2026-10-30",
        "raw_amount": "100000",
    }
    row.update(overrides)
    conn.execute(
        f"INSERT INTO orders ({', '.join(ORDER_COLUMNS)}) VALUES ({', '.join('?' * len(ORDER_COLUMNS))})",
        [row[column] for column in ORDER_COLUMNS],
    )


def insert_payment(conn, **overrides):
    row = {
        "payment_id": "PAY-1",
        "order_id": "ORD-1",
        "paid_at": "2026-10-31",
        "paid_amount": 100000,
        "method": "QRIS",
        "status": "PAID",
        "source_file": "payments.csv",
        "raw_paid_at": "2026-10-31",
        "raw_paid_amount": "100000",
    }
    row.update(overrides)
    conn.execute(
        f"INSERT INTO payments ({', '.join(PAYMENT_COLUMNS)}) VALUES ({', '.join('?' * len(PAYMENT_COLUMNS))})",
        [row[column] for column in PAYMENT_COLUMNS],
    )


def test_clean_rows_pass_every_check():
    conn = build_db()
    insert_order(conn)
    insert_payment(conn)

    results = run_checks(conn, date(2026, 10, 31))

    assert all(check["status"] == "PASS" for check in results), [
        check["name"] for check in results if check["status"] != "PASS"
    ]


def test_each_anomaly_is_detected():
    conn = build_db()

    insert_order(conn, order_id="ORD-1")
    insert_order(conn, order_id="ORD-1")  # duplikat
    insert_order(conn, order_id="ORD-2", customer_id=None)
    insert_order(conn, order_id="ORD-3", amount=-5000)
    insert_order(conn, order_id="ORD-4", status="DONE")
    insert_order(conn, order_id="ORD-5", order_date="2027-01-15")
    insert_order(
        conn,
        order_id="ORD-6",
        order_date=None,
        raw_order_date="31/13/2026",
    )
    insert_order(
        conn,
        order_id="ORD-7",
        amount=None,
        raw_amount="N/A",
    )

    insert_payment(conn, payment_id="PAY-1", order_id="ORD-1", paid_amount=100000)
    insert_payment(conn, payment_id="PAY-2", order_id="ORD-1", paid_amount=100000)
    insert_payment(conn, payment_id="PAY-3", order_id="ORD-2", paid_amount=50000)
    insert_payment(conn, payment_id="PAY-4", order_id="ORD-3", paid_amount=-5000)
    insert_payment(conn, payment_id="PAY-5", order_id="ORD-4", paid_at="2026-09-01")
    insert_payment(conn, payment_id="PAY-6", order_id="ORD-999", paid_amount=100000)
    insert_payment(conn, payment_id="PAY-7", order_id="ORD-5", paid_at=None)

    results = {check["name"]: check for check in run_checks(conn, date(2026, 10, 31))}

    expected_failures = {
        "duplicate_order_id": 1,
        "duplicate_payment_per_order": 1,
        "missing_customer_id": 1,
        "non_positive_amount": 1,
        "invalid_status": 1,
        "future_order_date": 1,
        "unparseable_order_date": 1,
        "missing_amount": 1,
        "non_positive_paid_amount": 1,
        "orphan_payment": 1,
        "payment_before_order": 1,
        "missing_paid_at": 1,
    }
    for name, expected in expected_failures.items():
        assert results[name]["status"] == "FAIL", name
        assert results[name]["failed_rows"] == expected, name

    assert results["amount_mismatch"]["status"] == "FAIL"
    assert results["amount_mismatch"]["failed_rows"] >= 1
