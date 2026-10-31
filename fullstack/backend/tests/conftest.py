from __future__ import annotations

import os
import tempfile
from pathlib import Path

_TEMP_DIR = tempfile.mkdtemp(prefix="dq-api-test-")
os.environ["STORAGE_DIR"] = _TEMP_DIR
os.environ["DATABASE_URL"] = f"sqlite:///{(Path(_TEMP_DIR) / 'test.db').as_posix()}"
