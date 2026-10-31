"""Entrypoint untuk Hugging Face Space (Gradio/Python SDK).
Menjalankan FastAPI backend di port 7860.
"""

import sys
from pathlib import Path

# Pastikan path modul terbaca
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "fullstack" / "backend"))

import uvicorn
from fullstack.backend.app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
