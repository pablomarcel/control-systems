
"""
utils.py — Shared helpers for minOrdTfTool
"""
from __future__ import annotations
from typing import List, Tuple
import numpy as np

def parse_mat(s: str | None) -> np.ndarray | None:
    """
    Parse matrix strings like "0 1; -2 -3" or "0, 1; -2, -3".
    Returns a real-if-close ndarray of shape (r, c).
    """
    if s is None:
        return None
    rows = [r.strip() for r in s.replace(",", " ").split(";")]
    data = []
    for r in rows:
        if not r:
            continue
        toks = [t for t in r.split() if t]
        data.append([complex(t.replace("i", "j")) for t in toks])
    M = np.array(data, dtype=complex)
    return np.real_if_close(M, tol=1e8)

def split_tokens_any(s: str) -> List[str]:
    parts: List[str] = []
    for chunk in s.split(","):
        parts.extend([t for t in chunk.strip().split() if t])
    return parts

def _expand_imag_coeffs(expr: str) -> str:
    e = expr.replace("sqrt", "np.sqrt").replace("i", "j")
    e = e.replace("j", "*1j").replace("**1j", "*1j")
    return e

def parse_cplx_tokens(tokens: List[str]) -> np.ndarray:
    env = {"np": np}
    vals = []
    for t in tokens:
        try:
            v = eval(_expand_imag_coeffs(t), {"__builtins__": {}}, env)
        except Exception:
            v = complex(t.replace("i", "j"))
        vals.append(complex(v))
    return np.asarray(vals, dtype=complex)

def array2str(M: np.ndarray, precision: int = 6) -> str:
    arr = np.asarray(np.real_if_close(M, 1e8))
    return np.array2string(np.asarray(arr, float), precision=precision, suppress_small=True)

def mat_inline(M: np.ndarray, precision: int = 4) -> str:
    A = np.asarray(np.real_if_close(M, 1e8))
    if A.ndim == 1:
        A = A.reshape(1, -1)
    rows = []
    for i in range(A.shape[0]):
        row = " ".join(f"{float(A[i,j]):.{precision}g}" for j in range(A.shape[1]))
        rows.append("[" + row.replace("-0", "0") + "]")
    return "[" + "; ".join(rows) + "]"

def poly_from_roots(roots: np.ndarray) -> np.ndarray:
    return np.real_if_close(np.poly(roots), 1e8).astype(float)

def phi_of_A(A: np.ndarray, coeff: np.ndarray) -> np.ndarray:
    r = len(coeff) - 1
    I = np.eye(A.shape[0])
    out = np.zeros_like(A, dtype=float)
    out += np.linalg.matrix_power(A, r)
    for k in range(1, r):
        out += coeff[k] * np.linalg.matrix_power(A, r - k)
    out += coeff[-1] * I
    return out

def build_S(Aab: np.ndarray, Abb: np.ndarray) -> np.ndarray:
    r = Abb.shape[0]
    return np.vstack([Aab @ np.linalg.matrix_power(Abb, i) for i in range(r)])
