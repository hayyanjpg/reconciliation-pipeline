"""Entry point agar pipeline bisa dijalankan tanpa install package.

Contoh:
    python scripts/run_pipeline.py --as-of 2026-10-31
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dq.run import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
