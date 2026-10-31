from datetime import date

import pytest

from dq.normalize import (
    normalize_amount,
    normalize_channel,
    normalize_date,
    normalize_id,
    normalize_status,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1500000", 1500000),
        ("Rp 1.500.000", 1500000),
        ("1.500.000,00", 1500000),
        ("1,500,000.00", 1500000),
        ("1500000.00", 1500000),
        ("-50.000", -50000),
        ("(75.000)", -75000),
        ("N/A", None),
        ("", None),
        (None, None),
    ],
)
def test_normalize_amount(raw, expected):
    assert normalize_amount(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2026-10-05", date(2026, 10, 5)),
        ("05/10/2026", date(2026, 10, 5)),
        ("05-10-2026", date(2026, 10, 5)),
        ("2026-10-05T10:00:00", date(2026, 10, 5)),
        ("2026-10-05 10:00:00", date(2026, 10, 5)),
        ("31/13/2026", None),
        ("not-a-date", None),
        ("", None),
    ],
)
def test_normalize_date(raw, expected):
    assert normalize_date(raw) == expected


def test_normalize_id_trims_and_uppercases():
    assert normalize_id(" ord-1001 ") == "ORD-1001"
    assert normalize_id("ORD 1001") == "ORD1001"
    assert normalize_id("") is None


def test_normalize_channel_maps_aliases():
    assert normalize_channel("website") == "WEB"
    assert normalize_channel("android") == "APP"
    assert normalize_channel(None, "WEB") == "WEB"


def test_normalize_status():
    assert normalize_status(" paid ") == "PAID"
    assert normalize_status("") is None
