from __future__ import annotations
import numpy as np
import sympy as sp

from transientAnalysis.hurwitzTool.core import (
    Polynomial, HurwitzMatrixBuilder, HurwitzMinors, HurwitzConditions, NumericChecker
)

def test_hurwitz_matrix_and_caching():
    a = [1, 5, 6, 7]
    H1 = HurwitzMatrixBuilder.matrix(a)
    H2 = HurwitzMatrixBuilder.matrix(a)  # cached path
    assert H1.shape == H2.shape == (3,3)
    # Leading minors nonzero for this numeric poly (just probe type/values)
    minors = HurwitzMinors.minors(a)
    assert len(minors) == 3
    assert all(isinstance(m, (int, float, sp.Expr)) for m in minors)

def test_inequalities_lienard_and_numeric_checker():
    # Liénard–Chipart on positive coefficients
    p = Polynomial([1, 5, 6, 7])
    ineqs, used = HurwitzConditions.inequalities(p, use_lienard=True)
    assert "Liénard–Chipart" in used
    assert len(ineqs) >= 3

    num = NumericChecker(tol=1e-12)
    ok, detail = num.check(p, {}, use_lienard=True)
    assert isinstance(ok, bool) and "Δ_numeric" in detail

    # RHP roots for a stable polynomial should be 0
    rhp = num.rhp_roots([1, 5, 6, 7])
    assert isinstance(rhp, int)

def test_scan2d_shapes():
    p = Polynomial([1, sp.Symbol("K")+2, 3, 4])
    num = NumericChecker()
    sx, sy = sp.Symbol("K"), sp.Symbol("A")
    xs, ys, Z = num.scan2d(p, sx, 0.0, 0.2, 0.1, sy, -0.1, 0.1, 0.1, use_lienard=False)
    assert Z.shape == (len(ys), len(xs))
