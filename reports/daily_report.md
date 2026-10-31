# Laporan Harian Data Quality - 2026-10-31

## Ringkasan

| Metrik | Nilai |
|---|---:|
| Baris order masuk | 230 |
| Order unik | 220 |
| Order matched | 190 |
| Check lulus | 2/16 (12.5%) |
| Critical check gagal | 10 |
| Estimasi nominal berisiko | Rp 5,118,000 |

## Temuan utama

1. 7 baris order duplikat di dalam file sumber.
2. 3 order_id muncul di lebih dari satu channel.
3. 12 order dengan nominal pembayaran tidak sama dengan order.
4. 18 order belum memiliki pembayaran valid.
5. 6 pembayaran tidak memiliki order induk.
6. 4 order menerima lebih dari satu pembayaran valid.

## Rekomendasi

- Terapkan constraint unik pada order_id dan idempotency key saat ingest.
- Normalisasi order_id, tanggal, nominal, dan channel di staging sebelum join.
- Pisahkan baris gagal ke tabel quarantine, jangan dibuang diam-diam.
- Tambahkan monitoring harian untuk duplikat, orphan payment, dan selisih nominal.
- Buat rekonsiliasi otomatis antara order dan payment sebelum laporan ke finance.

## Status

**PERLU TINDAKAN HARI INI.** Critical check gagal: duplicate_order_id, duplicate_payment_per_order, unparseable_order_date, missing_amount, non_positive_amount, invalid_status, future_order_date, amount_mismatch, orphan_payment, non_positive_paid_amount.

## Artefak

- `reports/dq_summary.json` - hasil semua check
- `reports/dq_summary.md` - tabel check
- `reports/processed/*.csv` - baris matched, mismatch, orphan, duplikat

