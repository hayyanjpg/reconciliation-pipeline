-- name: duplicate_order_id
-- category: uniqueness
-- severity: critical
-- table: orders
-- description: order_id harus unik setelah normalisasi. Lebih dari satu baris berarti duplikat.
SELECT order_id, COUNT(*) AS occurrences
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;
