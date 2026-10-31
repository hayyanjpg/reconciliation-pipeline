from __future__ import annotations

import sys

from .config import SRC_DIR

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dq.csv_utils import decode_csv, sniff_delimiter  # noqa: E402
from dq.run import main as run_pipeline_main  # noqa: E402
from dq.schema import (  # noqa: E402
    ACCEPTED_FORMATS,
    FILES,
    alias_lookup,
    canonical_headers,
    canonical_key,
    file_definition,
    schema_payload,
    template_csv,
    template_zip,
    validate_header_list,
)

__all__ = [
    "ACCEPTED_FORMATS",
    "FILES",
    "alias_lookup",
    "canonical_headers",
    "canonical_key",
    "decode_csv",
    "file_definition",
    "run_pipeline_main",
    "schema_payload",
    "sniff_delimiter",
    "template_csv",
    "template_zip",
    "validate_header_list",
]
