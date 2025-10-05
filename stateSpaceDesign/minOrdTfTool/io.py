
"""
io.py — I/O helpers (JSON export, pretty printing)
"""
from __future__ import annotations
import json, sys
from typing import Any, Dict, Optional
import numpy as np
from .utils import array2str, mat_inline

def export_json(payload: Dict[str, Any], path: str) -> str:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path

def pretty_dump(payload: Dict[str, Any], precision: int = 6) -> str:
    # Minimal pretty printer – returns a string for print()
    lines = []
    for k in ["A","B","C","T","Tinv","Abar","Bbar","Ahat","Bhat","Fhat","Ke","K","Kbar","Ka","Kb","Atil","Btil","Ctil","Dtil","tf_num","tf_den"]:
        if k not in payload: 
            continue
        v = payload[k]
        try:
            arr = np.asarray(v, float)
            lines.append(f"{k}:\n{array2str(arr, precision)}")
        except Exception:
            lines.append(f"{k}: {v}")
    return "\n".join(lines)
