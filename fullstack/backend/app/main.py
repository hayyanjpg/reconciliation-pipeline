from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from .config import (
    CORS_ORIGINS,
    DEMO_RAW_DIR,
    FRONTEND_DIST,
    MAX_FILE_MB,
    RUN_TTL_HOURS,
)
from .database import SessionLocal, init_db
from .dq_bridge import (
    file_definition,
    schema_payload,
    template_csv,
    template_zip,
)
from .jobs import enqueue, recover_stale_runs
from .models import Run
from .storage import (
    RUNS_DIR,
    artifact_path,
    cleanup_expired,
    copy_demo_files,
    ensure_storage,
    list_artifacts,
    new_run_dir,
    save_bytes,
)
from .validation import validate_uploads


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_storage()
    init_db()
    cleanup_expired()
    recover_stale_runs()
    yield


app = FastAPI(
    title="Data Quality API",
    description="Upload, validasi, dan jalankan pipeline Data Quality Assurance.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_as_of(value: str | None) -> str:
    if value is None or not str(value).strip():
        return date.today().isoformat()
    try:
        return date.fromisoformat(str(value).strip()).isoformat()
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail="Tanggal as-of harus berformat YYYY-MM-DD."
        ) from exc


def _iso(value):
    return value.isoformat() if value else None


def _serialize_run(run: Run, include_summary: bool = True) -> dict:
    summary = None
    if include_summary and run.summary_json:
        summary = json.loads(run.summary_json)
    return {
        "id": run.id,
        "status": run.status,
        "source": run.source,
        "as_of": run.as_of,
        "created_at": _iso(run.created_at),
        "started_at": _iso(run.started_at),
        "finished_at": _iso(run.finished_at),
        "error": run.error,
        "files": json.loads(run.files_json or "{}"),
        "summary": summary,
    }


async def _read_upload(upload: UploadFile | None) -> bytes | None:
    if upload is None:
        return None
    limit = MAX_FILE_MB * 1024 * 1024
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await upload.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise HTTPException(
                status_code=413,
                detail=f"File {upload.filename} melebihi batas {MAX_FILE_MB} MB.",
            )
        chunks.append(chunk)
    return b"".join(chunks)


async def _read_uploads(
    files: dict[str, UploadFile | None]
) -> dict[str, bytes | None]:
    contents: dict[str, bytes | None] = {}
    for key, upload in files.items():
        contents[key] = await _read_upload(upload)
    return contents


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api")
def api_info() -> dict:
    return {
        "name": "Data Quality API",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/meta")
def meta() -> dict:
    return {
        "schema": schema_payload(),
        "limits": {
            "max_file_mb": MAX_FILE_MB,
            "ttl_hours": RUN_TTL_HOURS,
        },
        "demo_available": DEMO_RAW_DIR.exists(),
    }


@app.get("/api/templates/all.zip")
def download_all_templates() -> Response:
    return Response(
        content=template_zip(),
        media_type="application/zip",
        headers={
            "Content-Disposition": 'attachment; filename="template-data-quality.zip"'
        },
    )


@app.get("/api/templates/{key}")
def download_template(key: str) -> Response:
    item = file_definition(key)
    if item is None:
        raise HTTPException(status_code=404, detail="Template tidak ditemukan.")
    content = template_csv(item["fields"], item["example"]).encode("utf-8")
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{item["filename"]}"'
        },
    )


@app.post("/api/validate")
async def validate_endpoint(
    orders_web: UploadFile | None = File(None),
    orders_app: UploadFile | None = File(None),
    payments: UploadFile | None = File(None),
) -> dict:
    contents = await _read_uploads(
        {
            "orders_web": orders_web,
            "orders_app": orders_app,
            "payments": payments,
        }
    )
    return validate_uploads(contents)


@app.post("/api/runs", status_code=202)
async def create_run(
    as_of: str = Form(...),
    orders_web: UploadFile | None = File(None),
    orders_app: UploadFile | None = File(None),
    payments: UploadFile | None = File(None),
) -> dict:
    as_of_value = _parse_as_of(as_of)
    contents = await _read_uploads(
        {
            "orders_web": orders_web,
            "orders_app": orders_app,
            "payments": payments,
        }
    )
    validation = validate_uploads(contents)

    if validation["missing_files"]:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Semua file wajib diupload.",
                "validation": validation,
            },
        )
    if not validation["ok"]:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Perbaiki file yang bertanda error sebelum menjalankan.",
                "validation": validation,
            },
        )

    run_id = str(uuid4())
    new_run_dir(run_id)
    files_meta: dict[str, dict] = {}
    for key, content in contents.items():
        item = file_definition(key)
        if item is None or content is None:
            continue
        save_bytes(run_id, item["filename"], content)
        files_meta[key] = {"filename": item["filename"], "size": len(content)}

    with SessionLocal() as db:
        run = Run(
            id=run_id,
            status="queued",
            source="upload",
            as_of=as_of_value,
            files_json=json.dumps(files_meta),
            report_dir=str(RUNS_DIR / run_id / "reports"),
        )
        db.add(run)
        db.commit()

    enqueue(run_id, as_of_value)
    return {"id": run_id, "status": "queued"}


@app.post("/api/runs/demo", status_code=202)
def create_demo_run(as_of: str | None = Form(None)) -> dict:
    as_of_value = _parse_as_of(as_of)
    run_id = str(uuid4())
    new_run_dir(run_id)
    copied = copy_demo_files(run_id)

    with SessionLocal() as db:
        run = Run(
            id=run_id,
            status="queued",
            source="demo",
            as_of=as_of_value,
            files_json=json.dumps(
                {"demo": {"filename": ", ".join(copied), "size": 0}}
            ),
            report_dir=str(RUNS_DIR / run_id / "reports"),
        )
        db.add(run)
        db.commit()

    enqueue(run_id, as_of_value)
    return {"id": run_id, "status": "queued"}


@app.get("/api/runs")
def list_runs() -> list[dict]:
    with SessionLocal() as db:
        runs = db.scalars(
            select(Run).order_by(Run.created_at.desc()).limit(10)
        ).all()
    return [_serialize_run(run, include_summary=False) for run in runs]


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict:
    with SessionLocal() as db:
        run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run tidak ditemukan.")
    return _serialize_run(run)


@app.get("/api/runs/{run_id}/results")
def get_results(run_id: str) -> dict:
    with SessionLocal() as db:
        run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run tidak ditemukan.")
    if run.status != "succeeded":
        raise HTTPException(
            status_code=409, detail="Run belum selesai atau gagal."
        )
    return {
        "run": _serialize_run(run, include_summary=False),
        "summary": json.loads(run.summary_json or "{}"),
        "artifacts": list_artifacts(run.report_dir),
    }


@app.get("/api/runs/{run_id}/artifacts/{artifact:path}")
def download_artifact(run_id: str, artifact: str) -> FileResponse:
    with SessionLocal() as db:
        run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run tidak ditemukan.")

    path = artifact_path(run.report_dir, artifact)
    if path is None:
        raise HTTPException(status_code=404, detail="Artefak tidak ditemukan.")

    media_type = "application/octet-stream"
    if path.suffix == ".json":
        media_type = "application/json"
    elif path.suffix == ".md":
        media_type = "text/markdown"
    elif path.suffix == ".csv":
        media_type = "text/csv"

    return FileResponse(
        path,
        media_type=media_type,
        filename=Path(artifact).name,
    )


if FRONTEND_DIST.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIST), html=True),
        name="frontend",
    )
