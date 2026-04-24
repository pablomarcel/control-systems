from __future__ import annotations
import numpy as np

def parse_matrix(s: str) -> np.ndarray:
    rows = [r.strip() for r in s.strip().split(";") if r.strip()]
    mat = [[float(x.replace("i","j")) for x in row.replace(",", " ").split()] for row in rows]
    return np.array(mat, dtype=float)

def parse_time(s: str) -> np.ndarray:
    s = s.strip()
    if ":" in s:
        a, b, c = s.split(":")
        a, b, c = float(a), float(b), float(c)
        n = int(round((c - a) / b)) + 1
        return np.linspace(a, c, n)
    return np.array([float(x) for x in s.replace(",", " ").split()], dtype=float)

def default_state_names(n: int) -> list[str]:
    return [f"x{i+1}" for i in range(n)]

def default_output_names(p: int) -> list[str]:
    return [f"y{i+1}" for i in range(p)]

def ensure_2d_row(v):
    arr = np.array(v, dtype=float)
    if arr.ndim == 1:
        return arr.reshape(1, -1)
    return arr

def ensure_col(v):
    arr = np.array(v, dtype=float)
    if arr.ndim == 1:
        return arr.reshape(-1, 1)
    return arr
