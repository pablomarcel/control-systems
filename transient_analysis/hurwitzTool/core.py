# =============================
# File: transient_analysis/hurwitzTool/core.py
# =============================
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Tuple

import numpy as np
import sympy as sp


# ---------- Data containers ----------
@dataclass(slots=True)
class Polynomial:
    """Real-coefficient polynomial stored with descending coefficients.

    The coefficient list is interpreted as ``[a0, a1, ..., an]`` for
    ``a0*s**n + a1*s**(n-1) + ... + an``.  The default polynomial variable is
    ``s``.  The field-level documentation is intentionally kept out of the
    class docstring so Sphinx/Napoleon does not emit duplicate object warnings
    for the dataclass fields when ``:members:`` is enabled in ``api.rst``.
    """

    a_desc: List[sp.Expr]
    var: sp.Symbol = sp.Symbol("s")

    @property
    def degree(self) -> int:
        """Return the polynomial degree."""
        return len(self.a_desc) - 1

    def as_expr(self) -> sp.Expr:
        """Return the polynomial as a SymPy expression."""
        n = self.degree
        s = self.var
        return sp.Add(*[self.a_desc[i] * s ** (n - i) for i in range(n + 1)])

    def is_numeric(self) -> bool:
        """Return ``True`` when all coefficients are numeric."""
        return all(sp.sympify(ai).is_number for ai in self.a_desc)


class HurwitzError(Exception):
    """Base exception for Hurwitz stability errors."""


# ---------- Hurwitz builders ----------
class HurwitzMatrixBuilder:
    """Build Hurwitz matrices from descending polynomial coefficients.

    The matrix convention used here is
    ``H[i, j] = a_{2*j + (1 - i)}``, with ``a_k = 0`` outside the coefficient
    range ``0 <= k <= n``.
    """

    @staticmethod
    @lru_cache(maxsize=None)
    def matrix_tuple(a_desc_tuple: Tuple[sp.Expr, ...]) -> Tuple[Tuple[sp.Expr, ...], ...]:
        """Return the Hurwitz matrix as a cacheable tuple of tuples."""
        a = list(a_desc_tuple)
        n = len(a) - 1

        def ak(k: int) -> sp.Expr:
            return a[k] if 0 <= k <= n else sp.Integer(0)

        return tuple(tuple(ak(2 * j + (1 - i)) for j in range(n)) for i in range(n))

    @classmethod
    def matrix(cls, a_desc: List[sp.Expr]) -> sp.Matrix:
        """Return the Hurwitz matrix as a SymPy ``Matrix``."""
        return sp.Matrix(cls.matrix_tuple(tuple(a_desc)))


class HurwitzMinors:
    """Compute and cache the leading principal Hurwitz minors."""

    @staticmethod
    @lru_cache(maxsize=None)
    def leading_minors(a_desc_tuple: Tuple[sp.Expr, ...]) -> Tuple[sp.Expr, ...]:
        """Return the leading principal minors ``Δ1`` through ``Δn``."""
        H = HurwitzMatrixBuilder.matrix(list(a_desc_tuple))
        n = H.shape[0]
        minors: List[sp.Expr] = []
        for k in range(1, n + 1):
            minors.append(sp.simplify(sp.factor(H[:k, :k].det())))
        return tuple(minors)

    @classmethod
    def minors(cls, a_desc: List[sp.Expr]) -> List[sp.Expr]:
        """Return the leading principal minors as a list."""
        return list(cls.leading_minors(tuple(a_desc)))


class HurwitzConditions:
    """Build Hurwitz or Lienard-Chipart inequality sets."""

    @staticmethod
    def lienard_indices(n: int) -> List[int]:
        """Return the required minor indices for the Lienard-Chipart test."""
        # even n -> {2,4,...,n}; odd n -> {1,3,...,n}
        return list(range(2, n + 1, 2)) if n % 2 == 0 else list(range(1, n + 1, 2))

    @classmethod
    def inequalities(cls, poly: Polynomial, use_lienard: bool) -> Tuple[List[sp.Rel], str]:
        """Return symbolic positivity inequalities and the criterion label.

        Strict SymPy relations are created with ``evaluate=False`` so display
        and tests can still show relations such as ``1 > 0`` instead of folding
        them immediately to ``True``.
        """
        a = poly.a_desc
        n = poly.degree
        delta = HurwitzMinors.minors(a)

        def gt0(expr: sp.Expr) -> sp.Rel:
            return sp.StrictGreaterThan(expr, 0, evaluate=False)

        ineqs: List[sp.Rel] = []
        if use_lienard:
            req = cls.lienard_indices(n)
            ineqs.extend(gt0(ai) for ai in a)
            ineqs.extend(gt0(delta[k - 1]) for k in req)
            used = f"Lienard-Chipart Δ{req} + all coefficients > 0"
        else:
            ineqs.append(gt0(a[0]))
            ineqs.extend(gt0(dk) for dk in delta)
            used = "Full Hurwitz Δ1..Δn"
        return ineqs, used


# ---------- Numeric evaluation / scans ----------
class NumericChecker:
    """Evaluate Hurwitz conditions numerically and run parameter scans."""

    def __init__(self, tol: float = 1e-10) -> None:
        self.tol = tol

    def eval_numeric(self, expr: sp.Expr, subs: Dict[sp.Symbol, float]) -> float:
        """Evaluate a numeric or symbolic expression after substitutions."""
        e = sp.sympify(expr)
        if subs:
            e = e.subs(subs)
        return float(sp.N(e))

    def check(self, poly: Polynomial, subs: Dict[sp.Symbol, float], use_lienard: bool) -> Tuple[bool, Dict]:
        """Check whether a polynomial satisfies the selected stability test."""
        a_num = [self.eval_numeric(ai, subs) for ai in poly.a_desc]
        H = HurwitzMatrixBuilder.matrix([sp.Float(x) for x in a_num])
        delta = HurwitzMinors.minors([sp.Float(x) for x in a_num])
        delta_num = [float(d) for d in delta]
        a0_pos = a_num[0] > self.tol
        coeff_pos = all(x > self.tol for x in a_num)
        n = poly.degree

        if use_lienard:
            req = HurwitzConditions.lienard_indices(n)
            conds = [delta_num[k - 1] > self.tol for k in req]
            ok = a0_pos and coeff_pos and all(conds)
            used = f"Lienard-Chipart Δ{req} + all coefficients > 0"
        else:
            conds = [v > self.tol for v in delta_num]
            ok = a0_pos and all(conds)
            used = "Full Hurwitz Δ1..Δn"

        return ok, {
            "used": used,
            "a_numeric": a_num,
            "H": H,
            "Δ": delta,
            "Δ_numeric": delta_num,
            "a0>0": a0_pos,
            "coeff>0": coeff_pos,
            "conds": conds,
        }

    def rhp_roots(self, a_num: List[float]) -> int:
        """Count roots whose real part is greater than the numeric tolerance."""
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
        """Sample stability over one scalar parameter."""
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
        sx: sp.Symbol,
        xlo: float,
        xhi: float,
        dx: float,
        sy: sp.Symbol,
        ylo: float,
        yhi: float,
        dy: float,
        use_lienard: bool,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Sample stability over two scalar parameters and return a Boolean grid."""
        if dx == 0 or dy == 0:
            raise ValueError("scan2d steps cannot be zero")
        if (xhi - xlo) * dx < 0:
            dx = -dx
        if (yhi - ylo) * dy < 0:
            dy = -dy

        xs = np.arange(xlo, xhi + 0.5 * abs(dx), dx, dtype=float)
        ys = np.arange(ylo, yhi + 0.5 * abs(dy), dy, dtype=float)
        Z = np.zeros((len(ys), len(xs)), dtype=bool)
        for iy, y in enumerate(ys):
            for ix, x in enumerate(xs):
                ok, _ = self.check(poly, {sx: x, sy: y}, use_lienard)
                Z[iy, ix] = ok
        return xs, ys, Z
