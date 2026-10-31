from __future__ import annotations

import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config import DEMO_RAW_DIR, RUN_TTL_HOURS, STORAGE_DIR
from .dq_bridge import FILES

RUNS_DIR = STORAGE_DIR / "runs"

ARTIFACTS = [
    ("dq_summary.json", "Ringkasan JSON", "application/json"),
    ("dq_summary.md", "Ringkasan Markdown", "text/markdown"),
    ("daily_report.md", "Laporan harian", "text/markdown"),
    ("processed/matched_orders.csv", "Order matched", "text/csv"),
    ("processed/amount_mismatch.csv", "Amount mismatch", "text/csv"),
    ("processed/order_without_payment.csv", "Order belum dibayar", "text/csv"),
    ("processed/orphan_payments.csv", "Pembayaran yatim", "text/csv"),
    ("processed/duplicate_orders.csv", "Duplikat order", "text/csv"),
    ("processed/duplicate_payments.csv", "Pembayaran ganda", "text/csv"),
    ("processed/cross_channel_duplicates.csv", "Duplikat antar channel", "text/csv"),
    ("processed/rejected_rows.csv", "Baris ditolak", "text/csv"),
    ("processed/orders_normalized.csv", "Order ternormalisasi", "text/csv"),
    ("processed/payments_normalized.csv", "Pembayaran ternormalisasi", "text/csv"),
]


def ensure_storage() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)


def new_run_dir(run_id: str) -> Path:
    path = RUNS_DIR / run_id
    (path / "raw").mkdir(parents=True, exist_ok=True)
    (path / "reports").mkdir(parents=True, exist_ok=True)
    return path


def save_bytes(run_id: str, filename: str, content: bytes) -> Path:
    path = RUNS_DIR / run_id / "raw" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def copy_demo_files(run_id: str) -> list[str]:
    copied: list[str] = []
    for item in FILES:
        source = DEMO_RAW_DIR / item["filename"]
        if not source.exists():
            raise FileNotFoundError(f"Data demo tidak ditemukan: {source}")
        save_bytes(run_id, item["filename"], source.read_bytes())
        copied.append(item["filename"])
    return copied


def artifact_path(report_dir: str, artifact: str) -> Path | None:
    base = Path(report_dir).resolve()
    path = (base / artifact).resolve()
    if not path.is_relative_to(base) or not path.is_file():
        return None
    return path


def list_artifacts(report_dir: str) -> list[dict]:
    base = Path(report_dir)
    result = []
    for name, label, media_type in ARTIFACTS:
        path = base / name
        if path.is_file():
            result.append(
                {
                    "name": name,
                    "label": label,
                    "media_type": media_type,
                    "size": path.stat().st_size,
                }
            )
    return result


def cleanup_expired(ttl_hours: int | None = None) -> int:
    ensure_storage()
    ttl = ttl_hours if ttl_hours is not None else RUN_TTL_HOURS
    cutoff = datetime.now(timezone.utc) - timedelta(hours=ttl)
    removed_ids: list[str] = []
    for path in RUNS_DIR.iterdir():
        if not path.is_dir():
            continue
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        if modified < cutoff:
            shutil.rmtree(path, ignore_errors=True)
            removed_ids.append(path.name)

    if removed_ids:
        from sqlalchemy import delete

        from .database import SessionLocal
        from .models import Run

        with SessionLocal() as db:
            db.execute(delete(Run).where(Run.id.in_(removed_ids)))
            db.commit()

    return len(removed_ids)
