from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from sqlalchemy import update

from .database import SessionLocal
from .models import Run, utcnow
from .pipeline_runner import execute_run

EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="dq-run")


def enqueue(run_id: str, as_of: str) -> None:
    EXECUTOR.submit(execute_run, run_id, as_of)


def recover_stale_runs(max_age_hours: float | None = None) -> int:
    statement = update(Run).where(Run.status.in_(("queued", "running")))
    if max_age_hours is not None:
        statement = statement.where(
            Run.created_at < utcnow() - timedelta(hours=max_age_hours)
        )
    with SessionLocal() as db:
        result = db.execute(
            statement.values(
                status="failed",
                error="Run terhenti karena server restart.",
                finished_at=utcnow(),
            )
        )
        db.commit()
        return result.rowcount or 0
