from __future__ import annotations

import argparse
import sqlite3
from datetime import date, datetime
from pathlib import Path

from . import report
from .checks import run_checks
from .config import DATA_DIR, REPORT_DIR, SQL_DIR
from .loader import load_orders, load_payments
from .reconcile import reconcile

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


def _placeholders(columns: list[str]) -> str:
    return ", ".join("?" for _ in columns)


def build_database(
    conn: sqlite3.Connection, orders: list[dict], payments: list[dict]
) -> None:
    conn.executescript((SQL_DIR / "schema.sql").read_text(encoding="utf-8"))

    conn.executemany(
        f"INSERT INTO orders ({', '.join(ORDER_COLUMNS)}) VALUES ({_placeholders(ORDER_COLUMNS)})",
        [[row[column] for column in ORDER_COLUMNS] for row in orders],
    )
    conn.executemany(
        f"INSERT INTO payments ({', '.join(PAYMENT_COLUMNS)}) VALUES ({_placeholders(PAYMENT_COLUMNS)})",
        [[row[column] for column in PAYMENT_COLUMNS] for row in payments],
    )
    conn.commit()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Jalankan pipeline Data Quality Assurance untuk data order dan payment."
    )
    parser.add_argument(
        "--raw-dir",
        default=str(DATA_DIR),
        help="Folder berisi orders_web.csv, orders_app.csv, dan payments.csv.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(REPORT_DIR),
        help="Folder output untuk laporan dan artefak.",
    )
    parser.add_argument(
        "--as-of",
        default=None,
        help="Tanggal acuan (YYYY-MM-DD). Default: hari ini.",
    )
    args = parser.parse_args(argv)

    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)
    processed_dir = out_dir / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()

    orders, rejected_orders = load_orders(raw_dir)
    payments, rejected_payments = load_payments(raw_dir)
    rejected = rejected_orders + rejected_payments

    report.write_csv(
        processed_dir / "orders_normalized.csv", orders, ORDER_COLUMNS
    )
    report.write_csv(
        processed_dir / "payments_normalized.csv", payments, PAYMENT_COLUMNS
    )
    report.write_csv(
        processed_dir / "rejected_rows.csv",
        rejected,
        ["source_file", "line", "reason"],
    )

    db_path = out_dir / "qa.db"
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        build_database(conn, orders, payments)
        checks = run_checks(conn, as_of)
    finally:
        conn.close()

    reconciliation = reconcile(orders, payments)
    summary = reconciliation["summary"]

    report.write_csv(processed_dir / "matched_orders.csv", reconciliation["matched"])
    report.write_csv(
        processed_dir / "amount_mismatch.csv", reconciliation["amount_mismatch"]
    )
    report.write_csv(
        processed_dir / "order_without_payment.csv",
        reconciliation["order_without_payment"],
    )
    report.write_csv(
        processed_dir / "orphan_payments.csv", reconciliation["orphan_payments"]
    )
    report.write_csv(
        processed_dir / "duplicate_orders.csv", reconciliation["duplicate_orders"]
    )
    report.write_csv(
        processed_dir / "duplicate_payments.csv", reconciliation["duplicate_payments"]
    )
    report.write_csv(
        processed_dir / "cross_channel_duplicates.csv",
        reconciliation["cross_channel_duplicates"],
    )

    passed = sum(1 for check in checks if check["status"] == "PASS")
    failed = sum(1 for check in checks if check["status"] == "FAIL")
    errored = sum(1 for check in checks if check["status"] == "ERROR")
    pass_rate = (passed / len(checks) * 100) if checks else 0.0

    payload = {
        "as_of": as_of.isoformat(),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "check_summary": {
            "total": len(checks),
            "passed": passed,
            "failed": failed,
            "errored": errored,
            "pass_rate": round(pass_rate, 2),
        },
        "checks": checks,
        "reconciliation": summary,
        "rejected_rows": len(rejected),
    }
    report.write_json(out_dir / "dq_summary.json", payload)
    report.write_checks_markdown(out_dir / "dq_summary.md", checks, as_of.isoformat())
    report.write_daily_report(
        out_dir / "daily_report.md", as_of.isoformat(), summary, checks
    )

    print("=" * 68)
    print(f"Data Quality Report - as of {as_of.isoformat()}")
    print("=" * 68)
    print(f"Order rows        : {summary['total_order_rows']}")
    print(f"Unique orders     : {summary['unique_orders']}")
    print(f"Matched orders    : {summary['matched_orders']}")
    print(f"Checks            : {passed} passed, {failed} failed, {errored} error")
    print(f"Pass rate         : {pass_rate:.1f}%")
    print(f"Amount at risk    : Rp {summary['amount_at_risk']:,}")
    print("-" * 68)
    print(f"Duplicate rows    : {summary['duplicate_order_rows']}")
    print(f"Cross-channel dup : {summary['cross_channel_duplicates']}")
    print(f"Amount mismatch   : {summary['amount_mismatch']}")
    print(f"Unpaid orders     : {summary['order_without_payment']}")
    print(f"Orphan payments   : {summary['orphan_payments']}")
    print(f"Duplicate payments: {summary['duplicate_payments']}")
    print("-" * 68)
    print(f"Laporan           : {out_dir / 'daily_report.md'}")
    print(f"Ringkasan check   : {out_dir / 'dq_summary.md'}")
    print(f"JSON              : {out_dir / 'dq_summary.json'}")
    print("=" * 68)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
