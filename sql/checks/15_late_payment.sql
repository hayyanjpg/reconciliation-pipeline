-- name: late_payment
-- category: timeliness
-- severity: info
-- table: payments
-- description: Pembayaran yang lebih dari 7 hari setelah order perlu ditinjau.
SELECT
    p.payment_id,
    p.order_id,
    p.paid_at,
    o.order_date,
    CAST(julianday(p.paid_at) - julianday(o.order_date) AS INTEGER) AS days_late
FROM payments p
JOIN orders_dedup o ON o.order_id = p.order_id
WHERE p.paid_at IS NOT NULL
  AND o.order_date IS NOT NULL
  AND julianday(p.paid_at) - julianday(o.order_date) > :late_payment_days
ORDER BY days_late DESC;
