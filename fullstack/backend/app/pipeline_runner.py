from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

from .database import SessionLocal
from .dq_bridge import run_pipeline_main
from .models import Run, utcnow


def execute_run(run_id: str, as_of: str) -> None:
    with SessionLocal() as db:
        run = db.get(Run, run_id)
        if run is None:
            return
        report_dir = Path(run.report_dir)
        run.status = "running"
        run.started_at = utcnow()
        db.commit()

    raw_dir = report_dir.parent / "raw"
    buffer = io.StringIO()

    try:
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            code = run_pipeline_main(
                [
                    "--raw-dir",
                    str(raw_dir),
                    "--out-dir",
                    str(report_dir),
                    "--as-of",
                    as_of,
                ]
            )

        (report_dir / "run.log").write_text(buffer.getvalue(), encoding="utf-8")

        if code != 0:
            raise RuntimeError(f"Pipeline berhenti dengan kode {code}.")

        summary_path = report_dir / "dq_summary.json"
        if not summary_path.exists():
            raise RuntimeError("Pipeline tidak menghasilkan dq_summary.json.")

        summary = json.loads(summary_path.read_text(encoding="utf-8"))

        with SessionLocal() as db:
            run = db.get(Run, run_id)
            if run is None:
                return
            run.status = "succeeded"
            run.summary_json = json.dumps(summary)
            run.finished_at = utcnow()
            db.commit()

    except Exception as exc:  # noqa: BLE001 - error disimpan untuk ditampilkan
        (report_dir / "run.log").write_text(buffer.getvalue(), encoding="utf-8")
        with SessionLocal() as db:
            run = db.get(Run, run_id)
            if run is None:
                return
            run.status = "failed"
            run.error = f"{type(exc).__name__}: {exc}"
            run.finished_at = utcnow()
            db.commit()
