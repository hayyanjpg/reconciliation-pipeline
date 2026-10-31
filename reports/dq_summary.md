# Ringkasan Data Quality - 2026-10-31

**Pass rate:** 2/16 check (12.5%)

| Check | Kategori | Severity | Status | Baris gagal | Total baris |
|---|---|---|---|---:|---:|
| duplicate_order_id | uniqueness | critical | FAIL | 9 | 230 |
| duplicate_payment_per_order | uniqueness | critical | FAIL | 4 | 214 |
| missing_customer_id | completeness | warning | FAIL | 5 | 230 |
| missing_order_date | completeness | critical | PASS | 0 | 230 |
| unparseable_order_date | validity | critical | FAIL | 2 | 230 |
| missing_amount | completeness | critical | FAIL | 1 | 230 |
| missing_paid_at | completeness | warning | FAIL | 2 | 214 |
| non_positive_amount | validity | critical | FAIL | 2 | 230 |
| invalid_status | validity | critical | FAIL | 3 | 230 |
| future_order_date | validity | critical | FAIL | 2 | 230 |
| amount_mismatch | consistency | critical | FAIL | 12 | 220 |
| orphan_payment | consistency | critical | FAIL | 6 | 214 |
| payment_before_order | consistency | warning | FAIL | 2 | 214 |
| stale_data | timeliness | warning | PASS | 0 | 230 |
| late_payment | timeliness | info | FAIL | 2 | 214 |
| non_positive_paid_amount | validity | critical | FAIL | 2 | 214 |

## Detail kegagalan

### duplicate_order_id (critical) - 9 baris

order_id harus unik setelah normalisasi. Lebih dari satu baris berarti duplikat.

| order_id | occurrences |
|---|---|
| ORD-1008 | 3 |
| ORD-1001 | 2 |
| ORD-1002 | 2 |

### duplicate_payment_per_order (critical) - 4 baris

Satu order seharusnya hanya punya satu pembayaran valid. Lebih dari satu berarti double charge.

| order_id | payment_count |
|---|---|
| ORD-1121 | 2 |
| ORD-1165 | 2 |
| ORD-1211 | 2 |

### missing_customer_id (warning) - 5 baris

customer_id wajib terisi agar order bisa ditelusuri ke pelanggan.

| order_id | customer_id |
|---|---|
| ORD-1064 | None |
| ORD-1110 | None |
| ORD-1144 | None |

### unparseable_order_date (critical) - 2 baris

order_date ada isinya tetapi formatnya tidak dikenali sehingga gagal dinormalisasi.

| order_id | raw_order_date |
|---|---|
| ORD-1098 | 31/13/2026 |
| ORD-1127 | 31/13/2026 |

### missing_amount (critical) - 1 baris

amount kosong atau tidak bisa diparse menjadi angka.

| order_id | raw_amount |
|---|---|
| ORD-1086 | N/A |

### missing_paid_at (warning) - 2 baris

paid_at wajib ada untuk pembayaran yang sudah berstatus PAID.

| payment_id | order_id | status |
|---|---|---|
| PAY-0021 | ORD-1023 | PAID |
| PAY-0035 | ORD-1037 | PAID |

### non_positive_amount (critical) - 2 baris

Nominal order harus lebih besar dari nol.

| order_id | amount |
|---|---|
| ORD-1043 | -50000 |
| ORD-1217 | -50000 |

### invalid_status (critical) - 3 baris

status order harus salah satu dari COMPLETED, PENDING, CANCELLED, REFUNDED.

| order_id | status |
|---|---|
| ORD-1198 | PAID |
| ORD-1055 | PAID |
| ORD-1085 | DONE |

### future_order_date (critical) - 2 baris

Tanggal order tidak boleh melewati tanggal acuan (data masa depan).

| order_id | order_date |
|---|---|
| ORD-1100 | 2027-01-15 |
| ORD-1161 | 2027-01-15 |

### amount_mismatch (critical) - 12 baris

Total pembayaran valid harus sama dengan nominal order (toleransi dapat diatur).

| order_id | order_amount | paid_amount | difference |
|---|---|---|---|
| ORD-1121 | 199000 | 398000 | 199000 |
| ORD-1220 | 99000 | 198000 | 99000 |
| ORD-1165 | 75000 | 150000 | 75000 |

### orphan_payment (critical) - 6 baris

Pembayaran harus selalu merujuk ke order yang ada (integritas referensial).

| payment_id | order_id | paid_amount | status |
|---|---|---|---|
| PAY-0209 | ORD-9001 | 199000 | PAID |
| PAY-0210 | ORD-9002 | 350000 | PAID |
| PAY-0211 | ORD-9003 | 499000 | PAID |

### payment_before_order (warning) - 2 baris

Tanggal pembayaran tidak boleh lebih awal dari tanggal order.

| payment_id | order_id | paid_at | order_date |
|---|---|---|---|
| PAY-0159 | ORD-1170 | 2026-10-03 | 2026-10-06 |
| PAY-0009 | ORD-1009 | 2026-10-04 | 2026-10-07 |

### late_payment (info) - 2 baris

Pembayaran yang lebih dari 7 hari setelah order perlu ditinjau.

| payment_id | order_id | paid_at | order_date | days_late |
|---|---|---|---|---|
| PAY-0073 | ORD-1077 | 2026-11-03 | 2026-10-19 | 15 |
| PAY-0158 | ORD-1169 | 2026-10-22 | 2026-10-07 | 15 |

### non_positive_paid_amount (critical) - 2 baris

Nominal pembayaran tidak boleh negatif atau nol.

| payment_id | order_id | paid_amount |
|---|---|---|
| PAY-0041 | ORD-1043 | -50000 |
| PAY-0204 | ORD-1217 | -50000 |

