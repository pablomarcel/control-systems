# =============================
# File: transient_analysis/hurwitzTool/core.py
# =============================
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import List, Dict, Tuple

import numpy as np
import sympy as sp


# ---------- Data containers ----------
@dataclass(slots=True)
class Polynomial:
    """
    Real-coefficient polynomial p(s) with *descending* coefficients.

    Attributes
    ----------
    a_desc : list of sympy.Expr
        [a0, a1, ..., an] representing a0*s^n + a1*s^(n-1) + ... + an.
    var : sympy.Symbol
        Symbol for the polynomial variable (default s).
    """
    a_desc: List[sp.Expr]
    var: sp.Symbol = sp.Symbol("s")

    @property
    def degree(self) -> int:
        return len(self.a_desc) - 1

    def as_expr(self) -> sp.Expr:
        n = self.degree
        s = self.var
        return sp.Add(*[self.a_desc[i] * s ** (n - i) for i in range(n + 1)])

    def is_numeric(self) -> bool:
        return all(ai.is_number for ai in self.a_desc)


class HurwitzError(Exception):
    pass


# ---------- Hurwitz builders ----------
class HurwitzMatrixBuilder:
    """
    Builds the Hurwitz matrix from descending coefficients.

    H[i, j] = a_{2*j + (1 - i)} with a_k = 0 outside [0..n].
    """

    @staticmethod
    @lru_cache(maxsize=None)
    def matrix_tuple(a_desc_tuple: Tuple[sp.Expr, ...]) -> Tuple[Tuple[sp.Expr, ...], ...]:
        a = list(a_desc_tuple)
        n = len(a) - 1

        def ak(k: int) -> sp.Expr:
            return a[k] if 0 <= k <= n else sp.Integer(0)

        H = tuple(tuple(ak(2 * j + (1 - i)) for j in range(n)) for i in range(n))
        return H

    @classmethod
    def matrix(cls, a_desc: List[sp.Expr]) -> sp.Matrix:
        Ht = cls.matrix_tuple(tuple(a_desc))
        return sp.Matrix(Ht)


class HurwitzMinors:
    """Computes leading principal minors Δ1..Δn and caches symbolic factors."""

    @staticmethod
    @lru_cache(maxsize=None)
    def leading_minors(a_desc_tuple: Tuple[sp.Expr, ...]) -> Tuple[sp.Expr, ...]:
        H = HurwitzMatrixBuilder.matrix(list(a_desc_tuple))
        n = H.shape[0]
        minors: List[sp.Expr] = []
        for k in range(1, n + 1):
            minors.append(sp.simplify(sp.factor(H[:k, :k].det())))
        return tuple(minors)

    @classmethod
    def minors(cls, a_desc: List[sp.Expr]) -> List[sp.Expr]:
        return list(cls.leading_minors(tuple(a_desc)))


class HurwitzConditions:
    """Builds the Hurwitz or Liénard–Chipart inequality set."""

    @staticmethod
    def lienard_indices(n: int) -> List[int]:
        # even n -> {2,4,...,n}, odd n -> {1,3,...,n}
        return list(range(2, n + 1, 2)) if n % 2 == 0 else list(range(1, n + 1, 2))

    @classmethod
    def inequalities(cls, poly: Polynomial, use_lienard: bool) -> Tuple[List[sp.Rel], str]:
        """
        Return a list of *relational* inequalities (kept as SymPy relations, not simplified
        to booleans) and a string describing which criterion is used. This preserves
        forms like '1 > 0' for testing and display.
        """
        a = poly.a_desc
        n = poly.degree
        Δ = HurwitzMinors.minors(a)

        def gt0(expr: sp.Expr) -> sp.Rel:
            # Keep strict relational form; prevent folding to True/False.
            return sp.StrictGreaterThan(expr, 0, evaluate=False)

        ineqs: List[sp.Rel] = []
        if use_lienard:
            req = cls.lienard_indices(n)
            # All coefficients > 0
            ineqs.extend(gt0(ai) for ai in a)
            # Required subset of minors > 0
            ineqs.extend(gt0(Δ[k - 1]) for k in req)
            used = f"Liénard–Chipart Δ{req} + all coefficients > 0"
        else:
            # Full Hurwitz: a0 > 0 and all leading principal minors > 0
            ineqs.append(gt0(a[0]))
            ineqs.extend(gt0(dk) for dk in Δ)
            used = "Full Hurwitz Δ1..Δn"
        return ineqs, used


# ---------- Numeric evaluation / scans ----------
class NumericChecker:
    def __init__(self, tol: float = 1e-10) -> None:
        self.tol = tol

    def eval_numeric(self, expr: sp.Expr, subs: Dict[sp.Symbol, float]) -> float:
        """
        Safely evaluate possibly-plain-numeric or symbolic expressions with substitutions.
        Handles Python ints/floats by coercing to SymPy first.
        """
        e = sp.sympify(expr)
        if subs:
            e = e.subs(subs)
        return float(sp.N(e))

    def check(self, poly: Polynomial, subs: Dict[sp.Symbol, float], use_lienard: bool) -> Tuple[bool, Dict]:
        a_num = [self.eval_numeric(ai, subs) for ai in poly.a_desc]
        H = HurwitzMatrixBuilder.matrix([sp.Float(x) for x in a_num])
        Δ = HurwitzMinors.minors([sp.Float(x) for x in a_num])
        Δ_num = [float(d) for d in Δ]
        a0_pos = (a_num[0] > self.tol)
        n = poly.degree
        if use_lienard:
            req = HurwitzConditions.lienard_indices(n)
            coeff_pos = all(x > self.tol for x in a_num)
            conds = [Δ_num[k - 1] > self.tol for k in req]
            ok = a0_pos and coeff_pos and all(conds)
            used = f"Liénard–Chipart Δ{req} + all coefficients > 0"
        else:
            conds = [v > self.tol for v in Δ_num]
            ok = a0_pos and all(conds)
            used = "Full Hurwitz Δ1..Δn"
        return ok, {
            "used": used,
            "a_numeric": a_num,
            "H": H,
            "Δ": Δ,
            "Δ_numeric": Δ_num,
            "a0>0": a0_pos,
            "coeff>0": all(x > self.tol for x in a_num),
            "conds": conds,
        }

    def rhp_roots(self, a_num: List[float]) -> int:
        roots = np.roots(np.array(a_num, dtype=float))
        return int(np.sum(np.real(roots) > self.tol))

    # --- scans ---
    def scan1d(
        self,
        poly: Polynomial,
        sym: sp.Symbol,
        lo: float,
        hi: float,
        step: float,
        use_lienard: bool,
    ) -> List[Tuple[float, bool]]:
        if step == 0:
            raise ValueError("scan step cannot be zero")
        if (hi - lo) * step < 0:
            step = -step
        xs: List[Tuple[float, bool]] = []
        t = lo
        while (step > 0 and t <= hi + 1e-12) or (step < 0 and t >= hi - 1e-12):
            ok, _ = self.check(poly, {sym: t}, use_lienard)
            xs.append((t, ok))
            t += step
        return xs

    def scan2d(
        self,
        poly: Polynomial,
        sx: sp.Symbol, xlo: float, xhi: float, dx: float,
        sy: sp.Symbol, ylo: float, yhi: float, dy: float,
        use_lienard: bool,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        xs = np.arange(xlo, xhi + 0.5 * abs(dx), dx, dtype=float)
        ys = np.arange(ylo, yhi + 0.5 * abs(dy), dy, dtype=float)
        Z = np.zeros((len(ys), len(xs)), dtype=bool)
        for iy, y in enumerate(ys):
            for ix, x in enumerate(xs):
                ok, _ = self.check(poly, {sx: x, sy: y}, use_lienard)
                Z[iy, ix] = ok
        return xs, ys, Z
