# ---------------------------------
# File: transient_analysis/icTool/utils.py
# ---------------------------------
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
import json
import numpy as np
import control as ct


# ---------------- Utilities ---------------- #

def parse_vector(s: str) -> np.ndarray:
    """Accept 'a b c', 'a,b,c', 'a; b' or bracketed; return 1-D float array.
    Robust to extra whitespace; raises ValueError on empty.
    """
    if s is None:
        raise ValueError("parse_vector: got None")
    toks = [
        t
        for t in s.replace(",", " ").replace(";", " ")
                 .replace("[", " ").replace("]", " ").split()
        if t.strip()
    ]
    if not toks:
        raise ValueError("parse_vector: empty input")
    return np.array([float(t) for t in toks], dtype=float)


def parse_matrix(s: str) -> np.ndarray:
    """Accept 'row1; row2' with spaces or commas; return 2-D float array.
    Example: "0 1; -6 -5" or "[0, 1; -6, -5]".
    """
    if s is None:
        raise ValueError("parse_matrix: got None")
    s = s.strip().replace("[", "").replace("]", "")
    rows = [r for r in s.split(";") if r.strip()]
    if not rows:
        raise ValueError("parse_matrix: no rows")
    mat = []
    for r in rows:
        toks = [t for t in r.replace(",", " ").split() if t.strip()]
        if not toks:
            raise ValueError("parse_matrix: empty row")
        mat.append([float(t) for t in toks])
    arr = np.array(mat, dtype=float)
    if arr.ndim != 2:
        raise ValueError("parse_matrix: not 2-D")
    return arr


def parse_poly(s: str) -> np.ndarray:
    """Parse TF polynomial coefficients in descending powers.
    Accepts forms like '1 3 2', '1,3,2', or '[1, 3, 2]'.
    Returns a 1-D float array.
    """
    return parse_vector(s)


def time_grid(tfinal: float, dt: float) -> np.ndarray:
    if tfinal <= 0 or dt <= 0:
        raise ValueError("tfinal and dt must be positive")
    N = int(np.floor(tfinal / dt)) + 1
    return np.linspace(0.0, tfinal, N)


def _to_2d(a: Any) -> np.ndarray:
    """Ensure (rows, N) float ndarray (never np.matrix)."""
    a = np.asarray(a, dtype=float)
    if a.ndim == 1:
        a = a.reshape(1, -1)
    return a


def _ensure_1d(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    return v.ravel()


def safe_ss(A: np.ndarray, B: np.ndarray, C: np.ndarray, D: np.ndarray) -> ct.StateSpace:
    """Wrapper around control.ss that normalizes input types and shapes."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    C = np.asarray(C, dtype=float)
    D = np.asarray(D, dtype=float)
    return ct.ss(A, B, C, D)


def initial_response_safe(sys: ct.StateSpace, T: np.ndarray, X0: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Call control.initial_response and return (T, Y) with Y shape (m, N),
    where m is the number of outputs. Works across python-control versions
    that return (T, y) or a ResponseData-like object.
    """
    res = ct.initial_response(sys, T=T, X0=X0)
    if isinstance(res, tuple):  # older API
        T_out, y = res[0], res[1]
    else:  # ResponseData-like
        T_out, y = getattr(res, "time"), getattr(res, "outputs")
    return np.asarray(T_out, float), _to_2d(y)


def forced_response_safe(sys: ct.StateSpace, T: np.ndarray, U: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Call control.forced_response and return (T, Y) with Y shape (m, N)."""
    res = ct.forced_response(sys, T=T, U=U)
    if isinstance(res, tuple):
        T_out, y = res[0], res[1]
    else:
        T_out, y = getattr(res, "time"), getattr(res, "outputs")
    return np.asarray(T_out, float), _to_2d(y)


# ------------- Result containers ------------- #

@dataclass(slots=True)
class CaseResult:
    """Container for a single IC computation (direct or step-equivalent)."""
    T: np.ndarray            # shape (N,)
    Y: np.ndarray            # shape (r, N)  (states or outputs)
    label_rows: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "T": self.T.tolist(),
            "Y": self.Y.tolist(),
            "labels": list(self.label_rows),
        }


@dataclass(slots=True)
class CompareResult:
    """Paired result for direct vs step-equivalent calculations."""
    direct: CaseResult
    step_equiv: CaseResult

    def to_json(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "direct": self.direct.to_dict(),
            "step_equiv": self.step_equiv.to_dict(),
        }, indent=2), encoding="utf-8")
        return path


# ------------- Lightweight tracing decorator ------------- #

try:  # pragma: no cover
    from .tools.diagram import track  # reuse track if available
except Exception:  # pragma: no cover
    def track(_src: str, _dst: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
            return fn
        return deco


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p
