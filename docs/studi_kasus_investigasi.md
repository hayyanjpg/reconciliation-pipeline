# Studi Kasus: Selisih Omzet 2,3% antara Dashboard dan Finance

Dokumen ini meniru alur investigasi awal atas keluhan teknis, salah satu
tanggung jawab posisi Data Quality Assurance.

## 1. Keluhan

> "Angka omzet di dashboard lebih tinggi 2,3% dibanding laporan finance untuk
> periode yang sama. Mohon dicek."

Yang dilaporkan hanya gejala. Tugas Data QA adalah mengubah gejala menjadi
hipotesis yang bisa diuji.

## 2. Informasi awal yang dikumpulkan

- Periode: 1-30 Oktober 2026.
- Sumber: 2 file order (WEB, APP) dan 1 file payment.
- Volume: 230 baris order, 220 order unik, 214 baris payment.
- Selisih yang dilaporkan: sekitar 2,3% dari omzet.

## 3. Hipotesis

| # | Hipotesis | Cara uji |
|---|---|---|
| H1 | Ada order duplikat sehingga omzet terhitung dua kali | Cek `duplicate_order_id` dan duplikat antar channel |
| H2 | Ada pembayaran tanpa order yang ikut terhitung | Cek `orphan_payment` |
| H3 | Nominal order dan payment tidak sama | Cek `amount_mismatch` |
| H4 | Ada order yang belum dibayar tetapi masuk omzet | Cek `order_without_payment` |

## 4. Temuan

Hasil pipeline pada dataset uji:

- **7 baris order duplikat** di dalam file sumber.
- **3 order_id muncul di dua channel** (WEB dan APP) sekaligus.
- **12 order** dengan total pembayaran tidak sama dengan nominal order.
- **18 order** belum memiliki pembayaran valid.
- **6 pembayaran yatim** tanpa order induk.
- **4 order** menerima lebih dari satu pembayaran valid.

Estimasi nominal berisiko: **Rp 5.118.000**.

## 5. Akar masalah

1. **Tidak ada idempotency key** saat ingest, sehingga file yang dikirim ulang
   menciptakan baris duplikat.
2. **Normalisasi tidak konsisten**: `ORD-1001`, `ord-1001`, dan ` ORD-1001 `
   dianggap entitas berbeda oleh sistem lama.
3. **Tidak ada validasi sebelum load**: baris dengan nominal negatif, status
   tidak dikenal, dan tanggal tidak valid tetap masuk.
4. **Rekonsiliasi manual**: finance mencocokkan data dengan spreadsheet,
   sehingga selisih baru terlihat di akhir bulan.

## 6. Tindakan

| Tindakan | Pemilik | Dampak |
|---|---|---|
| Dedup berdasarkan `order_id` yang sudah dinormalisasi | Tim Teknis | Menghilangkan 10 baris ganda |
| Constraint unik + foreign key di lapisan curated | Tim Teknis | Mencegah duplikat dan orphan sejak awal |
| Quarantine untuk baris gagal validasi | Data QA | Data buruk tidak lagi masuk dashboard |
| Rekonsiliasi otomatis harian | Data QA | Selisih terdeteksi di hari yang sama |
| Laporan harian berisi dampak nominal | Data QA | Finance bisa langsung menindaklanjuti |

## 7. Verifikasi perbaikan

Setelah normalisasi, dedup, dan rekonsiliasi diterapkan pada dataset bersih:

- 220 dari 220 order matched.
- 16 dari 16 check PASS (100%).
- Nominal berisiko: Rp 0.

## 8. Pelajaran

- Keluhan "angka beda" hampir selalu berakar pada definisi dan kualitas data,
  bukan pada tampilan dashboard.
- Duplikat dan orphan lebih murah dicegah di ingest daripada dibersihkan
  setiap akhir bulan.
- Laporan yang baik memuat **angka, penyebab, dampak, dan tindakan**, bukan
  hanya daftar error.
