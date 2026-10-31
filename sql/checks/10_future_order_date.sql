-- name: future_order_date
-- category: validity
-- severity: critical
-- table: orders
-- description: Tanggal order tidak boleh melewati tanggal acuan (data masa depan).
SELECT order_id, order_date
FROM orders
WHERE order_date IS NOT NULL
  AND order_date > :as_of;
