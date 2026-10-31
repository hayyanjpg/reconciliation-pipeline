# Laporan Harian Data Quality - 2026-10-31

## Ringkasan

| Metrik | Nilai |
|---|---:|
| Baris order masuk | 220 |
| Order unik | 220 |
| Order matched | 220 |
| Check lulus | 16/16 (100.0%) |
| Critical check gagal | 0 |
| Estimasi nominal berisiko | Rp 0 |

## Temuan utama

1. 0 baris order duplikat di dalam file sumber.
2. 0 order_id muncul di lebih dari satu channel.
3. 0 order dengan nominal pembayaran tidak sama dengan order.
4. 0 order belum memiliki pembayaran valid.
5. 0 pembayaran tidak memiliki order induk.
6. 0 order menerima lebih dari satu pembayaran valid.

## Rekomendasi

- Terapkan constraint unik pada order_id dan idempotency key saat ingest.
- Normalisasi order_id, tanggal, nominal, dan channel di staging sebelum join.
- Pisahkan baris gagal ke tabel quarantine, jangan dibuang diam-diam.
- Tambahkan monitoring harian untuk duplikat, orphan payment, dan selisih nominal.
- Buat rekonsiliasi otomatis antara order dan payment sebelum laporan ke finance.

## Status

**AMAN.** Semua critical check lulus.

## Artefak

- `reports/dq_summary.json` - hasil semua check
- `reports/dq_summary.md` - tabel check
- `reports/processed/*.csv` - baris matched, mismatch, orphan, duplikat

