-- name: stale_data
-- category: timeliness
-- severity: warning
-- table: orders
-- description: Data terbaru tidak boleh lebih lama dari batas freshness (default 2 hari).
SELECT MAX(order_date) AS latest_order_date
FROM orders
HAVING MAX(order_date) < date(:as_of, '-' || :freshness_days || ' day');
