from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import os
import numpy as np
from pathlib import Path

# Package-level directories (resolved relative to this file)
PKG_DIR = Path(__file__).resolve().parent
IN_DIR  = PKG_DIR / "in"
OUT_DIR = PKG_DIR / "out"

def ensure_dirs():
    IN_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

def ensure_out_path(name: Optional[str], default_name: str) -> str:
    """
    If 'name' is None or base-only, place it under the package OUT_DIR.
    """
    ensure_dirs()
    if not name:
        return str(OUT_DIR / default_name)
    # If user passed a bare filename, put it in OUT_DIR
    p = Path(name)
    if not p.is_absolute() and p.parent == Path("."):
        return str(OUT_DIR / p.name)
    return str(p)

def parse_vec_real(s: Optional[str], n: int, default_first_one: bool = True) -> np.ndarray:
    """
    Parse '1 0 0' (or '1,0,0') into a real vector of length n.
    If s is None and default_first_one is True, returns e1. Else zeros.
    """
    if s is None:
        v = np.zeros(n, float)
        if default_first_one and n > 0:
            v[0] = 1.0
        return v
    toks = [t for t in s.replace(",", " ").split() if t]
    comp = np.array([complex(t.replace("i","j")) for t in toks], complex)
    if comp.size != n:
        raise ValueError(f"vector has length {comp.size}, expected n={n}.")
    comp = np.real_if_close(comp, tol=1e8)
    if np.iscomplexobj(comp) and np.max(np.abs(comp.imag)) > 1e-12:
        raise ValueError("vector contains non-negligible imaginary parts.")
    return np.asarray(comp.real, float)

def parse_time(s: str) -> np.ndarray:
    """Parse 't0:dt:tf' or '0 0.1 ... 4' into a numpy array."""
    s = s.strip()
    if ":" in s:
        t0, dt, tf = (float(v) for v in s.split(":"))
        n = int(round((tf - t0)/dt)) + 1
        return np.linspace(t0, tf, n)
    return np.array([float(v) for v in s.replace(",", " ").split()], float)

def to2d(arr: np.ndarray) -> np.ndarray:
    """Ensure 2D (n, N)."""
    arr = np.asarray(arr)
    if arr.ndim == 1:
        return arr.reshape(1, -1)
    return arr

def safe_series(name: str, arr) -> Optional[np.ndarray]:
    if arr is None:
        return None
    try:
        return np.asarray(arr, float)
    except Exception as e:
        raise ValueError(f"malformed '{name}' in JSON: {e}")

def series_labels(prefix: str, n: int) -> List[str]:
    return [f"{prefix}{i+1}" for i in range(n)]
