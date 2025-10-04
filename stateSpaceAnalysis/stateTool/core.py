from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict
import sympy as sp
import numpy as np

from .utils import sym_s, coeffs_asc

@dataclass(slots=True, frozen=True)
class StateSpaceModel:
    A: sp.Matrix
    B: sp.Matrix
    C: sp.Matrix | None = None
    D: sp.Matrix | None = None

# -------- Canonical realization from TF --------

def controllable_canonical_from_tf(num_desc: List[sp.Expr], den_desc: List[sp.Expr]):
    a_desc = den_desc
    n = len(a_desc) - 1
    a_asc = coeffs_asc(a_desc[1:], n)
    b_asc = coeffs_asc(num_desc, n)
    A = sp.zeros(n)
    for i in range(n-1):
        A[i, i+1] = 1
    A[n-1, :] = sp.Matrix([[-ai for ai in a_asc]])
    B = sp.zeros(n, 1); B[n-1, 0] = 1
    C = sp.Matrix([b_asc])
    D = sp.Matrix([[0]])
    return A, B, C, D

# -------- Algebra helpers --------

def controllability_matrix(A: sp.Matrix, B: sp.Matrix) -> sp.Matrix:
    n = A.shape[0]
    blocks = [B]
    Ak = sp.eye(n)
    for _ in range(1, n):
        Ak = Ak * A
        blocks.append(Ak * B)
    return sp.Matrix.hstack(*blocks)

def observability_matrix(A: sp.Matrix, C: sp.Matrix) -> sp.Matrix:
    n = A.shape[0]
    blocks = [C]
    Ak = sp.eye(n)
    for _ in range(1, n):
        Ak = A*Ak
        blocks.append(C * Ak)
    return sp.Matrix.vstack(*blocks)

def is_diagonalizable_distinct(A: sp.Matrix) -> bool:
    evals = [ev for ev, mult in sp.Matrix.eigenvals(A).items()]
    return len(evals) == A.shape[0]

def alt_modal_ctrl(A: sp.Matrix, B: sp.Matrix):
    if not is_diagonalizable_distinct(A):
        return None, None, None
    try:
        P, D = A.diagonalize(reals_only=False, sort=False)
        F = P.inv() * B
        ok = all(any(F[i, j] != 0 for j in range(F.shape[1])) for i in range(F.shape[0]))
        return ok, P, F
    except Exception:
        return None, None, None

def alt_modal_obs(A: sp.Matrix, C: sp.Matrix):
    if not is_diagonalizable_distinct(A):
        return None, None, None
    try:
        P, D = A.diagonalize(reals_only=False, sort=False)
        CP = C * P
        ok = all(any(CP[i, j] != 0 for i in range(CP.shape[0])) for j in range(CP.shape[1]))
        return ok, P, CP
    except Exception:
        return None, None, None

def s_plane_minimality(num_desc: List[sp.Expr], den_desc: List[sp.Expr]):
    s = sym_s()
    N = sp.Poly(num_desc, s)
    D = sp.Poly(den_desc, s)
    g = sp.gcd(N, D)
    gcd_expr = sp.together(g.as_expr())
    ok = (g.degree() == 0)
    info: Dict = {}
    if not ok:
        info["gcd_factorized"] = sp.factor(gcd_expr)
        try:
            info["canceled_roots"] = {str(r): int(m) for r, m in sp.roots(gcd_expr).items()}
        except Exception:
            info["canceled_roots"] = "n/a"
    return ok, gcd_expr, info

def pbh_stabilizable(A: sp.Matrix, B: sp.Matrix, eps: float = 0.0):
    n = A.shape[0]
    I = sp.eye(n)
    bad = []
    for lam, mult in A.eigenvals().items():
        lam_c = complex(sp.N(lam))
        if lam_c.real >= -eps:
            M = sp.Matrix.hstack(lam * I - A, B)
            if M.rank() < n:
                bad.append(lam_c)
    return len(bad) == 0, bad

def pbh_detectable(A: sp.Matrix, C: sp.Matrix, eps: float = 0.0):
    n = A.shape[0]
    I = sp.eye(n)
    bad = []
    for lam, mult in A.eigenvals().items():
        lam_c = complex(sp.N(lam))
        if lam_c.real >= -eps:
            M = sp.Matrix.vstack(lam * I - A, C)
            if M.rank() < n:
                bad.append(lam_c)
    return len(bad) == 0, bad
