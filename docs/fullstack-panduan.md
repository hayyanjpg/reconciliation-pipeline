# Panduan Full Stack - Apa yang Kamu Kerjakan

Dokumen ini memisahkan **bagian teknis yang sudah dibuat** dan **pekerjaan kamu**
sebagai pemilik portofolio. Tujuannya agar kamu bisa menjelaskan proyek ini
dengan jujur saat interview, bukan sekadar mengirim link.

## 1. Yang sudah tersedia

- Backend FastAPI: upload, validasi header, job async, hasil, unduh artefak.
- Frontend React + Tailwind + Recharts: hero, upload 3 file, template CSV,
  panduan format, progress, KPI, chart, tabel temuan, unduh laporan.
- Template CSV otomatis dari satu skema (`src/dq/schema.py`).
- Validasi: kolom wajib/disarankan, encoding, delimiter, duplikat header,
  preview 5 baris, jumlah baris.
- Database SQLite lokal, bisa diganti Postgres lewat `DATABASE_URL`.
- TTL cleanup: file dan hasil dihapus otomatis (default 24 jam).
- 10 test API + 29 test pipeline/dashboard.
- Dockerfile dan `render.yaml` untuk deploy.

## 2. Kerjaan kamu (yang tidak bisa diwakilkan)

### A. Jalankan dan pahami (30-45 menit)

- [ ] Jalankan backend + frontend, buka `http://127.0.0.1:5173`.
- [ ] Klik **Coba data demo**, pastikan muncul 12,5% pass rate dan Rp 5.118.000.
- [ ] Unduh template ZIP, buka di Excel, lalu upload ketiga file.
- [ ] Klik **Validasi**, lihat preview dan status per file.
- [ ] Klik **Jalankan pipeline**, cek tab Checks, Rekonsiliasi, Data, Artefak.
- [ ] Coba upload file yang kolomnya dihapus, pastikan muncul error yang jelas.
- [ ] Buka `http://127.0.0.1:8000/docs`, lihat daftar endpoint.

### B. Publikasikan (30-60 menit)

- [ ] Buat repo GitHub baru (public), lalu dari root repo:

```powershell
git init
git add .
git commit -m "Data Quality Studio: full-stack data quality portfolio"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

- [ ] Deploy ke Render: **New > Blueprint**, pilih repo, Render membaca
      `render.yaml` (Docker + Postgres). Tunggu build selesai.
- [ ] Buka URL publik, ulangi checklist demo di atas.
- [ ] Cek `/api/health` mengembalikan `{"status":"ok"}`.

### C. Siapkan bukti (30 menit)

- [ ] Screenshot: hero + upload, validasi error, dashboard hasil, tab checks.
- [ ] Rekam video 60-90 detik: demo data, upload template, jalankan, tunjukkan
      satu temuan dan satu unduhan laporan.
- [ ] Tempel link demo + repo di CV dan jawaban lamaran.
- [ ] Pastikan README menampilkan link demo di bagian paling atas.

### D. Lamar (15 menit)

- [ ] Buka lowongan MagangHub Data Quality Assurance Nolimit Teknologi.
- [ ] Isi lamaran, lampirkan CV, cantumkan link demo dan repo.
- [ ] Kirim sebelum **4 November 2026**.
- [ ] Simpan bukti lamaran (screenshot/email).

### E. Latihan interview (45 menit)

Baca `docs/panduan_interview.md`, lalu latih 5 jawaban ini:

1. **Kenapa pakai validasi sebelum pipeline?**
   Agar file yang salah format tidak menghasilkan error membingungkan; user
   dapat pesan kolom yang hilang dan preview sebelum job berjalan.
2. **Kenapa job dibuat async?**
   Pipeline bisa beberapa detik sampai menit. Request upload langsung
   mengembalikan `202` dan frontend polling status, sehingga UI tidak timeout.
3. **Kenapa template dan validasi dari satu skema?**
   `src/dq/schema.py` mencegah template, validasi, dan loader berbeda versi.
4. **Bagaimana data user dilindungi?**
   File disimpan sementara, dihapus setelah 24 jam, tidak ada data sensitif di
   repo publik, dan ukuran file dibatasi.
5. **Apa batasannya?**
   Storage masih lokal (bisa hilang saat restart), belum ada autentikasi, dan
   belum ada alerting. Sebutkan ini sebagai next step, bukan kelemahan tersembunyi.

## 3. Perintah penting

```powershell
# dev: dua server
powershell -ExecutionPolicy Bypass -File scripts\run_fullstack.ps1

# produksi lokal: satu server
powershell -ExecutionPolicy Bypass -File scripts\run_fullstack_prod.ps1

# test
python -m pytest -q
cd fullstack\backend; python -m pytest -q
cd ..\frontend; npm run typecheck; npm run build
```

## 4. Checklist verifikasi sebelum lamar

- [ ] Demo berjalan dari URL publik (bukan localhost).
- [ ] Upload template sukses dan hasil 12,5% / 16 check.
- [ ] Upload data bersih menghasilkan 16/16 PASS (gunakan `data/clean` bila perlu).
- [ ] Validasi menolak file tanpa `order_id` dengan pesan jelas.
- [ ] Tombol unduh JSON, laporan, dan CSV berfungsi.
- [ ] Tampilan rapi di layar HP.
- [ ] Tidak ada error di log Render.
- [ ] Repo tidak berisi `node_modules`, `storage`, `.env`, atau data sensitif.

## 5. Yang jangan diklaim

- Jangan bilang "saya coding semuanya sendiri" jika memang dibantu. Yang jujur:
  "Saya merancang alur dan aturan DQ, lalu mengimplementasikan dan memverifikasi
  dengan bantuan AI; saya bisa menjelaskan setiap bagian."
- Jangan sebut sudah dipakai perusahaan atau data nyata. Ini dataset sintetis.
- Jangan sebut production-grade: sebutkan batasan storage, auth, dan alerting.

## 6. Estimasi waktu

| Kegiatan | Waktu |
|---|---|
| Jalankan + pahami | 30-45 menit |
| Push GitHub + deploy | 30-60 menit |
| Screenshot + video | 30 menit |
| Lamar | 15 menit |
| Latihan interview | 45 menit |

Total realistis: **2,5-3 jam**. Sisakan waktu sebelum deadline 4 November 2026.
