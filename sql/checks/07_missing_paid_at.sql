-- name: missing_paid_at
-- category: completeness
-- severity: warning
-- table: payments
-- description: paid_at wajib ada untuk pembayaran yang sudah berstatus PAID.
SELECT payment_id, order_id, status
FROM payments
WHERE paid_at IS NULL
  AND status = 'PAID';
