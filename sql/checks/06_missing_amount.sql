-- name: missing_amount
-- category: completeness
-- severity: critical
-- table: orders
-- description: amount kosong atau tidak bisa diparse menjadi angka.
SELECT order_id, raw_amount
FROM orders
WHERE amount IS NULL;
