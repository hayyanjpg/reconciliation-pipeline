-- Template "general request" untuk menarik data order + status pembayaran.
-- Parameter: :start_date, :end_date, :channel (isi 'ALL' untuk semua channel).
-- Dipakai untuk menjawab permintaan data harian dari tim lain.

SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.channel,
    o.amount              AS order_amount,
    o.status              AS order_status,
    COALESCE(SUM(p.paid_amount), 0) AS paid_amount,
    CASE
        WHEN COUNT(p.payment_id) = 0 THEN 'UNPAID'
        WHEN SUM(p.paid_amount) = o.amount THEN 'PAID'
        ELSE 'PARTIAL'
    END                   AS payment_state
FROM orders_dedup o
LEFT JOIN payments p
       ON p.order_id = o.order_id
      AND p.status <> 'FAILED'
WHERE o.order_date BETWEEN :start_date AND :end_date
  AND (:channel = 'ALL' OR o.channel = :channel)
GROUP BY
    o.order_id, o.customer_id, o.order_date, o.channel, o.amount, o.status
ORDER BY o.order_date, o.order_id;
