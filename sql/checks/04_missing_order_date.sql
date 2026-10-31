-- name: missing_order_date
-- category: completeness
-- severity: critical
-- table: orders
-- description: order_date kosong total di file sumber.
SELECT order_id, raw_order_date
FROM orders
WHERE order_date IS NULL
  AND (raw_order_date IS NULL OR TRIM(raw_order_date) = '');
