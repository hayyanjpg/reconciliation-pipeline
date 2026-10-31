from __future__ import annotations

import csv


def decode_csv(content: bytes) -> tuple[str, str, list[str]]:
    try:
        return content.decode("utf-8-sig"), "utf-8", []
    except UnicodeDecodeError:
        return (
            content.decode("cp1252", errors="replace"),
            "cp1252",
            ["Encoding bukan UTF-8. Simpan ulang sebagai CSV UTF-8 agar aman."],
        )


def sniff_delimiter(text: str) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    if lines:
        counts = {delimiter: lines[0].count(delimiter) for delimiter in ",;\t|"}
        best = max(counts, key=counts.get)
        if counts[best]:
            return best

    sample = "\n".join(lines[:10])
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","
