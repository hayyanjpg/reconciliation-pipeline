import json
from pathlib import Path

from dq.run import main

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_dirty_dataset_matches_ground_truth(tmp_path):
    out_dir = tmp_path / "dirty"
    assert main(
        [
            "--raw-dir",
            str(ROOT / "data" / "raw"),
            "--out-dir",
            str(out_dir),
            "--as-of",
            "2026-10-31",
        ]
    ) == 0

    summary = load_json(out_dir / "dq_summary.json")
    truth = load_json(ROOT / "data" / "raw" / "_ground_truth.json")
    expected = truth["expected"]

    checks = {check["name"]: check["failed_rows"] for check in summary["checks"]}
    assert checks["duplicate_order_id"] == expected["duplicate_order_id_check"]
    assert checks["duplicate_payment_per_order"] == expected["duplicate_payment_per_order"]
    assert checks["missing_customer_id"] == expected["missing_customer_id"]
    assert checks["invalid_status"] == expected["invalid_status"]
    assert checks["non_positive_amount"] == expected["non_positive_amount"]
    assert checks["future_order_date"] == expected["future_order_date"]
    assert checks["unparseable_order_date"] == expected["unparseable_order_date"]
    assert checks["missing_amount"] == expected["missing_amount"]
    assert checks["orphan_payment"] == expected["orphan_payments"]
    assert checks["amount_mismatch"] == expected["amount_mismatch"]

    reconciliation = summary["reconciliation"]
    assert reconciliation["duplicate_order_rows"] == expected["duplicate_order_rows"]
    assert reconciliation["cross_channel_duplicates"] == expected["cross_channel_duplicates"]
    assert reconciliation["order_without_payment"] == expected["orders_without_payment"]
    assert reconciliation["orphan_payments"] == expected["orphan_payments"]
    assert reconciliation["duplicate_payments"] == expected["duplicate_payment_per_order"]

    assert summary["check_summary"]["failed"] > 0
    for name in (
        "daily_report.md",
        "dq_summary.md",
        "dq_summary.json",
        "processed/matched_orders.csv",
        "processed/amount_mismatch.csv",
        "processed/orphan_payments.csv",
    ):
        assert (out_dir / name).exists(), name


def test_clean_dataset_has_no_false_positive(tmp_path):
    out_dir = tmp_path / "clean"
    assert main(
        [
            "--raw-dir",
            str(ROOT / "data" / "clean"),
            "--out-dir",
            str(out_dir),
            "--as-of",
            "2026-10-31",
        ]
    ) == 0

    summary = load_json(out_dir / "dq_summary.json")
    assert summary["check_summary"]["failed"] == 0
    assert summary["check_summary"]["pass_rate"] == 100.0
    assert summary["reconciliation"]["amount_at_risk"] == 0
    assert summary["reconciliation"]["matched_orders"] == 220
