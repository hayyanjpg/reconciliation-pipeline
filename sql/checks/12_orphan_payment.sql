-- name: orphan_payment
-- category: consistency
-- severity: critical
-- table: payments
-- description: Pembayaran harus selalu merujuk ke order yang ada (integritas referensial).
SELECT p.payment_id, p.order_id, p.paid_amount, p.status
FROM payments p
LEFT JOIN orders_dedup o ON o.order_id = p.order_id
WHERE o.order_id IS NULL;
