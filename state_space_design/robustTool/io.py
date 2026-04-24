from __future__ import annotations
import json, os
from typing import Any, Dict

PKG_ROOT = os.path.dirname(__file__)
IN_DIR  = os.path.join(PKG_ROOT, "in")
OUT_DIR = os.path.join(PKG_ROOT, "out")

def ensure_out_dir(path: str | None = None) -> str:
    d = OUT_DIR if path is None else os.path.dirname(os.path.join(OUT_DIR, path))
    os.makedirs(d, exist_ok=True)
    return d

def save_json(obj: Dict[str, Any], relpath: str) -> str:
    full = os.path.join(OUT_DIR, relpath)
    ensure_out_dir(full)
    with open(full, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    return full
