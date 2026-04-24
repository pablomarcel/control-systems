
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence
import json
import numpy as np

DEFAULT_IN_DIR = Path("control_systems/converterTool/in")
DEFAULT_OUT_DIR = Path("control_systems/converterTool/out")

def parse_vector(s: str | None) -> np.ndarray | None:
    if s is None:
        return None
    toks = [t for t in s.replace(",", " ").replace(";", " ")
                 .replace("[", "").replace("]", "").split() if t.strip()]
    return np.array([float(x) for x in toks], dtype=float)

def parse_matrix(s: str | None) -> np.ndarray | None:
    if s is None:
        return None
    s = s.strip().replace("[", "").replace("]", "")
    rows = [r for r in s.split(";") if r.strip()]
    mat = []
    for r in rows:
        toks = [t for t in r.replace(",", " ").split() if t.strip()]
        mat.append([float(x) for x in toks])
    return np.array(mat, dtype=float)

def ensure_out_path(path: Optional[Path], default_name: str, suffix: str = ".json") -> Path:
    if path is None:
        DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)
        return DEFAULT_OUT_DIR / f"{default_name}{suffix}"
    if path.suffix:
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    path.mkdir(parents=True, exist_ok=True)
    return path / f"{default_name}{suffix}"

def write_json(obj, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return out_path

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
