# CV dan LinkedIn

## 1. Bullet CV (pilih 4-5)

- Membangun pipeline Data Quality Assurance untuk 230 baris data order/payment
  multichannel; menormalisasi 3 format sumber (tanggal, nominal, channel) dan
  mendeteksi 7 baris duplikat, 6 orphan payment, serta 12 mismatch nominal.
- Menyusun 16 SQL check untuk uniqueness, completeness, validity, consistency,
  dan timeliness dengan output JSON/Markdown dan tabel quarantine.
- Melakukan rekonsiliasi order vs payment dan mengkuantifikasi nominal berisiko
  sebesar Rp 5.118.000 untuk diteruskan ke tim finance.
- Menyusun SOP verifikasi data harian, matriks eskalasi P1-P3, dan template
  laporan harian yang mencakup temuan, dampak, dan tindakan.
- Menulis 29 automated test pipeline + 10 test API serta dataset bersih untuk
  membuktikan pipeline tidak menghasilkan false positive (16/16 check PASS).
- Membangun aplikasi full-stack FastAPI + React untuk upload CSV, template
  otomatis, validasi header, job async, dan dashboard hasil; SQLite lokal atau
  Postgres, dengan Docker dan Render untuk deploy.
- Membuat dashboard Streamlit dan React untuk memantau pass rate, check yang
  gagal, dan baris bermasalah lintas channel.

## 2. Ringkasan LinkedIn

> Lulusan Teknologi Informasi dengan fokus Data Quality Assurance dan analisis
> data. Terbiasa melakukan normalisasi data, rekonsiliasi antar sumber,
> validasi berbasis SQL, dan penyusunan laporan operasional. Portofolio:
> pipeline Data QA end-to-end dengan 16 SQL check, rekonsiliasi order vs
> payment, dan dashboard monitoring.

## 3. Deskripsi portofolio (pendek)

> Pipeline Data Quality Assurance untuk data order dan payment multichannel:
> normalisasi, 16 SQL check, rekonsiliasi, laporan harian, dan dashboard.
> Divalidasi dengan dataset kotor dan bersih (16/16 PASS).

## 4. Deskripsi portofolio (panjang)

> Proyek ini mensimulasikan pekerjaan harian Data QA: menerima data order dari
> dua channel dan data payment, menormalisasi format yang berbeda, lalu
> memvalidasi integritas data sebelum dipakai tim lain. Terdapat 16 SQL check
> yang mencakup duplikat, data kosong, nilai tidak valid, ketidaksesuaian
> nominal, orphan payment, dan freshness. Hasilnya berupa laporan harian,
> tabel baris bermasalah, dan dashboard Streamlit. Pada dataset uji, pipeline
> menemukan 7 baris duplikat, 3 duplikat antar channel, 6 pembayaran yatim, dan
> 12 mismatch dengan nominal berisiko Rp 5,1 juta. Pada dataset bersih, seluruh
> 16 check lulus sehingga tidak ada false positive.

## 5. Cara menaruh di CV

```text
Data Quality Assurance Portfolio - github.com/<username>/data-quality-qa-portfolio
Pipeline normalisasi + 16 SQL checks + rekonsiliasi order/payment + dashboard.
Menemukan 7 duplikat, 6 orphan payment, 12 mismatch (Rp 5,1 juta berisiko);
16/16 check PASS pada dataset bersih. Python, SQL, FastAPI, React, Tailwind,
SQLite/Postgres, Docker, pytest.
```
