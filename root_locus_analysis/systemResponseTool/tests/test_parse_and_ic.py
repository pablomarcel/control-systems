# root_locus_analysis/systemResponseTool/tests/test_parse_and_ic.py
from __future__ import annotations
import numpy as np
from root_locus_analysis.systemResponseTool.core import Parser, ResponseEngine

def test_factor_poly_parse_equivalence():
    p = Parser()
    # (s+1)(s+2) = s^2 + 3s + 2
    tf = p.parse_sys_arg("tf; name=H; num=(s+1); den=(s+1)*(s+2)")
    assert np.allclose(tf.den, np.array([1.0, 3.0, 2.0]))

def test_ic_case1_step_equiv_matches_direct_linear_system():
    eng = ResponseEngine()
    A = np.array([[0.0, 1.0], [-1.0, -1.0]])
    x0 = np.array([1.0, 0.5])
    T = np.linspace(0, 1.0, 51)

    Xd = eng.ic_case1_direct(A, x0, T)
    Xs = eng.ic_case1_step_equiv(A, x0, T)
    # They are theoretically identical; allow small numerical noise
    assert Xd.shape == Xs.shape
    assert np.allclose(Xd, Xs, rtol=1e-4, atol=1e-6)
