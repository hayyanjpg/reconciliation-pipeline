-- name: duplicate_payment_per_order
-- category: uniqueness
-- severity: critical
-- table: payments
-- description: Satu order seharusnya hanya punya satu pembayaran valid. Lebih dari satu berarti double charge.
SELECT order_id, COUNT(*) AS payment_count
FROM payments
WHERE status <> 'FAILED'
GROUP BY order_id
HAVING COUNT(*) > 1
ORDER BY payment_count DESC;
