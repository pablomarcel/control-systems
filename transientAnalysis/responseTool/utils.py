# transientAnalysis/responseTool/utils.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Tuple
import numpy as np
import control as ct

# ---------- parsing helpers ----------

def parse_vector(s: str | None) -> np.ndarray | None:
    if s is None:
        return None
    toks = [
        t
        for t in s.replace(",", " ").replace(";", " ").replace("[", "").replace("]", "").split()
        if t.strip()
    ]
    return np.array([float(x) for x in toks], dtype=float)


def parse_matrix(s: str | None) -> np.ndarray | None:
    if s is None:
        return None
    s = s.strip().replace("[", "").replace("]", "")
    rows = [r for r in s.split(";") if r.strip()]
    data: list[list[float]] = []
    for r in rows:
        toks = [t for t in r.replace(",", " ").split() if t.strip()]
        data.append([float(x) for x in toks])
    return np.array(data, dtype=float)


def parse_zetas_list(s: str | None) -> list[float]:
    """Parse comma/space-separated list of zeta values; provide a sensible default."""
    if not s:
        return [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    toks = [t for t in s.replace(",", " ").split() if t.strip()]
    return [float(t) for t in toks]


def time_grid(tfinal: float, dt: float) -> np.ndarray:
    return np.arange(0.0, tfinal + dt, dt, dtype=float)

# ---------- version-safe wrappers ----------

def _unpack_step_result(res) -> Tuple[np.ndarray, np.ndarray]:
    if isinstance(res, tuple):
        if len(res) >= 2:
            T, Y = res[0], res[1]
            return np.asarray(T), np.asarray(Y)
        raise RuntimeError("Unexpected step_response tuple length.")
    T = getattr(res, "time", getattr(res, "t", None))
    Y = getattr(res, "outputs", getattr(res, "y", None))
    if T is None or Y is None:
        raise RuntimeError("step_response returned unrecognized object.")
    return np.asarray(T), np.asarray(Y)


def _unpack_forced_result(res) -> Tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    if isinstance(res, tuple):
        if len(res) == 3:
            T, Y, X = res
            return np.asarray(T), np.asarray(Y), np.asarray(X)
        if len(res) == 2:
            T, Y = res
            return np.asarray(T), np.asarray(Y), None
        raise RuntimeError("Unexpected forced_response tuple length.")
    T = getattr(res, "time", getattr(res, "t", None))
    Y = getattr(res, "outputs", getattr(res, "y", None))
    X = getattr(res, "states", getattr(res, "x", None))
    if T is None or Y is None:
        raise RuntimeError("forced_response returned unrecognized object.")
    return np.asarray(T), np.asarray(Y), (np.asarray(X) if X is not None else None)


def step_response(sys, T: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    try:
        res = ct.step_response(sys, T=T)
    except TypeError:
        res = ct.step_response(sys, T)
    return _unpack_step_result(res)


def forced_response(sys, U: np.ndarray, T: np.ndarray):
    try:
        res = ct.forced_response(sys, T=T, U=U)
    except TypeError:
        res = ct.forced_response(sys, T, U)
    return _unpack_forced_result(res)

# ---------- creators ----------

def mk_ss(A, B, C, D):
    A = np.asarray(A, float); B = np.asarray(B, float)
    C = np.asarray(C, float); D = np.asarray(D, float)
    return ct.ss(A, B, C, D)


def mk_tf(num, den):
    return ct.tf(np.asarray(num, float), np.asarray(den, float))
