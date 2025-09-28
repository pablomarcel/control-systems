# =============================
# File: transientAnalysis/hurwitzTool/tests/test_core_minors.py
# =============================
from __future__ import annotations
import sympy as sp
from transientAnalysis.hurwitzTool.core import Polynomial, HurwitzMatrixBuilder, HurwitzMinors, HurwitzConditions


def test_hurwitz_matrix_and_minors_numeric():
    p = Polynomial([1, 5, 6, 7])  # s^3 + 5 s^2 + 6 s + 7
    H = HurwitzMatrixBuilder.matrix(p.a_desc)
    assert H.shape == (3, 3)
    Δ = HurwitzMinors.minors(p.a_desc)
    assert len(Δ) == 3
    # All minors should be positive for a strictly stable cubic with positive coeffs (not always sufficient).
    assert all(d.evalf() > 0 for d in Δ)


def test_hurwitz_inequalities_symbolic():
    K = sp.Symbol("K")
    p = Polynomial([1, 5, 6, K])
    ineqs, used = HurwitzConditions.inequalities(p, use_lienard=False)
    assert any(str(ineq).startswith("1 > 0") for ineq in ineqs)
    assert used.startswith("Full Hurwitz")