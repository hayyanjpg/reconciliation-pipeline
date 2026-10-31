-- name: unparseable_order_date
-- category: validity
-- severity: critical
-- table: orders
-- description: order_date ada isinya tetapi formatnya tidak dikenali sehingga gagal dinormalisasi.
SELECT order_id, raw_order_date
FROM orders
WHERE order_date IS NULL
  AND raw_order_date IS NOT NULL
  AND TRIM(raw_order_date) <> '';
