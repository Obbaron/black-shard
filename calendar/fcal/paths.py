"""
fcal.paths

The *data* the engine operates on operates sits outside the package,
one level up.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CANON_DIR = DATA_DIR / "canon"
REFERENCE_DIR = DATA_DIR / "reference"
RENDERED_DIR = ROOT / "rendered"


def canon(name: str) -> Path:
    """Path to a canon calendar JSON by short name (without extension)."""
    return CANON_DIR / f"{name}.json"


def reference(name: str) -> Path:
    """Path to a reference calendar JSON by short name (without extension)."""
    return REFERENCE_DIR / f"{name}.json"
