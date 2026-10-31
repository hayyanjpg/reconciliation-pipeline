# SOP Verifikasi Data Harian

Dokumen ini menjelaskan langkah operasional harian untuk memastikan data order
dan payment yang masuk konsisten, lengkap, dan siap dipakai tim lain.

## 1. Tujuan dan ruang lingkup

- Memastikan tidak ada order/payment yang hilang, ganda, atau salah nominal.
- Menjaga integritas data lintas channel (WEB dan APP).
- Menyediakan laporan harian yang bisa dipertanggungjawabkan.

Ruang lingkup: file `orders_web.csv`, `orders_app.csv`, dan `payments.csv`
dari sumber internal. Data pelanggan (PII) tidak termasuk.

## 2. Peran

| Peran | Tanggung jawab |
|---|---|
| Data QA | Menjalankan pipeline, membaca hasil check, menyusun laporan |
| Data Owner | Memutuskan koreksi data sumber dan prioritaskan perbaikan |
| Tim Finance | Menerima hasil rekonsiliasi order vs payment |
| Tim Teknis | Memperbaiki bug ingest jika ada anomali berulang |

## 3. Input

- `orders_web.csv` - order dari channel web.
- `orders_app.csv` - order dari channel aplikasi.
- `payments.csv` - pembayaran dari payment gateway.
- Tanggal acuan (`--as-of`) sesuai hari kerja berjalan.

## 4. Langkah harian

1. **Terima file (08:30).** Pastikan ketiga file tersedia dan ukurannya wajar
   dibanding hari sebelumnya (lonjakan > 30% perlu dicek).
2. **Jalankan pipeline (08:45).**
   ```bash
   python scripts/run_pipeline.py --as-of YYYY-MM-DD
   ```
3. **Baca ringkasan check (09:00).** Buka `reports/dq_summary.md`.
   Fokus pada check dengan severity `critical`.
4. **Rekonsiliasi (09:15).** Buka `reports/processed/amount_mismatch.csv`,
   `order_without_payment.csv`, dan `orphan_payments.csv`.
5. **Susun laporan (09:30).** Lengkapi `reports/daily_report.md` dengan
   penyebab dan tindakan, bukan hanya angka.
6. **Eskalasi (10:00).** Gunakan matriks di bagian 6 jika ada critical check
   yang gagal.

## 5. Kriteria lulus

| Kriteria | Ambang |
|---|---|
| Critical check | 100% PASS |
| Warning check | Maksimal 2 yang gagal |
| Freshness data | Maksimal 2 hari dari tanggal acuan |
| Amount mismatch | 0 untuk order berstatus COMPLETED |
| Orphan payment | 0 |

Jika salah satu tidak terpenuhi, data **tidak boleh** dipublikasikan ke
dashboard finance sebelum ada catatan persetujuan Data Owner.

## 6. Matriks eskalasi

| Prioritas | Kondisi | SLA | PIC |
|---|---|---|---|
| P1 | Orphan payment, duplikat massal, nominal negatif | Hari yang sama | Data Owner + Tim Teknis |
| P2 | Amount mismatch > 5 order, data stale > 2 hari | 1x24 jam | Data QA + Tim Finance |
| P3 | Missing customer_id, late payment, format tidak konsisten | 3 hari kerja | Data QA |

## 7. Output dan arsip

- `reports/dq_summary.json` - hasil mesin, dipakai dashboard.
- `reports/dq_summary.md` - tabel check untuk dibaca manusia.
- `reports/daily_report.md` - laporan harian siap kirim.
- `reports/processed/*.csv` - bukti baris matched, mismatch, orphan, duplikat.
- Arsipkan laporan minimal 90 hari untuk kebutuhan audit.

## 8. Definition of Done

- Pipeline selesai tanpa error.
- Semua critical check PASS atau sudah dieskalasi dengan catatan.
- Laporan harian memuat: jumlah data, temuan, dampak nominal, tindakan, PIC.
- Perbaikan data sumber dicatat sebagai tiket, bukan dikerjakan manual tanpa jejak.
