from __future__ import annotations

import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import artifact_path

RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def upload_files() -> dict:
    return {
        "orders_web": (
            "orders_web.csv",
            (RAW_DIR / "orders_web.csv").read_bytes(),
            "text/csv",
        ),
        "orders_app": (
            "orders_app.csv",
            (RAW_DIR / "orders_app.csv").read_bytes(),
            "text/csv",
        ),
        "payments": (
            "payments.csv",
            (RAW_DIR / "payments.csv").read_bytes(),
            "text/csv",
        ),
    }


def test_health_and_meta(client: TestClient):
    assert client.get("/api/health").json() == {"status": "ok"}

    meta = client.get("/api/meta").json()
    assert len(meta["schema"]["files"]) == 3
    assert meta["limits"]["max_file_mb"] == 10
    assert meta["demo_available"] is True


def test_templates(client: TestClient):
    response = client.get("/api/templates/orders_web")
    assert response.status_code == 200
    assert response.text.splitlines()[0] == (
        "order_id,customer_id,order_date,amount,status,channel"
    )

    archive = client.get("/api/templates/all.zip")
    assert archive.status_code == 200
    assert archive.content[:2] == b"PK"


def test_validate_uploaded_files(client: TestClient):
    response = client.post("/api/validate", files=upload_files())
    assert response.status_code == 200

    payload = response.json()
    assert payload["ok"] is True
    assert payload["missing_files"] == []
    assert payload["files"]["orders_web.csv"]["row_count"] == 113
    assert payload["files"]["orders_app.csv"]["row_count"] == 117
    assert payload["files"]["payments.csv"]["row_count"] == 214


def test_validate_missing_required_column(client: TestClient):
    response = client.post(
        "/api/validate",
        files={
            "orders_web": ("orders_web.csv", b"amount\n100\n", "text/csv"),
        },
    )
    payload = response.json()
    assert payload["ok"] is False
    assert "order_id" in payload["files"]["orders_web.csv"]["missing_required"]
    assert payload["missing_files"] == ["orders_app.csv", "payments.csv"]


def test_validate_warning_does_not_block(client: TestClient):
    response = client.post(
        "/api/validate",
        files={
            "orders_web": ("orders_web.csv", b"order_id\nORD-1\n", "text/csv"),
            "orders_app": ("orders_app.csv", b"order_id\nORD-2\n", "text/csv"),
            "payments": (
                "payments.csv",
                b"payment_id,order_id\nPAY-1,ORD-1\n",
                "text/csv",
            ),
        },
    )
    payload = response.json()
    assert payload["ok"] is True
    assert payload["files"]["orders_web.csv"]["status"] == "warning"
    assert "customer_id" in payload["files"]["orders_web.csv"]["missing_recommended"]


def test_invalid_as_of(client: TestClient):
    response = client.post(
        "/api/runs/demo", data={"as_of": "31-10-2026"}
    )
    assert response.status_code == 422


def test_upload_run_end_to_end(client: TestClient):
    created = client.post(
        "/api/runs",
        data={"as_of": "2026-10-31"},
        files=upload_files(),
    )
    assert created.status_code == 202
    run_id = created.json()["id"]

    run = {}
    for _ in range(90):
        run = client.get(f"/api/runs/{run_id}").json()
        if run["status"] in ("succeeded", "failed"):
            break
        time.sleep(1)

    assert run["status"] == "succeeded", run.get("error")
    assert run["source"] == "upload"

    results = client.get(f"/api/runs/{run_id}/results").json()
    assert results["summary"]["check_summary"]["pass_rate"] == 12.5
    assert results["summary"]["reconciliation"]["amount_at_risk"] == 5118000
    assert len(results["artifacts"]) >= 10


def test_run_requires_all_files(client: TestClient):
    response = client.post(
        "/api/runs",
        data={"as_of": "2026-10-31"},
        files={"orders_web": ("orders_web.csv", b"order_id\nORD-1\n", "text/csv")},
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["validation"]["missing_files"] == [
        "orders_app.csv",
        "payments.csv",
    ]


def test_demo_run_end_to_end(client: TestClient):
    created = client.post("/api/runs/demo", data={"as_of": "2026-10-31"})
    assert created.status_code == 202
    run_id = created.json()["id"]

    run = {}
    for _ in range(90):
        run = client.get(f"/api/runs/{run_id}").json()
        if run["status"] in ("succeeded", "failed"):
            break
        time.sleep(1)

    assert run["status"] == "succeeded", run.get("error")

    results = client.get(f"/api/runs/{run_id}/results").json()
    summary = results["summary"]
    assert summary["check_summary"]["total"] == 16
    assert summary["check_summary"]["passed"] == 2
    assert summary["check_summary"]["pass_rate"] == 12.5
    assert summary["reconciliation"]["amount_at_risk"] == 5118000
    assert len(results["artifacts"]) >= 10

    artifact = client.get(f"/api/runs/{run_id}/artifacts/daily_report.md")
    assert artifact.status_code == 200
    assert "Data Quality" in artifact.text


def test_artifact_path_blocks_traversal(tmp_path):
    base = tmp_path / "reports"
    base.mkdir()
    (base / "daily_report.md").write_text("ok", encoding="utf-8")

    assert artifact_path(str(base), "daily_report.md") is not None
    assert artifact_path(str(base), "../secret.txt") is None

