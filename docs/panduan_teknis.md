# Panduan Teknis

Panduan menjalankan, memahami, dan mengembangkan pipeline.

## 1. Prasyarat

- Python 3.10 atau lebih baru.
- Tidak butuh Docker, PostgreSQL, atau API key.
- SQLite sudah termasuk di Python standar.

## 2. Instalasi

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## 3. Menjalankan

```bash
# 1) Buat dataset uji (dirty) dan dataset bersih
python scripts/generate_sample_data.py
python scripts/generate_sample_data.py --clean

# 2) Jalankan pipeline pada data uji
python scripts/run_pipeline.py --as-of 2026-10-31

# 3) Jalankan pada data bersih (uji false positive)
python scripts/run_pipeline.py --raw-dir data/clean --out-dir reports_clean --as-of 2026-10-31

# 4) Test
python -m pytest -q

# 5) Dashboard
streamlit run streamlit/dashboard.py
```

Argumen penting:

| Argumen | Arti |
|---|---|
| `--raw-dir` | Folder input (default `data/raw`) |
| `--out-dir` | Folder output (default `reports`) |
| `--as-of` | Tanggal acuan untuk check future date dan freshness |

## 4. Data dictionary

### orders_web.csv / orders_app.csv

| Kolom | Tipe | Catatan |
|---|---|---|
| order_id | teks | Kunci order, dinormalisasi ke huruf besar tanpa spasi |
| customer_id | teks | Boleh kosong pada data uji untuk check completeness |
| order_date | tanggal | WEB: `YYYY-MM-DD`, APP: `DD/MM/YYYY` |
| amount | angka | APP memakai pemisah ribuan titik |
| status | teks | COMPLETED, PENDING, CANCELLED, REFUNDED |
| channel | teks | WEB/APP, bisa berupa alias `website`/`android` |

### payments.csv

| Kolom | Tipe | Catatan |
|---|---|---|
| payment_id | teks | Unik per pembayaran |
| order_id | teks | Harus merujuk ke order |
| paid_at | tanggal | Boleh kosong untuk status tertentu |
| paid_amount | angka | Nominal yang benar-benar dibayar |
| method | teks | BCA_VA, GOPAY, OVO, DANA, QRIS, CREDIT_CARD |
| status | teks | PAID, PENDING, FAILED |

## 5. Struktur pipeline

1. **Loader** (`src/dq/loader.py`) membaca CSV dan menormalisasi id, tanggal,
   nominal, channel, dan status. Baris tanpa kunci masuk `rejected_rows.csv`.
2. **Staging** (`sql/schema.sql`) menyimpan semua baris apa adanya setelah
   normalisasi. Tabel staging sengaja tanpa constraint unik.
3. **Checks** (`sql/checks/*.sql`) dijalankan terhadap staging. Setiap file
   punya header `name`, `category`, `severity`, `table`, `description`.
4. **Rekonsiliasi** (`src/dq/reconcile.py`) mencocokkan order dan payment,
   lalu mengklasifikasikan hasilnya.
5. **Report** (`src/dq/report.py`) menulis JSON, Markdown, dan CSV.

## 6. Menambah check baru

Buat file di `sql/checks/` dengan header berikut:

```sql
-- name: nama_check
-- category: uniqueness | completeness | validity | consistency | timeliness
-- severity: critical | warning | info
-- table: orders | payments | orders_dedup
-- description: kalimat singkat yang menjelaskan aturan bisnis
SELECT ...
```

Aturan:

- Query mengembalikan **baris yang bermasalah** (bukan baris yang lulus).
- Gunakan parameter `:as_of`, `:tolerance`, `:freshness_days`,
  `:late_payment_days` bila perlu.
- Untuk join ke order, pakai view `orders_dedup` agar duplikat tidak
  menggandakan hasil.
- Tambahkan test di `tests/test_checks.py` untuk memastikan check benar-benar
  menangkap anomali.

## 7. Troubleshooting

| Gejala | Penyebab umum | Solusi |
|---|---|---|
| `File sumber tidak ditemukan` | Folder input salah | Jalankan generator atau isi `--raw-dir` |
| Semua check FAIL | Data memang kotor | Lihat `reports/dq_summary.md` |
| `stale_data` FAIL saat demo | Tanggal acuan tidak sesuai data | Set `--as-of` sesuai tanggal data |
| Karakter aneh di CSV | File disimpan sebagai non-UTF8 | Simpan ulang sebagai UTF-8 |
| Dashboard kosong | Pipeline belum dijalankan | Jalankan pipeline lalu refresh |

## 8. Deploy dashboard (opsional, gratis)

**Streamlit Community Cloud**

1. Push repo ke GitHub.
2. Buka share.streamlit.io, pilih repo.
3. Main file: `streamlit/dashboard.py`.
4. Pastikan `reports/dq_summary.json` ikut ter-commit.

**Hugging Face Spaces**

1. Buat Space tipe Streamlit.
2. Upload repo, set app file ke `streamlit/dashboard.py`.
3. Tambahkan `requirements.txt`.

## 9. Batasan yang perlu disebut jujur

- Dataset bersifat sintetis, bukan data produksi.
- Penyimpanan memakai SQLite agar portabel; di produksi gunakan PostgreSQL.
- Belum ada scheduler; di produksi jalankan lewat cron, Airflow, atau GitHub Actions.
- Belum ada alerting ke Slack/email.
