-- name: amount_mismatch
-- category: consistency
-- severity: critical
-- table: orders_dedup
-- description: Total pembayaran valid harus sama dengan nominal order (toleransi dapat diatur).
SELECT
    o.order_id,
    o.amount AS order_amount,
    SUM(p.paid_amount) AS paid_amount,
    SUM(p.paid_amount) - o.amount AS difference
FROM orders_dedup o
JOIN payments p ON p.order_id = o.order_id
WHERE p.status <> 'FAILED'
GROUP BY o.order_id, o.amount
HAVING ABS(SUM(p.paid_amount) - o.amount) > :tolerance
ORDER BY ABS(SUM(p.paid_amount) - o.amount) DESC;
