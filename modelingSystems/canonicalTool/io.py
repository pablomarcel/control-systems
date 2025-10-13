
# io.py
from __future__ import annotations
from pathlib import Path
from typing import List
import json

def parse_coeffs(s: str) -> list[float]:
    return [float(x.strip()) for x in s.split(",") if x.strip()]

def ensure_out_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def write_json(obj, path: str | Path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    return p
