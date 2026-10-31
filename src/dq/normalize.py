from __future__ import annotations

import re
from datetime import date, datetime

DATE_FORMATS = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
    "%d %b %Y",
    "%d %B %Y",
)

CHANNEL_MAP = {
    "web": "WEB",
    "website": "WEB",
    "situs": "WEB",
    "app": "APP",
    "apps": "APP",
    "android": "APP",
    "ios": "APP",
    "aplikasi": "APP",
}


def normalize_id(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    text = re.sub(r"\s+", "", text)
    return text or None


def normalize_amount(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(round(value))

    text = str(value).strip()
    if not text:
        return None

    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    text = re.sub(r"(?i)\brp\.?\b|\bidr\b", "", text).strip()
    text = text.replace(" ", "")
    if not text:
        return None

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        parts = text.split(",")
        if len(parts[-1]) in (1, 2):
            text = "".join(parts[:-1]).replace(".", "") + "." + parts[-1]
        else:
            text = text.replace(",", "")
    elif "." in text:
        parts = text.split(".")
        if len(parts) > 1 and len(parts[-1]) == 3:
            text = "".join(parts)

    try:
        amount = float(text)
    except ValueError:
        return None

    amount = int(round(amount))
    return -amount if negative else amount


def normalize_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    if not text:
        return None
    if "T" in text:
        text = text.split("T", 1)[0]
    elif " " in text:
        text = text.split(" ", 1)[0]

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(str(value)).date()
    except ValueError:
        return None


def normalize_channel(value, default: str | None = None) -> str:
    if value is None or not str(value).strip():
        return default or "UNKNOWN"
    key = str(value).strip().lower()
    return CHANNEL_MAP.get(key, str(value).strip().upper())


def normalize_status(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    return text or None
