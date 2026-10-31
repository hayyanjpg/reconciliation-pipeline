from __future__ import annotations

from collections import defaultdict


def reconcile(orders: list[dict], payments: list[dict]) -> dict:
    seen: dict[tuple[str, str], dict] = {}
    unique_orders: list[dict] = []
    duplicate_orders: list[dict] = []

    for record in orders:
        key = (record["source_file"], record["order_id"])
        if key in seen:
            duplicate_orders.append(
                {
                    **record,
                    "duplicate_of_source": seen[key]["source_file"],
                }
            )
        else:
            seen[key] = record
            unique_orders.append(record)

    groups: dict[str, list[dict]] = defaultdict(list)
    for record in unique_orders:
        groups[record["order_id"]].append(record)

    canonical: dict[str, dict] = {}
    cross_channel: list[dict] = []
    for order_id, records in groups.items():
        canonical[order_id] = records[0]
        if len(records) > 1:
            cross_channel.append(
                {
                    "order_id": order_id,
                    "channels": ", ".join(sorted({r["channel"] for r in records})),
                    "source_files": ", ".join(
                        sorted({r["source_file"] for r in records})
                    ),
                    "rows": len(records),
                }
            )

    payments_by_order: dict[str, list[dict]] = defaultdict(list)
    for payment in payments:
        payments_by_order[payment["order_id"]].append(payment)

    matched: list[dict] = []
    amount_mismatch: list[dict] = []
    order_without_payment: list[dict] = []
    duplicate_payments: list[dict] = []

    for order_id, order in canonical.items():
        order_payments = payments_by_order.get(order_id, [])
        valid_payments = [p for p in order_payments if p["status"] != "FAILED"]

        if len(valid_payments) > 1:
            duplicate_payments.append(
                {
                    "order_id": order_id,
                    "payment_count": len(valid_payments),
                    "payment_ids": ", ".join(
                        p["payment_id"] for p in valid_payments
                    ),
                    "paid_amount": sum(
                        p["paid_amount"] or 0 for p in valid_payments
                    ),
                }
            )

        if not valid_payments:
            order_without_payment.append(order)
            continue

        paid = sum(p["paid_amount"] or 0 for p in valid_payments)
        expected = order["amount"]
        difference = paid - (expected or 0)

        if expected is not None and difference == 0:
            matched.append(
                {
                    **order,
                    "paid_amount": paid,
                    "payment_count": len(valid_payments),
                }
            )
        else:
            amount_mismatch.append(
                {
                    **order,
                    "expected_amount": expected,
                    "paid_amount": paid,
                    "difference": difference,
                    "payment_count": len(valid_payments),
                }
            )

    orphan_payments = [
        payment for payment in payments if payment["order_id"] not in canonical
    ]

    mismatch_abs = sum(abs(row["difference"]) for row in amount_mismatch)
    orphan_amount = sum(payment["paid_amount"] or 0 for payment in orphan_payments)
    unpaid_amount = sum(order["amount"] or 0 for order in order_without_payment)

    summary = {
        "total_order_rows": len(orders),
        "unique_orders": len(canonical),
        "duplicate_order_rows": len(duplicate_orders),
        "cross_channel_duplicates": len(cross_channel),
        "total_payment_rows": len(payments),
        "matched_orders": len(matched),
        "amount_mismatch": len(amount_mismatch),
        "order_without_payment": len(order_without_payment),
        "orphan_payments": len(orphan_payments),
        "duplicate_payments": len(duplicate_payments),
        "mismatch_abs_amount": mismatch_abs,
        "orphan_amount": orphan_amount,
        "unpaid_order_amount": unpaid_amount,
        "amount_at_risk": mismatch_abs + orphan_amount + unpaid_amount,
    }

    return {
        "summary": summary,
        "matched": matched,
        "amount_mismatch": amount_mismatch,
        "order_without_payment": order_without_payment,
        "orphan_payments": orphan_payments,
        "duplicate_orders": duplicate_orders,
        "duplicate_payments": duplicate_payments,
        "cross_channel_duplicates": cross_channel,
    }
