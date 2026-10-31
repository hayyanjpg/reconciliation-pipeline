"""Definisi skema sumber data - satu sumber kebenaran.

Dipakai oleh loader, validasi upload, dan generator template CSV agar
format file, validasi, dan pipeline tidak pernah berbeda versi.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile

ORDER_FIELDS = [
    {
        "name": "order_id",
        "required": True,
        "recommended": True,
        "aliases": ["order_id", "orderId", "id"],
        "example": "ORD-1001",
        "description": "ID unik order. Wajib ada di setiap baris.",
    },
    {
        "name": "customer_id",
        "required": False,
        "recommended": True,
        "aliases": ["customer_id", "customerId", "cust_id"],
        "example": "CUST-001",
        "description": "ID pelanggan untuk penelusuran.",
    },
    {
        "name": "order_date",
        "required": False,
        "recommended": True,
        "aliases": ["order_date", "orderDate", "date"],
        "example": "2026-10-01",
        "description": "Tanggal order. Format bebas yang didukung normalisasi.",
    },
    {
        "name": "amount",
        "required": False,
        "recommended": True,
        "aliases": ["amount", "total", "grand_total"],
        "example": "150000",
        "description": "Nominal order. Boleh Rp 150.000 atau 150000.",
    },
    {
        "name": "status",
        "required": False,
        "recommended": True,
        "aliases": ["status", "order_status"],
        "example": "COMPLETED",
        "description": "COMPLETED, PENDING, CANCELLED, atau REFUNDED.",
    },
    {
        "name": "channel",
        "required": False,
        "recommended": False,
        "aliases": ["channel", "source"],
        "example": "WEB",
        "description": "Kosongkan jika sudah dipisah per file web/app.",
    },
]

PAYMENT_FIELDS = [
    {
        "name": "payment_id",
        "required": True,
        "recommended": True,
        "aliases": ["payment_id", "paymentId", "id"],
        "example": "PAY-9001",
        "description": "ID unik pembayaran. Wajib ada di setiap baris.",
    },
    {
        "name": "order_id",
        "required": True,
        "recommended": True,
        "aliases": ["order_id", "orderId"],
        "example": "ORD-1001",
        "description": "Order yang dibayar. Harus merujuk ke order yang ada.",
    },
    {
        "name": "paid_at",
        "required": False,
        "recommended": True,
        "aliases": ["paid_at", "payment_date", "date"],
        "example": "2026-10-01",
        "description": "Tanggal pembayaran.",
    },
    {
        "name": "paid_amount",
        "required": False,
        "recommended": True,
        "aliases": ["paid_amount", "amount", "nominal"],
        "example": "150000",
        "description": "Nominal yang dibayar.",
    },
    {
        "name": "method",
        "required": False,
        "recommended": False,
        "aliases": ["method", "payment_method"],
        "example": "BCA_VA",
        "description": "Metode pembayaran (bebas).",
    },
    {
        "name": "status",
        "required": False,
        "recommended": True,
        "aliases": ["status", "payment_status"],
        "example": "PAID",
        "description": "PAID, PENDING, atau FAILED.",
    },
]

FILES = [
    {
        "key": "orders_web",
        "filename": "orders_web.csv",
        "label": "Order - Web",
        "description": "Order dari channel web.",
        "fields": ORDER_FIELDS,
        "example": {
            "order_id": "ORD-1001",
            "customer_id": "CUST-001",
            "order_date": "2026-10-01",
            "amount": "150000",
            "status": "COMPLETED",
            "channel": "WEB",
        },
    },
    {
        "key": "orders_app",
        "filename": "orders_app.csv",
        "label": "Order - App",
        "description": "Order dari channel aplikasi.",
        "fields": ORDER_FIELDS,
        "example": {
            "order_id": "ORD-1002",
            "customer_id": "CUST-002",
            "order_date": "31/10/2026",
            "amount": "Rp 99.000",
            "status": "PENDING",
            "channel": "APP",
        },
    },
    {
        "key": "payments",
        "filename": "payments.csv",
        "label": "Pembayaran",
        "description": "Pembayaran untuk order di kedua channel.",
        "fields": PAYMENT_FIELDS,
        "example": {
            "payment_id": "PAY-9001",
            "order_id": "ORD-1001",
            "paid_at": "2026-10-01",
            "paid_amount": "150000",
            "method": "BCA_VA",
            "status": "PAID",
        },
    },
]

ACCEPTED_FORMATS = {
    "amount": [
        "45000",
        "45.000",
        "45,000",
        "Rp 45.000",
        "1.500.000,00",
        "(75.000) untuk negatif",
    ],
    "date": [
        "2026-10-31",
        "31/10/2026",
        "31-10-2026",
        "2026/10/31",
        "31 Oct 2026",
        "31 October 2026",
    ],
    "status_order": ["COMPLETED", "PENDING", "CANCELLED", "REFUNDED"],
    "status_payment": ["PAID", "PENDING", "FAILED"],
    "channel": ["WEB", "APP", "web", "app", "website", "android", "ios", "aplikasi"],
    "encoding": ["UTF-8", "UTF-8 with BOM"],
    "delimiter": ["koma", "titik koma", "tab"],
}


def canonical_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def canonical_headers(fields: list[dict]) -> list[str]:
    return [field["name"] for field in fields]


def alias_lookup(fields: list[dict]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for field in fields:
        for alias in field["aliases"]:
            lookup[canonical_key(alias)] = field["name"]
    return lookup


def validate_header_list(headers: list[str], fields: list[dict]) -> dict:
    lookup = alias_lookup(fields)
    recognized: list[str] = []
    unknown: list[str] = []
    duplicates: list[str] = []

    for header in headers:
        if not str(header).strip():
            continue
        name = lookup.get(canonical_key(str(header)))
        if name is None:
            unknown.append(str(header).strip())
        else:
            if name in recognized and name not in duplicates:
                duplicates.append(name)
            recognized.append(name)

    required = {field["name"] for field in fields if field["required"]}
    recommended = {
        field["name"]
        for field in fields
        if field["recommended"] and not field["required"]
    }

    return {
        "recognized": recognized,
        "unknown_columns": unknown,
        "duplicate_columns": duplicates,
        "missing_required": sorted(required - set(recognized)),
        "missing_recommended": sorted(recommended - set(recognized)),
    }


def template_csv(fields: list[dict], example: dict, delimiter: str = ",") -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=delimiter, lineterminator="\n")
    names = canonical_headers(fields)
    writer.writerow(names)
    writer.writerow([example.get(name, "") for name in names])
    return buffer.getvalue()


TEMPLATE_README = """# Template Data Quality

Tiga file CSV di dalam arsip ini adalah contoh format minimal.

- orders_web.csv : order dari channel web
- orders_app.csv : order dari channel aplikasi
- payments.csv   : pembayaran untuk order di kedua channel

## Aturan penting

1. Baris pertama harus header. Nama kolom boleh memakai alias
   (mis. orderId untuk order_id), tetapi header template ini paling aman.
2. order_id wajib ada dan unik setelah normalisasi.
3. payment_id dan order_id wajib ada di payments.csv.
4. Nominal boleh ditulis 45000, 45.000, Rp 45.000, atau 1.500.000,00.
5. Tanggal boleh 2026-10-31, 31/10/2026, 31-10-2026, atau 31 Oct 2026.
6. Status order: COMPLETED, PENDING, CANCELLED, REFUNDED.
   Status pembayaran: PAID, PENDING, FAILED.
7. Simpan sebagai CSV UTF-8 dengan pemisah koma.

Isi data boleh berbeda-beda; yang harus sama adalah struktur kolomnya.
"""


def template_zip() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("README.md", TEMPLATE_README)
        for item in FILES:
            content = template_csv(item["fields"], item["example"])
            archive.writestr(item["filename"], content)
    return buffer.getvalue()


def file_definition(key: str) -> dict | None:
    for item in FILES:
        if item["key"] == key:
            return item
    return None


def schema_payload() -> dict:
    return {
        "files": [
            {
                "key": item["key"],
                "filename": item["filename"],
                "label": item["label"],
                "description": item["description"],
                "fields": item["fields"],
                "example": item["example"],
            }
            for item in FILES
        ],
        "accepted_formats": ACCEPTED_FORMATS,
    }
