from __future__ import annotations

import csv
import json
from pathlib import Path


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_checks_markdown(path: Path, checks: list[dict], as_of: str) -> None:
    passed = sum(1 for check in checks if check["status"] == "PASS")
    total = len(checks)
    rate = (passed / total * 100) if total else 0.0

    lines = [
        f"# Ringkasan Data Quality - {as_of}",
        "",
        f"**Pass rate:** {passed}/{total} check ({rate:.1f}%)",
        "",
        "| Check | Kategori | Severity | Status | Baris gagal | Total baris |",
        "|---|---|---|---|---:|---:|",
    ]
    for check in checks:
        lines.append(
            "| {name} | {category} | {severity} | {status} | {failed} | {total} |".format(
                name=check.get("name", "-"),
                category=check.get("category", "-"),
                severity=check.get("severity", "-"),
                status=check["status"],
                failed=check["failed_rows"] if check["failed_rows"] is not None else "-",
                total=check["total_rows"],
            )
        )

    lines += ["", "## Detail kegagalan", ""]
    failed_checks = [check for check in checks if check["status"] == "FAIL"]
    if not failed_checks:
        lines.append("Tidak ada check yang gagal.")
    else:
        for check in failed_checks:
            lines.append(
                f"### {check['name']} ({check.get('severity', '-')}) - "
                f"{check['failed_rows']} baris"
            )
            lines.append("")
            lines.append(check.get("description", ""))
            lines.append("")
            if check.get("sample"):
                headers = list(check["sample"][0].keys())
                lines.append("| " + " | ".join(headers) + " |")
                lines.append("|" + "---|" * len(headers))
                for row in check["sample"]:
                    lines.append(
                        "| " + " | ".join(str(row[h]) for h in headers) + " |"
                    )
                lines.append("")

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_daily_report(
    path: Path,
    as_of: str,
    summary: dict,
    checks: list[dict],
) -> None:
    passed = sum(1 for check in checks if check["status"] == "PASS")
    total = len(checks)
    rate = (passed / total * 100) if total else 0.0
    critical_failed = [
        check
        for check in checks
        if check["status"] == "FAIL" and check.get("severity") == "critical"
    ]

    findings = [
        f"{summary['duplicate_order_rows']} baris order duplikat di dalam file sumber.",
        f"{summary['cross_channel_duplicates']} order_id muncul di lebih dari satu channel.",
        f"{summary['amount_mismatch']} order dengan nominal pembayaran tidak sama dengan order.",
        f"{summary['order_without_payment']} order belum memiliki pembayaran valid.",
        f"{summary['orphan_payments']} pembayaran tidak memiliki order induk.",
        f"{summary['duplicate_payments']} order menerima lebih dari satu pembayaran valid.",
    ]

    recommendations = [
        "Terapkan constraint unik pada order_id dan idempotency key saat ingest.",
        "Normalisasi order_id, tanggal, nominal, dan channel di staging sebelum join.",
        "Pisahkan baris gagal ke tabel quarantine, jangan dibuang diam-diam.",
        "Tambahkan monitoring harian untuk duplikat, orphan payment, dan selisih nominal.",
        "Buat rekonsiliasi otomatis antara order dan payment sebelum laporan ke finance.",
    ]

    lines = [
        f"# Laporan Harian Data Quality - {as_of}",
        "",
        "## Ringkasan",
        "",
        "| Metrik | Nilai |",
        "|---|---:|",
        f"| Baris order masuk | {summary['total_order_rows']} |",
        f"| Order unik | {summary['unique_orders']} |",
        f"| Order matched | {summary['matched_orders']} |",
        f"| Check lulus | {passed}/{total} ({rate:.1f}%) |",
        f"| Critical check gagal | {len(critical_failed)} |",
        f"| Estimasi nominal berisiko | Rp {summary['amount_at_risk']:,} |",
        "",
        "## Temuan utama",
        "",
    ]
    lines += [f"{index}. {text}" for index, text in enumerate(findings, start=1)]
    lines += ["", "## Rekomendasi", ""]
    lines += [f"- {text}" for text in recommendations]

    lines += ["", "## Status", ""]
    if critical_failed:
        names = ", ".join(check["name"] for check in critical_failed)
        lines.append(
            f"**PERLU TINDAKAN HARI INI.** Critical check gagal: {names}."
        )
    else:
        lines.append("**AMAN.** Semua critical check lulus.")

    lines += [
        "",
        "## Artefak",
        "",
        "- `reports/dq_summary.json` - hasil semua check",
        "- `reports/dq_summary.md` - tabel check",
        "- `reports/processed/*.csv` - baris matched, mismatch, orphan, duplikat",
        "",
    ]

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
