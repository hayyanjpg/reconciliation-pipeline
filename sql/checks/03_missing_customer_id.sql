-- name: missing_customer_id
-- category: completeness
-- severity: warning
-- table: orders
-- description: customer_id wajib terisi agar order bisa ditelusuri ke pelanggan.
SELECT order_id, customer_id
FROM orders
WHERE customer_id IS NULL OR TRIM(customer_id) = '';
