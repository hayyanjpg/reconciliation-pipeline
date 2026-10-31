from dq.reconcile import reconcile


def order(order_id, source_file, channel, amount=100):
    return {
        "order_id": order_id,
        "source_file": source_file,
        "channel": channel,
        "amount": amount,
        "customer_id": "CUST-001",
        "order_date": "2026-10-01",
        "status": "COMPLETED",
    }


def payment(payment_id, order_id, amount=100, status="PAID"):
    return {
        "payment_id": payment_id,
        "order_id": order_id,
        "paid_amount": amount,
        "status": status,
        "paid_at": "2026-10-02",
    }


def test_reconcile_classifies_all_cases():
    orders = [
        order("A", "orders_web.csv", "WEB"),
        order("A", "orders_app.csv", "APP"),
        order("B", "orders_web.csv", "WEB"),
        order("B", "orders_web.csv", "WEB"),
        order("C", "orders_web.csv", "WEB"),
        order("D", "orders_web.csv", "WEB"),
    ]
    payments = [
        payment("P1", "A", 100),
        payment("P2", "B", 100),
        payment("P3", "D", 50),
        payment("P4", "E", 100),
        payment("P5", "C", 100, status="FAILED"),
    ]

    result = reconcile(orders, payments)
    summary = result["summary"]

    assert summary["unique_orders"] == 4
    assert summary["duplicate_order_rows"] == 1
    assert summary["cross_channel_duplicates"] == 1
    assert summary["matched_orders"] == 2
    assert summary["amount_mismatch"] == 1
    assert summary["order_without_payment"] == 1
    assert summary["orphan_payments"] == 1
    assert summary["duplicate_payments"] == 0
    assert summary["amount_at_risk"] == 250


def test_reconcile_detects_duplicate_payment():
    orders = [order("A", "orders_web.csv", "WEB")]
    payments = [
        payment("P1", "A", 100),
        payment("P2", "A", 100),
    ]

    result = reconcile(orders, payments)
    summary = result["summary"]

    assert summary["duplicate_payments"] == 1
    assert summary["amount_mismatch"] == 1
    assert summary["matched_orders"] == 0
    assert summary["mismatch_abs_amount"] == 100
