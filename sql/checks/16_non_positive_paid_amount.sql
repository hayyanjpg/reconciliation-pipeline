-- name: non_positive_paid_amount
-- category: validity
-- severity: critical
-- table: payments
-- description: Nominal pembayaran tidak boleh negatif atau nol.
SELECT payment_id, order_id, paid_amount
FROM payments
WHERE paid_amount IS NOT NULL
  AND paid_amount <= 0;
