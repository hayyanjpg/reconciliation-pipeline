from __future__ import annotations

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parents[1]
SRC_DIR = PROJECT_ROOT / "src"
FRONTEND_DIST = BACKEND_DIR.parent / "frontend" / "dist"
DEMO_RAW_DIR = PROJECT_ROOT / "data" / "raw"

STORAGE_DIR = Path(os.getenv("STORAGE_DIR", str(BACKEND_DIR / "storage"))).resolve()
DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite:///{(STORAGE_DIR / 'app.db').as_posix()}"
)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "10"))
RUN_TTL_HOURS = int(os.getenv("RUN_TTL_HOURS", "24"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,*"
    ).split(",")
    if origin.strip()
]

