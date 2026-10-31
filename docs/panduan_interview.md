# Panduan Interview

Dokumen ini membantu menjelaskan proyek secara meyakinkan, bukan menghafal.

## 1. Pitch 60 detik

> "Saya membuat pipeline Data Quality Assurance untuk data order dan payment
> multichannel. Pipeline menormalisasi id, tanggal, nominal, dan channel dari
> dua format file yang berbeda, lalu menjalankan 16 SQL check untuk duplikat,
> completeness, validity, consistency, dan timeliness. Setelah itu saya
> rekonsiliasi order vs payment untuk menemukan mismatch, orphan payment, dan
> pembayaran ganda. Hasilnya berupa laporan harian dan dashboard. Pada data uji,
> pipeline menemukan 7 baris duplikat, 6 pembayaran yatim, dan 12 mismatch
> dengan nominal berisiko Rp 5,1 juta. Pada dataset bersih, 16 dari 16 check
> lulus, jadi tidak ada false positive. Saya juga membangun versi full-stack
> FastAPI + React agar orang bisa upload CSV sendiri, mendapat validasi format,
> dan melihat hasilnya tanpa menjalankan kode."

## 2. Pertanyaan yang mungkin muncul

**Kenapa pakai SQL check, bukan hanya pandas?**
Karena aturan kualitas data lebih mudah diaudit dan dipindahkan ke database
produksi. SQL juga memaksa saya memikirkan join, duplikasi, dan tipe data.

**Bagaimana kamu menangani data duplikat?**
Saya normalisasi kunci lebih dulu (huruf besar, hapus spasi), lalu dedup di
dalam file dan deteksi duplikat antar channel. Baris duplikat tidak dibuang
diam-diam; dicatat di laporan.

**Apa bedanya orphan payment dan order tanpa pembayaran?**
Orphan payment adalah pembayaran yang tidak punya order induk. Order tanpa
pembayaran adalah order yang belum dibayar. Dua arah berbeda, penanganannya
juga berbeda.

**Bagaimana kamu tahu check-nya tidak false positive?**
Saya membuat dataset bersih terpisah dan menjalankan pipeline yang sama. Hasilnya
16 dari 16 check PASS. Itu juga saya jadikan automated test.

**Kalau ada 1 juta baris, apa yang berubah?**
Pindah dari SQLite ke PostgreSQL, tambahkan index pada kolom join, proses
inkremental per hari, dan jalankan check secara terjadwal. Query yang sama
tetap dipakai.

**Bagaimana kamu prioritaskan temuan?**
Berdasarkan severity dan dampak nominal. Orphan payment dan nominal negatif
masuk P1 karena langsung memengaruhi uang. Missing customer_id masuk P3.

**Kenapa upload divalidasi sebelum pipeline dijalankan?**
Supaya file yang salah format tidak menghasilkan error membingungkan. User
langsung melihat kolom yang hilang, encoding, delimiter, jumlah baris, dan
preview lima baris. Job baru dibuat jika tidak ada error.

**Kenapa job pipeline dibuat async?**
Pipeline bisa memakan waktu. Endpoint upload mengembalikan `202` dan frontend
polling status `queued/running/succeeded`, jadi request tidak timeout dan UI
tetap responsif.

**Bagaimana template CSV dan validasi tetap konsisten?**
Keduanya membaca satu definisi skema di `src/dq/schema.py`, yang juga dipakai
loader. Tidak ada duplikasi aturan kolom yang bisa berbeda versi.

**Bagaimana data user dilindungi?**
File disimpan sementara, dihapus otomatis setelah 24 jam, ukuran dibatasi, dan
tidak ada data sensitif di repo publik. Untuk produksi nyata, storage lokal
diganti S3/Supabase dengan TTL dan autentikasi.

**Apa yang belum kamu kerjakan?**
Autentikasi, alerting otomatis, scheduler, dan integrasi ke data warehouse.
Saya sengaja membatasi scope agar pipeline bisa diverifikasi end-to-end.

## 3. Yang harus dihindari

- Jangan klaim "menguasai Airflow/Kafka/Spark" jika belum pernah menjalankan.
- Jangan menyebut angka tanpa bisa menjelaskan asalnya.
- Jangan bilang "semua otomatis" jika masih ada langkah manual.
- Jangan menyalahkan data sumber; tunjukkan kontrol yang bisa kamu tambahkan.

## 4. Pertanyaan untuk interviewer

- Data source apa saja yang harus diverifikasi setiap hari?
- Seberapa sering data dikirim ulang oleh tim sumber?
- Apakah sudah ada definisi resmi untuk status order dan payment?
- Siapa yang menjadi pemilik keputusan saat data source salah?
- Tool apa yang dipakai untuk pelaporan harian saat ini?
