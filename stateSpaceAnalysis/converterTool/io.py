from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent
IN_DIR  = PKG_ROOT / "in"
OUT_DIR = PKG_ROOT / "out"

@dataclass
class SavePaths:
    tf_plot: Path | None = None
    ss_plot: Path | None = None

def default_out(name: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUT_DIR / name
