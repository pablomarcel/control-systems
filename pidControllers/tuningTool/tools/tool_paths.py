
# tools/tool_paths.py
from __future__ import annotations
from pathlib import Path

# Base directories (resolved at runtime)
PKG_ROOT = Path(__file__).resolve().parents[1]
IN_DIR = PKG_ROOT / "in"
OUT_DIR = PKG_ROOT / "out"

def ensure_outdir() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
