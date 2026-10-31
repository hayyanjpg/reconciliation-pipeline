# Data Quality Studio - Full Stack

Aplikasi full stack untuk upload, validasi, dan menjalankan pipeline Data
Quality Assurance: **FastAPI + React + Tailwind + Recharts + SQLAlchemy**.

Frontend dan backend berada di repo yang sama. Backend melayani API dan, pada
mode produksi, juga menyajikan hasil build frontend sebagai satu service.

## Status verifikasi

- 29 test pipeline/dashboard + 10 test API lulus.
- Frontend `npm run typecheck` dan `npm run build` lulus.
- Demo end-to-end: 230 baris order, 2/16 check PASS (12,5%), nominal berisiko
  Rp 5.118.000, 13 artefak siap unduh.
- Halaman `/?demo=1` langsung menjalankan demo dan menampilkan hasil.

## Arsitektur

```text
Browser (React + Tailwind + Recharts)
        |
        |  /api (JSON, multipart CSV)
        v
FastAPI  --->  validasi header & preview
   |
   +--> SQLite / Postgres (metadata run)
   +--> storage/runs/<id>/raw       (file upload)
   +--> storage/runs/<id>/reports   (artefak pipeline)
   |
   +--> ThreadPoolExecutor
          |
          +--> src/dq pipeline (normalisasi, 16 SQL check, rekonsiliasi)
```

- **Satu sumber kebenaran skema**: `src/dq/schema.py` dipakai loader, validasi,
  dan generator template.
- **Job async**: upload langsung mengembalikan `202`, frontend polling status.
- **Penyimpanan sementara**: file dan hasil dihapus otomatis setelah
  `RUN_TTL_HOURS` (default 24 jam).
- **Database**: SQLite untuk lokal, Postgres cukup lewat `DATABASE_URL`.
- **Tanpa Docker lokal**: Dockerfile disediakan untuk deploy.

## Menjalankan lokal (Windows)

Prasyarat: Python 3.10+, Node.js 18+.

```powershell
# 1. dependency backend
cd fullstack\backend
pip install -r requirements.txt

# 2. dependency frontend
cd ..\frontend
npm install

# 3. jalankan dua server (terminal terpisah)
cd ..\backend
python -m uvicorn app.main:app --reload --port 8000

cd ..\frontend
npm run dev
```

Buka `http://127.0.0.1:5173`. API docs di `http://127.0.0.1:8000/docs`.

Link demo instan: `http://127.0.0.1:5173/?demo=1` (langsung menjalankan data demo).

Atau dari root repo:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_fullstack.ps1
```

Catatan: di PowerShell, gunakan `npm.cmd` jika `npm` diblokir execution policy.

## Menjalankan mode produksi (satu server)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_fullstack_prod.ps1
```

Script membuild frontend ke `fullstack/frontend/dist`, lalu FastAPI menyajikan
`/` dan `/api` dari port 8000.

## Endpoint utama

| Method | Path | Fungsi |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/meta` | Skema file, format, batas upload |
| GET | `/api/templates/all.zip` | Template 3 CSV + README |
| GET | `/api/templates/{key}` | Template per file |
| POST | `/api/validate` | Validasi header + preview |
| POST | `/api/runs` | Upload 3 CSV, mulai job |
| POST | `/api/runs/demo` | Jalankan data demo |
| GET | `/api/runs/{id}` | Status job |
| GET | `/api/runs/{id}/results` | Ringkasan + daftar artefak |
| GET | `/api/runs/{id}/artifacts/{name}` | Unduh artefak |

Dokumentasi interaktif: `/docs`.

## Format data

Tiga file: `orders_web.csv`, `orders_app.csv`, `payments.csv`.

- `order_id` wajib; `payment_id` dan `order_id` wajib di payments.
- Kolom lain disarankan dan divalidasi sebagai peringatan.
- Nominal: `45000`, `45.000`, `Rp 45.000`, `1.500.000,00`.
- Tanggal: `2026-10-31`, `31/10/2026`, `31 Oct 2026`.
- Isi data bebas; struktur kolom harus sama. Template bisa diunduh dari UI.

## Testing

```powershell
# pipeline + dashboard lama
python -m pytest -q

# backend API
cd fullstack\backend
python -m pytest -q

# frontend typecheck + build
cd ..\frontend
npm run typecheck
npm run build
```

## Deploy

### Render (Blueprint)

1. Push repo ke GitHub.
2. Di Render: **New > Blueprint**, pilih repo.
3. Render membaca `render.yaml`: Docker build + Postgres.
4. Setelah deploy, buka URL service dan cek `/api/health`.

### Docker manual

```bash
docker build -f fullstack/Dockerfile -t dq-studio .
docker run -p 8000:8000 -e DATABASE_URL=sqlite:///./storage/app.db dq-studio
```

### Catatan deploy

- Jangan set `VITE_API_URL` jika frontend dan backend satu domain.
- Jika frontend dipisah (mis. Vercel) dan backend di Render, set
  `VITE_API_URL=https://backend-anda.onrender.com` saat build frontend dan
  `CORS_ORIGINS=https://frontend-anda.vercel.app` di backend.
- Render free Postgres punya masa berlaku; untuk jangka panjang gunakan Neon
  atau Supabase, lalu tempel connection string ke `DATABASE_URL`.
- Di platform dengan filesystem ephemeral, file upload hilang saat restart;
  metadata tetap aman di Postgres. Untuk produksi nyata, ganti storage lokal
  dengan S3/Supabase Storage.
- App demo bersifat publik: jangan upload data klien atau data sensitif.
- Jalankan **satu worker** (`uvicorn` tanpa `--workers`): job berjalan di
  `ThreadPoolExecutor` proses, jadi beberapa worker tidak berbagi antrean.

## Struktur

```text
fullstack/
|-- backend/
|   |-- app/
|   |   |-- main.py            # endpoint + static frontend
|   |   |-- validation.py      # validasi header, encoding, delimiter
|   |   |-- pipeline_runner.py # menjalankan src/dq di background
|   |   |-- storage.py         # folder run + TTL cleanup
|   |   |-- models.py          # tabel runs
|   |   `-- dq_bridge.py       # jembatan ke src/dq
|   |-- tests/test_api.py
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- App.tsx
|   |   |-- components/        # hero, upload, validasi, hasil, chart
|   |   |-- api.ts
|   |   `-- types.ts
|   `-- package.json
`-- Dockerfile
```

