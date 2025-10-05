# SPDX-License-Identifier: MIT
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Tuple, Optional
import json
import numpy as np
from pathlib import Path

@dataclass(frozen=True)
class ControllerJSON:
    mode: str  # 'K' or 'L'
    A: np.ndarray
    B: Optional[np.ndarray]
    C: Optional[np.ndarray]
    K: Optional[np.ndarray]
    L: Optional[np.ndarray]
    state_names: list[str]

@dataclass(frozen=True)
class IOJSON:
    Acl: np.ndarray
    Bcl: np.ndarray
    C: np.ndarray
    D: np.ndarray
    r: float
    state_names: list[str]
    output_names: list[str]

def _as_np(x):
    if x is None:
        return None
    return np.array(x, float)

def load_json(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def try_parse_controller(payload: dict) -> Optional[ControllerJSON]:
    mode = (payload.get("mode","K") or "K").upper()
    if not {"A"}.issubset(payload.keys()):
        return None
    A = _as_np(payload["A"])
    B = _as_np(payload.get("B"))
    C = _as_np(payload.get("C"))
    K = _as_np(payload.get("K"))
    L = _as_np(payload.get("L"))
    names = payload.get("state_names") or [f"x{i+1}" for i in range(A.shape[0])]
    if mode not in ("K","L"):
        return None
    return ControllerJSON(mode, A, B, C, K, L, names)

def try_parse_io(payload: dict) -> Optional[IOJSON]:
    needed = {"Acl","Bcl","C","D"}
    if not needed.issubset(payload.keys()):
        return None
    Acl = _as_np(payload["Acl"])
    Bcl = _as_np(payload["Bcl"])
    C   = _as_np(payload["C"])
    D   = _as_np(payload["D"])
    r   = float(payload.get("r", 1.0))
    n = Acl.shape[0]
    p = C.shape[0] if C.ndim == 2 else 1
    state_names  = payload.get("state_names")  or [f"x{i+1}" for i in range(n)]
    output_names = payload.get("output_names") or [f"y{i+1}" for i in range(p)]
    return IOJSON(Acl, Bcl, C, D, r, state_names, output_names)
