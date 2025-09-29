# ---------------------------------
# File: transientAnalysis/icTool/tests/test_core_equivalence.py
# ---------------------------------
from __future__ import annotations
import numpy as np
import numpy.testing as npt
from transientAnalysis.icTool.core import ICProblem, ICSolver
from transientAnalysis.icTool.utils import time_grid


def test_case1_direct_equals_step_equiv_states():
    A = np.array([[0,1],[-6,-5]], float)
    x0 = np.array([2,1], float)
    T = time_grid(1.0, 0.01)
    s = ICSolver(ICProblem(A=A, x0=x0))
    d = s.case1_direct(T)
    e = s.case1_step_equiv(T)
    npt.assert_allclose(d.Y, e.Y, rtol=1e-7, atol=1e-8)
    npt.assert_allclose(d.T, e.T)


def test_case2_direct_equals_step_equiv_outputs():
    A = np.array([[0,1,0],[0,0,1],[-10,-17,-8]], float)
    C = np.array([[1,0,0]], float)
    x0 = np.array([2,1,0.5], float)
    T = time_grid(0.8, 0.005)
    s = ICSolver(ICProblem(A=A, x0=x0, C=C))
    d = s.case2_direct(T)
    e = s.case2_step_equiv(T)
    npt.assert_allclose(d.Y, e.Y, rtol=1e-7, atol=1e-8)