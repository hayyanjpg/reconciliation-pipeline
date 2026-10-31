-- name: non_positive_amount
-- category: validity
-- severity: critical
-- table: orders
-- description: Nominal order harus lebih besar dari nol.
SELECT order_id, amount
FROM orders
WHERE amount IS NOT NULL AND amount <= 0;
