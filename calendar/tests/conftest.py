"""Ensure the calendar subdirectory root (containing the ``fcal`` package and the
``examples`` builder) is importable when tests are run from anywhere."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "examples"):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
