from __future__ import annotations

from dq.loader import load_orders, load_payments


def test_loader_handles_semicolon_and_cp1252(tmp_path):
    orders_web = (
        "order_id;customer_id;order_date;amount;status;channel\n"
        "ORD-1;Cust-é;2026-10-01;10.000,00;paid;web\n"
    )
    (tmp_path / "orders_web.csv").write_bytes(orders_web.encode("cp1252"))
    (tmp_path / "orders_app.csv").write_bytes(
        b"order_id;customer_id;order_date;amount;status;channel\n"
    )
    payments = (
        "payment_id;order_id;paid_at;paid_amount;method;status\n"
        "PAY-1;ORD-1;2026-10-01;10.000,00;bank;paid\n"
    )
    (tmp_path / "payments.csv").write_bytes(payments.encode("cp1252"))

    orders, rejected = load_orders(tmp_path)
    assert not rejected
    assert orders[0]["order_id"] == "ORD-1"
    assert orders[0]["customer_id"] == "CUST-É"
    assert orders[0]["amount"] == 10000

    loaded_payments, rejected_payments = load_payments(tmp_path)
    assert not rejected_payments
    assert loaded_payments[0]["payment_id"] == "PAY-1"
    assert loaded_payments[0]["paid_amount"] == 10000
