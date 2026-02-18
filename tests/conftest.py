"""Shared pytest configuration for local source-tree testing."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure `src/` is importable even when package is not installed.
SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
