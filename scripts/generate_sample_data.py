"""Generate dataset contoh multichannel untuk pengujian pipeline Data Quality.

Dua mode:
  dirty (default) : data sengaja kotor, setiap kategori anomali diwakili.
  clean           : data bersih, dipakai untuk membuktikan tidak ada false positive.

Contoh:
  python scripts/generate_sample_data.py
  python scripts/generate_sample_data.py --clean
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
BASE_DATE = date(2026, 10, 1)
AS_OF = date(2026, 10, 31)

STATUSES = ["COMPLETED", "PENDING", "CANCELLED", "REFUNDED"]
METHODS = ["BCA_VA", "GOPAY", "OVO", "DANA", "QRIS", "CREDIT_CARD"]
AMOUNTS = [45000, 75000, 99000, 125000, 150000, 199000, 250000, 350000, 499000, 750000]

ANOMALY_KEYS = (
    "null_customer_id",
    "invalid_status",
    "negative_amount",
    "future_order_date",
    "old_order_date",
    "unparseable_order_date",
    "unparseable_amount",
)


def build_base_orders(rng: random.Random) -> list[dict]:
    orders = []
    for index in range(1, 221):
        order_date = BASE_DATE + timedelta(days=rng.randint(0, 29))
        orders.append(
            {
                "order_id": f"ORD-{1000 + index}",
                "customer_id": f"CUST-{rng.randint(1, 80):03d}",
                "order_date": order_date,
                "amount": rng.choice(AMOUNTS),
                "status": rng.choices(STATUSES, weights=[82, 10, 5, 3])[0],
                "channel": "WEB" if index % 2 == 0 else "APP",
            }
        )
    return orders


def build_dataset(dirty: bool, rng: random.Random):
    orders = build_base_orders(rng)
    web = [order for order in orders if order["channel"] == "WEB"]
    app = [order for order in orders if order["channel"] == "APP"]
    rows: list[dict] = list(orders)

    cross_sources: list[dict] = []
    duplicate_app_sources: list[dict] = []
    duplicate_web_sources: list[dict] = []
    anomalies: dict[str, list[dict]] = {key: [] for key in ANOMALY_KEYS}

    if dirty:
        cross_sources = web[:3]
        for order in cross_sources:
            rows.append({**order, "channel": "APP"})

        duplicate_app_sources = app[:4]
        for order in duplicate_app_sources:
            rows.append({**order, "channel": "APP"})

        duplicate_web_sources = web[3:5]
        for order in duplicate_web_sources:
            rows.append(
                {**order, "order_id": order["order_id"].lower(), "channel": "WEB"}
            )
        rows.append(
            {
                **duplicate_web_sources[0],
                "order_id": " " + duplicate_web_sources[0]["order_id"] + " ",
                "channel": "WEB",
            }
        )

        protected = {
            order["order_id"]
            for order in cross_sources
            + duplicate_app_sources
            + duplicate_web_sources
        }
        pool = [order for order in orders if order["order_id"] not in protected]
        rng.shuffle(pool)

        def take(count: int) -> list[dict]:
            selected = pool[:count]
            del pool[:count]
            return selected

        anomalies = {
            "null_customer_id": take(5),
            "invalid_status": take(3),
            "negative_amount": take(2),
            "future_order_date": take(2),
            "old_order_date": take(3),
            "unparseable_order_date": take(2),
            "unparseable_amount": take(1),
        }

        for order in anomalies["null_customer_id"]:
            order["customer_id"] = ""
        for order in anomalies["invalid_status"]:
            order["status"] = rng.choice(["DONE", "paid", ""])
        for order in anomalies["negative_amount"]:
            order["amount"] = -50000
        for order in anomalies["future_order_date"]:
            order["order_date"] = date(2027, 1, 15)
        for order in anomalies["old_order_date"]:
            order["order_date"] = date(2019, 5, 10)
        for order in anomalies["unparseable_order_date"]:
            order["_bad_date"] = True
        for order in anomalies["unparseable_amount"]:
            order["_bad_amount"] = True

    # Variasi nama channel untuk menguji normalisasi (tetap valid).
    for order in rng.sample(rows, 10):
        if order["channel"] == "WEB":
            order["channel"] = "website"
        else:
            order["channel"] = "android"

    canonical_ids = [order["order_id"] for order in orders]
    order_by_id = {order["order_id"]: order for order in orders}
    anomaly_ids = {
        order["order_id"] for group in anomalies.values() for order in group
    }
    bad_amount_id = (
        anomalies["unparseable_amount"][0]["order_id"] if dirty else None
    )

    if dirty:
        unpaid = set(
            rng.sample([oid for oid in canonical_ids if oid != bad_amount_id], 15)
        )
        unpaid.add(bad_amount_id)
    else:
        unpaid = set()

    remaining = [
        oid for oid in canonical_ids if oid not in unpaid and oid not in anomaly_ids
    ]
    rng.shuffle(remaining)

    mismatch_ids: set[str] = set()
    duplicate_payment_ids: set[str] = set()
    before_order_ids: set[str] = set()
    late_payment_ids: set[str] = set()
    failed_ids: set[str] = set()
    null_paid_at_ids: set[str] = set()

    if dirty:
        mismatch_ids = set(remaining[:8])
        duplicate_payment_ids = set(remaining[8:12])
        before_order_ids = set(remaining[12:14])
        late_payment_ids = set(remaining[14:16])
        failed_ids = set(remaining[16:18])
        null_paid_at_ids = set(remaining[18:20])

    payments: list[dict] = []
    counter = 0

    def add_payment(order_id: str, paid_at, amount, status: str) -> None:
        nonlocal counter
        counter += 1
        payments.append(
            {
                "payment_id": f"PAY-{counter:04d}",
                "order_id": order_id,
                "paid_at": paid_at,
                "paid_amount": amount,
                "method": rng.choice(METHODS),
                "status": status,
            }
        )

    for order_id in canonical_ids:
        if order_id in unpaid:
            continue

        order = order_by_id[order_id]
        order_date = order["order_date"]
        paid_at = order_date + timedelta(days=rng.randint(0, 2))
        amount = order["amount"]
        status = "PAID" if rng.random() < 0.9 else "PENDING"

        if order_id in mismatch_ids:
            amount = max(order["amount"] - rng.choice([5000, 10000, 25000]), 1000)
        if order_id in before_order_ids:
            paid_at = order_date - timedelta(days=3)
        if order_id in late_payment_ids:
            paid_at = order_date + timedelta(days=15)
        if order_id in failed_ids:
            status = "FAILED"
        if order_id in null_paid_at_ids:
            paid_at = None
            status = "PAID"

        add_payment(order_id, paid_at, amount, status)

        if order_id in duplicate_payment_ids:
            add_payment(order_id, paid_at, order["amount"], "PAID")

    if dirty:
        for index in range(6):
            orphan_date = BASE_DATE + timedelta(days=rng.randint(0, 25))
            add_payment(
                f"ORD-{9001 + index}", orphan_date, rng.choice(AMOUNTS), "PAID"
            )

    ground_truth = {
        "mode": "dirty" if dirty else "clean",
        "seed": SEED,
        "as_of": AS_OF.isoformat(),
        "base_orders": len(orders),
        "order_rows_written": len(rows),
        "payment_rows_written": len(payments),
        "expected": {
            "cross_channel_duplicates": len(cross_sources),
            "duplicate_order_rows": len(duplicate_app_sources)
            + len(duplicate_web_sources)
            + (1 if dirty else 0),
            "duplicate_order_id_check": len(cross_sources)
            + len(duplicate_app_sources)
            + len(duplicate_web_sources),
            "duplicate_payment_per_order": len(duplicate_payment_ids),
            "amount_mismatch": len(mismatch_ids) + len(duplicate_payment_ids),
            "missing_customer_id": len(anomalies["null_customer_id"]),
            "invalid_status": len(anomalies["invalid_status"]),
            "non_positive_amount": len(anomalies["negative_amount"]),
            "non_positive_paid_amount": len(anomalies["negative_amount"]),
            "future_order_date": len(anomalies["future_order_date"]),
            "unparseable_order_date": len(anomalies["unparseable_order_date"]),
            "missing_amount": len(anomalies["unparseable_amount"]),
            "orders_without_payment": len(unpaid) + len(failed_ids),
            "orphan_payments": 6 if dirty else 0,
            "payment_before_order": len(before_order_ids),
            "late_payment": len(late_payment_ids),
            "missing_paid_at": len(null_paid_at_ids),
        },
    }
    return rows, payments, ground_truth


def format_date(row: dict, channel: str) -> str:
    if row.get("_bad_date"):
        return "31/13/2026"
    if channel == "WEB":
        return row["order_date"].isoformat()
    return row["order_date"].strftime("%d/%m/%Y")


def format_amount(row: dict, channel: str, rng: random.Random) -> str:
    if row.get("_bad_amount"):
        return "N/A"
    amount = row["amount"]
    if channel == "WEB":
        return str(amount)
    text = f"{amount:,}".replace(",", ".")
    return text + ",00" if rng.random() < 0.4 else text


def write_outputs(out_dir: Path, rows: list[dict], payments: list[dict], truth: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    writer_rng = random.Random(SEED + 1)

    def write_orders(filename: str, subset: list[dict], default_channel: str) -> None:
        with open(out_dir / filename, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "order_id",
                    "customer_id",
                    "order_date",
                    "amount",
                    "status",
                    "channel",
                ],
            )
            writer.writeheader()
            for row in subset:
                writer.writerow(
                    {
                        "order_id": row["order_id"],
                        "customer_id": row["customer_id"],
                        "order_date": format_date(row, default_channel),
                        "amount": format_amount(row, default_channel, writer_rng),
                        "status": row["status"],
                        "channel": row["channel"],
                    }
                )

    web_rows = [row for row in rows if row["channel"] in ("WEB", "website")]
    app_rows = [row for row in rows if row["channel"] in ("APP", "android")]
    write_orders("orders_web.csv", web_rows, "WEB")
    write_orders("orders_app.csv", app_rows, "APP")

    with open(out_dir / "payments.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "payment_id",
                "order_id",
                "paid_at",
                "paid_amount",
                "method",
                "status",
            ],
        )
        writer.writeheader()
        for payment in payments:
            paid_at = (
                payment["paid_at"].isoformat()
                if payment["paid_at"] is not None
                else ""
            )
            writer.writerow({**payment, "paid_at": paid_at})

    (out_dir / "_ground_truth.json").write_text(
        json.dumps(truth, indent=2), encoding="utf-8"
    )

    print(f"orders_web.csv : {len(web_rows)} baris")
    print(f"orders_app.csv : {len(app_rows)} baris")
    print(f"payments.csv   : {len(payments)} baris")
    print(f"ground truth   : {out_dir / '_ground_truth.json'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate dataset contoh Data QA.")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Buat dataset bersih (tanpa anomali) untuk uji false positive.",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Folder output. Default: data/raw (dirty) atau data/clean (clean).",
    )
    args = parser.parse_args()

    out_dir = (
        Path(args.out_dir)
        if args.out_dir
        else ROOT / "data" / ("clean" if args.clean else "raw")
    )
    rng = random.Random(SEED)
    rows, payments, truth = build_dataset(dirty=not args.clean, rng=rng)
    write_outputs(out_dir, rows, payments, truth)


if __name__ == "__main__":
    main()
