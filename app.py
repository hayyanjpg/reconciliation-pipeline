"""Entrypoint untuk Hugging Face Space.
Menjalankan FastAPI backend langsung via Uvicorn di port 7860 tanpa dependensi Gradio.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "fullstack" / "backend"))

import uvicorn
from fullstack.backend.app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
