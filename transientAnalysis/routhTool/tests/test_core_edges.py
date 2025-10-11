
from __future__ import annotations
import importlib.util
import pytest

from transientAnalysis.routhTool.core import RouthArrayBuilder, RouthConfig

_SYMPY_AVAILABLE = importlib.util.find_spec("sympy") is not None

def test_epsilon_trick_numeric():
    # Make the second row leading element zero (a1 = 0, a3 != 0)
    coeffs = [1.0, 0.0, 2.0, 3.0]
    b = RouthArrayBuilder(RouthConfig(eps=1e-8))
    A, fc, degs = b.build_array(coeffs)
    # first column's second row should be replaced by epsilon
    assert abs(fc[1] - b.cfg.eps) < 1e-20

def test_verify_with_roots_stable_cubic():
    coeffs = [1.0, 3.0, 3.0, 1.0]  # (s+1)^3 -> no RHP roots
    b = RouthArrayBuilder()
    rhp = b.verify_with_roots(coeffs)
    # numpy may not be present in some envs; accept None or 0
    assert (rhp is None) or (rhp == 0)

@pytest.mark.skipif(not _SYMPY_AVAILABLE, reason="SymPy not installed")
def test_symbolic_sign_changes_returns_none():
    import sympy as sp
    K = sp.Symbol("K", real=True)
    coeffs = [1, 5, 6, K]
    b = RouthArrayBuilder()
    A, fc, _ = b.build_array(coeffs)
    assert b.sign_changes_first_column(fc) is None

@pytest.mark.skipif(not _SYMPY_AVAILABLE, reason="SymPy not installed")
def test_hurwitz_minors_length():
    coeffs = [1, 2, 3, 4, 5]
    b = RouthArrayBuilder()
    minors = b.hurwitz_minors(coeffs)
    assert len(minors) == 4
