from __future__ import annotations
import os
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple
import numpy as np
import sympy as sp
import control as ct

# Optional progress bar (tqdm)
try:
    from tqdm import tqdm  # type: ignore
    TQDM_OK = True
except Exception:
    TQDM_OK = False

def ensure_out_dir(base: str = None) -> str:
    """Ensure output directory exists (package-local ./out by default)."""
    if base is None:
        base = os.path.join(os.path.dirname(__file__), "out")
    os.makedirs(base, exist_ok=True)
    return base

def parse_list_of_floats(s: str | None) -> List[float]:
    if not s:
        return []
    return [float(x) for x in s.replace(",", " ").split()]

def parse_list_of_complex(s: str | None) -> List[complex]:
    if not s:
        return []
    toks = s.replace(",", " ").replace("i", "j").split()
    return [complex(tok) for tok in toks]

def poly_from_string(expr: str, s_symbol: sp.Symbol) -> List[float]:
    sym = sp.sympify(expr, locals={str(s_symbol): s_symbol})
    poly = sp.Poly(sp.expand(sym), s_symbol)
    return [float(c) for c in poly.all_coeffs()]

def squeeze_poly(arr_like) -> np.ndarray:
    arr = np.array(arr_like, dtype=float).squeeze()
    if arr.ndim == 0:
        arr = np.array([float(arr)], dtype=float)
    return arr

def pretty_tf(name: str, G: ct.TransferFunction) -> str:
    return f"{name}:\n{G}"

def pick_tgrid_from_poles(p: Sequence[complex], safety: float = 8.0) -> np.ndarray:
    if len(p) == 0:
        tfinal = 10.0
    else:
        max_real = np.max(np.real(p))
        if max_real < 0:
            tau = 1.0 / max(1e-6, -max_real)
        else:
            tau = 10.0
        tfinal = float(np.clip(safety * tau, 4.0, 40.0))
    dt = tfinal / 2000.0
    return np.arange(0.0, tfinal + dt, dt, dtype=float)

def forced_xy(sys: ct.TransferFunction, t: np.ndarray, u: np.ndarray):
    from control.timeresp import forced_response
    res = forced_response(sys, t, u)
    if isinstance(res, (tuple, list)):
        if len(res) == 3:
            t_out, y_out, _ = res
        elif len(res) == 2:
            t_out, y_out = res
        else:
            raise RuntimeError(f"Unexpected forced_response return length: {len(res)}")
        t_out = np.asarray(t_out, dtype=float)
        y_out = np.asarray(y_out, dtype=float)
    else:
        if hasattr(res, "T"):
            t_out = np.asarray(res.T, dtype=float)
        elif hasattr(res, "time"):
            t_out = np.asarray(res.time, dtype=float)
        else:
            raise AttributeError("forced_response result lacks .T/.time")
        if hasattr(res, "y"):
            y_out = np.asarray(res.y, dtype=float)
        elif hasattr(res, "yout"):
            y_out = np.asarray(res.yout, dtype=float)
        else:
            raise AttributeError("forced_response result lacks .y/.yout")
    y_out = np.squeeze(y_out)
    if y_out.ndim == 2:
        if y_out.shape[0] == 1:
            y_out = y_out[0]
        elif y_out.shape[1] == 1:
            y_out = y_out[:, 0]
        else:
            raise RuntimeError(f"Unexpected y shape {y_out.shape} for SISO response.")
    if y_out.ndim != 1:
        y_out = y_out.reshape(-1)
    if y_out.shape[0] != t_out.shape[0]:
        n = min(y_out.shape[0], t_out.shape[0])
        t_out = t_out[:n]
        y_out = y_out[:n]
    return t_out, y_out
