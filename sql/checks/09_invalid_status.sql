-- name: invalid_status
-- category: validity
-- severity: critical
-- table: orders
-- description: status order harus salah satu dari COMPLETED, PENDING, CANCELLED, REFUNDED.
SELECT order_id, status
FROM orders
WHERE status IS NULL
   OR status NOT IN ('COMPLETED', 'PENDING', 'CANCELLED', 'REFUNDED');
