from __future__ import annotations

import csv
import io

from .config import MAX_FILE_MB
from .dq_bridge import (
    FILES,
    alias_lookup,
    canonical_key,
    decode_csv,
    sniff_delimiter,
    validate_header_list,
)

MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024


def _empty_result(item: dict, message: str) -> dict:
    return {
        "key": item["key"],
        "filename": item["filename"],
        "status": "error",
        "errors": [message],
        "warnings": [],
        "encoding": None,
        "delimiter": None,
        "row_count": 0,
        "headers": [],
        "recognized": [],
        "missing_required": [field["name"] for field in item["fields"] if field["required"]],
        "missing_recommended": [],
        "unknown_columns": [],
        "duplicate_columns": [],
        "preview": [],
    }


def validate_file(content: bytes | None, item: dict) -> dict:
    if content is None:
        return _empty_result(item, "File belum diupload.")

    if len(content) == 0:
        return _empty_result(item, "File kosong.")

    if len(content) > MAX_FILE_BYTES:
        return _empty_result(
            item, f"Ukuran file melebihi batas {MAX_FILE_MB} MB."
        )

    text, encoding, warnings = decode_csv(content)
    errors: list[str] = []

    if not text.strip():
        return _empty_result(item, "File tidak berisi teks.")

    delimiter = sniff_delimiter(text)
    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
    headers = [header.strip() for header in rows[0]] if rows else []

    if not headers or not any(headers):
        return _empty_result(item, "Baris header tidak ditemukan.")

    header_check = validate_header_list(headers, item["fields"])

    if header_check["missing_required"]:
        errors.append(
            "Kolom wajib hilang: " + ", ".join(header_check["missing_required"])
        )
    if header_check["missing_recommended"]:
        warnings.append(
            "Kolom disarankan hilang: "
            + ", ".join(header_check["missing_recommended"])
        )
    if header_check["unknown_columns"]:
        warnings.append(
            "Kolom tidak dikenal (diabaikan): "
            + ", ".join(header_check["unknown_columns"])
        )
    if header_check["duplicate_columns"]:
        warnings.append(
            "Kolom duplikat: " + ", ".join(header_check["duplicate_columns"])
        )

    data_rows = [
        row for row in rows[1:] if any(str(cell).strip() for cell in row)
    ]
    if not data_rows:
        warnings.append("File hanya berisi header, belum ada baris data.")

    lookup = alias_lookup(item["fields"])
    canonical = [lookup.get(canonical_key(header)) for header in headers]
    preview: list[dict] = []
    for row in data_rows[:5]:
        mapped: dict[str, str] = {}
        for index, name in enumerate(canonical):
            if name and index < len(row):
                mapped[name] = row[index]
        preview.append(mapped)

    status = "error" if errors else ("warning" if warnings else "ok")

    return {
        "key": item["key"],
        "filename": item["filename"],
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "encoding": encoding,
        "delimiter": delimiter,
        "row_count": len(data_rows),
        "headers": headers,
        "recognized": header_check["recognized"],
        "missing_required": header_check["missing_required"],
        "missing_recommended": header_check["missing_recommended"],
        "unknown_columns": header_check["unknown_columns"],
        "duplicate_columns": header_check["duplicate_columns"],
        "preview": preview,
    }


def validate_uploads(contents: dict[str, bytes | None]) -> dict:
    files: dict[str, dict] = {}
    missing: list[str] = []

    for item in FILES:
        content = contents.get(item["key"])
        if content is None:
            missing.append(item["filename"])
        files[item["filename"]] = validate_file(content, item)

    ok = not missing and all(
        result["status"] != "error" for result in files.values()
    )

    return {"ok": ok, "files": files, "missing_files": missing}
