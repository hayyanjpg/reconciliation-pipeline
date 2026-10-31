# Ringkasan Data Quality - 2026-10-31

**Pass rate:** 16/16 check (100.0%)

| Check | Kategori | Severity | Status | Baris gagal | Total baris |
|---|---|---|---|---:|---:|
| duplicate_order_id | uniqueness | critical | PASS | 0 | 220 |
| duplicate_payment_per_order | uniqueness | critical | PASS | 0 | 220 |
| missing_customer_id | completeness | warning | PASS | 0 | 220 |
| missing_order_date | completeness | critical | PASS | 0 | 220 |
| unparseable_order_date | validity | critical | PASS | 0 | 220 |
| missing_amount | completeness | critical | PASS | 0 | 220 |
| missing_paid_at | completeness | warning | PASS | 0 | 220 |
| non_positive_amount | validity | critical | PASS | 0 | 220 |
| invalid_status | validity | critical | PASS | 0 | 220 |
| future_order_date | validity | critical | PASS | 0 | 220 |
| amount_mismatch | consistency | critical | PASS | 0 | 220 |
| orphan_payment | consistency | critical | PASS | 0 | 220 |
| payment_before_order | consistency | warning | PASS | 0 | 220 |
| stale_data | timeliness | warning | PASS | 0 | 220 |
| late_payment | timeliness | info | PASS | 0 | 220 |
| non_positive_paid_amount | validity | critical | PASS | 0 | 220 |

## Detail kegagalan

Tidak ada check yang gagal.
