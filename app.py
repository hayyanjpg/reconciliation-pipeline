"""Entrypoint untuk Hugging Face Space (Gradio/Python SDK).
Menjalankan FastAPI backend langsung atau lewat gradio mount.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "fullstack" / "backend"))

import gradio as gr
from fullstack.backend.app.main import app as fastapi_app

# Pasang FastAPI ke Gradio interface agar dikenali sempurna oleh server HF
with gr.Blocks(title="Data Quality API") as demo:
    gr.Markdown("# 🛡️ Data Quality Studio - Backend API")
    gr.Markdown("Backend FastAPI sedang berjalan aktif.")
    gr.Markdown("[Lihat Dokumentasi API Swagger](/docs)")

app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
