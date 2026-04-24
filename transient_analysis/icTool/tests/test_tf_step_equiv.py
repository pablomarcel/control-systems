# ---------------------------------
# File: transient_analysis/icTool/tests/test_tf_step_equiv.py
# ---------------------------------
from __future__ import annotations
import numpy as np
import numpy.testing as npt
import control as ct
from transient_analysis.icTool.core import ICProblem, ICSolver
from transient_analysis.icTool.tfcore import TfProblem, TfSolver
from transient_analysis.icTool.utils import time_grid


def test_tf_step_equiv_matches_state_space_for_ogata_ex58():
    # Ogata Ex 5-8 parameters
    m,b,k = 1.0, 3.0, 2.0
    x0,v0 = 0.10, 0.05
    # State-space zero-input output y=x
    A = np.array([[0,1],[-k/m, -b/m]], float)
    C = np.array([[1,0]], float)
    x0_vec = np.array([x0, v0], float)
    T = time_grid(5.0, 0.01)
    ss_d = ICSolver(ICProblem(A=A, x0=x0_vec, C=C)).case2_direct(T)

    # TF step-equivalent using solver
    pb = TfProblem(den=np.array([m,b,k], float), m=m, b=b, k=k, x0=x0, v0=v0)
    T2, Y2 = TfSolver(pb).step_equiv_output(T)

    npt.assert_allclose(ss_d.Y, Y2, rtol=2e-7, atol=2e-8)
    npt.assert_allclose(ss_d.T, T2)