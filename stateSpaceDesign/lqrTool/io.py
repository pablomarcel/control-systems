from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import control as ct
from typing import Tuple
from .core import StateSpaceModel

def parse_matrix(s: str) -> np.ndarray:
    s = (s or "").strip()
    if s.lower() in ("", "none"):
        return np.array([[]], dtype=float)
    rows = [r for r in s.replace(",", " ").split(";")]
    data = []
    for r in rows:
        r = r.strip()
        if not r:
            continue
        data.append([float(x) for x in r.split()])
    return np.array(data, dtype=float)

def parse_vector(s: str) -> np.ndarray:
    v = np.array([float(x) for x in s.replace(",", " ").split()], dtype=float)
    return v.reshape((-1, 1))

def parse_Q(s: str, n: int) -> np.ndarray:
    s = (s or "").strip().lower()
    if s.startswith("eye"):
        if ":" in s:
            return np.eye(int(s.split(":")[1]))
        return np.eye(n)
    if s.startswith("diag:"):
        vals = [float(x) for x in s.split(":", 1)[1].replace(",", " ").split()]
        return np.diag(vals)
    Q = parse_matrix(s)
    if Q.ndim == 1:
        Q = np.diag(Q)
    return Q

def parse_R(s: str):
    s = (s or "").strip().lower()
    try:
        return float(s)
    except ValueError:
        pass
    R = parse_matrix(s)
    if R.size == 1:
        return float(np.asarray(R).reshape(()).item())
    return R

def build_model_from_ABCD(A: str, B: str, C: str | None, D: str | None) -> StateSpaceModel:
    A_ = parse_matrix(A)
    B_ = parse_matrix(B)
    if B_.ndim == 1:
        B_ = B_.reshape((-1, 1))
    n = A_.shape[0]
    if C:
        C_ = parse_matrix(C)
        if C_.ndim == 1:
            C_ = C_.reshape((1, -1))
    else:
        C_ = np.zeros((1, n)); C_[0, 0] = 1.0
    if D:
        D_ = parse_matrix(D)
        if D_.size == 0:
            D_ = np.zeros((1, 1))
        elif D_.ndim == 1:
            D_ = D_.reshape((1, -1))
    else:
        D_ = np.zeros((1, 1))
    return StateSpaceModel(A_, B_, C_, D_)

def build_model_from_tf(num: str, den: str, C: str | None = None, D: str | None = None) -> StateSpaceModel:
    numv = np.array([float(x) for x in num.replace(",", " ").split()], dtype=float)
    denv = np.array([float(x) for x in den.replace(",", " ").split()], dtype=float)
    sys_ss = ct.ss(ct.tf(numv, denv))
    A, B, C0, D0 = map(np.asarray, (sys_ss.A, sys_ss.B, sys_ss.C, sys_ss.D))
    if C:
        C_ = parse_matrix(C)
        if C_.ndim == 1:
            C_ = C_.reshape((1, -1))
    else:
        C_ = C0
    if D:
        D_ = parse_matrix(D)
        if D_.size == 0:
            D_ = np.zeros((1, 1))
        elif D_.ndim == 1:
            D_ = D_.reshape((1, -1))
    else:
        D_ = D0 if D0.size else np.zeros((1, 1))
    return StateSpaceModel(A, B, C_, D_)
