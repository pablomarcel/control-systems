#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils.py — parsing helpers, decorators, math utilities (root locus, Bode) for regulatorTool.
"""

from __future__ import annotations
import functools, logging, warnings
from typing import Callable, Iterable, Tuple, Optional
import numpy as np
import control as ct

# Optional deps
try:
    import sympy as sp  # noqa: F401
    HAS_SYMPY = True
except Exception:
    HAS_SYMPY = False

try:
    import matplotlib.pyplot as plt  # noqa: F401
    HAS_MPL = True
except Exception:
    HAS_MPL = False

try:
    import plotly.graph_objects as go  # noqa: F401
    from plotly.subplots import make_subplots  # noqa: F401
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False


# ---------------------- decorators ----------------------

def log_call(fn: Callable) -> Callable:
    """Decorator to log function calls (name + kwargs) at DEBUG level."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        logging.debug("CALL %s(%s)", fn.__name__, ", ".join(
            [", ".join(repr(a) for a in args)] +
            [f"{k}={v!r}" for k, v in kwargs.items()]))
        return fn(*args, **kwargs)
    return wrapper


# ---------------------- parsing helpers ----------------------

@log_call
def parse_real_vec(s: str) -> np.ndarray:
    return np.array([float(x) for x in s.replace(",", " ").split()], float)

@log_call
def parse_complex_list(s: str) -> np.ndarray:
    out = []
    for w in s.replace(",", " ").split():
        w = w.replace("i", "j").replace("I", "j")
        val = complex(eval(w, {"__builtins__": {},"sqrt": np.sqrt, "np": np}, {}))
        out.append(val)
    return np.array(out, dtype=complex)


# ---------------------- array/printing helpers ----------------------

@log_call
def array2str(M: np.ndarray, p: int = 6) -> str:
    A = np.real_if_close(M, 1e8)
    return np.array2string(np.asarray(A, float), precision=p, suppress_small=True)

@log_call
def mat_inline(M: np.ndarray, precision: int = 4) -> str:
    M = np.atleast_2d(np.asarray(np.real_if_close(M, 1e8), float))
    rows = [" ".join(f"{float(v):.{precision}g}" for v in row) for row in M]
    return "[[" + "]; ".join(rows) + "]]"


# ---------------------- math helpers ----------------------

@log_call
def poly_from_roots(roots: np.ndarray) -> np.ndarray:
    return np.real_if_close(np.poly(roots), 1e8).astype(float)

@log_call
def phi_of_A(A: np.ndarray, coeff: np.ndarray) -> np.ndarray:
    r = len(coeff) - 1
    out = np.linalg.matrix_power(A, r)
    for k in range(1, r):
        out += coeff[k] * np.linalg.matrix_power(A, r - k)
    out += coeff[-1] * np.eye(A.shape[0])
    return out

@log_call
def tf_eval_jw(tf: ct.TransferFunction, w: np.ndarray) -> np.ndarray:
    num = np.squeeze(np.array(tf.num[0][0], float))
    den = np.squeeze(np.array(tf.den[0][0], float))
    s = 1j * w
    return np.polyval(num, s) / np.polyval(den, s)

@log_call
def bode_data(tf: ct.TransferFunction, w: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    H = tf_eval_jw(tf, w)
    mag_db = 20 * np.log10(np.maximum(np.abs(H), 1e-16))
    phase_deg = np.unwrap(np.angle(H)) * 180 / np.pi
    return mag_db, phase_deg

# ---- Root locus helpers

@log_call
def _normalize_rl_array(r: np.ndarray, k: np.ndarray) -> np.ndarray:
    """Ensure r is (branches, samples)."""
    r = np.asarray(r)
    if r.ndim != 2:
        raise RuntimeError(f"Unexpected root-locus array shape {r.shape}")
    if r.shape[0] == k.size:   # samples × branches
        return r.T.copy()
    if r.shape[1] == k.size:   # branches × samples
        return r.copy()
    # default: assume first axis = samples
    return r.T.copy()

@log_call
def rlocus_from_control(L: ct.TransferFunction,
                        kvect: Optional[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns (rlist, kvals) with shape (branches, samples).
    1) Try root_locus_map() (new API).
    2) On any error or unknown type, fall back to root_locus(plot=False)
       with its FutureWarning suppressed.
    """
    # ---- 1) Try modern API
    try:
        if hasattr(ct, "root_locus_map"):
            rmap = ct.root_locus_map(L) if kvect is None else ct.root_locus_map(L, kvect=kvect)
            # Try common attribute names across 0.10.x
            roots = None; gains = None
            for attr in ("roots", "r", "poles"):
                if hasattr(rmap, attr):
                    roots = np.asarray(getattr(rmap, attr))
                    break
            for attr in ("k", "gains", "kvect"):
                if hasattr(rmap, attr):
                    gains = np.asarray(getattr(rmap, attr)).ravel()
                    break
            if roots is None or gains is None or roots.ndim != 2 or gains.size == 0:
                raise RuntimeError("Unknown root_locus_map return type")
            return _normalize_rl_array(roots, gains), gains
        # If not available, drop to legacy path
    except Exception as e:
        logging.debug("root_locus_map path failed: %s — using legacy root_locus()", e)

    # ---- 2) Legacy API, suppressing the FutureWarning
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning, module=r"control\.rlocus")
        if kvect is None:
            r, k = ct.root_locus(L, plot=False)
        else:
            r, k = ct.root_locus(L, kvect=kvect, plot=False)
    r = np.asarray(r); k = np.asarray(k).ravel()
    return _normalize_rl_array(r, k), k
