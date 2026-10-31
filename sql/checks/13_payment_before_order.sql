-- name: payment_before_order
-- category: consistency
-- severity: warning
-- table: payments
-- description: Tanggal pembayaran tidak boleh lebih awal dari tanggal order.
SELECT p.payment_id, p.order_id, p.paid_at, o.order_date
FROM payments p
JOIN orders_dedup o ON o.order_id = p.order_id
WHERE p.paid_at IS NOT NULL
  AND o.order_date IS NOT NULL
  AND p.paid_at < o.order_date;
