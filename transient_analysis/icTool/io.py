# ---------------------------------
# File: transient_analysis/icTool/io.py
# ---------------------------------
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
from .utils import parse_vector, parse_matrix


def load_matrix_from_txt(path: Path) -> np.ndarray:
    return parse_matrix(path.read_text(encoding="utf-8"))


def load_vector_from_txt(path: Path) -> np.ndarray:
    return parse_vector(path.read_text(encoding="utf-8"))


def dump_json(path: Path, obj: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return path