"""Entrypoint untuk Hugging Face Space.
Menjalankan FastAPI backend langsung via Uvicorn di port 7860.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "fullstack" / "backend"))

import uvicorn
from fullstack.backend.app.main import app

# Hugging Face menjalankan `python app.py` baik secara direct modul maupun __main__
# Jangan bungkus di dalam if __name__ == '__main__' agar selalu dieksekusi dan tidak exit
if __name__ == "__main__":
    uvicorn.run("fullstack.backend.app.main:app", host="0.0.0.0", port=7860, reload=False)
else:
    uvicorn.run(app, host="0.0.0.0", port=7860)
