
from __future__ import annotations

import numpy as np
import control as ct

from rootLocus.systemResponseTool.core import ResponseEngine

def test_engine_step_impulse_forced_and_stepinfo():
    # First-order stable system
    G = ct.tf([1.0], [1.0, 1.0])
    eng = ResponseEngine()
    T = np.linspace(0, 0.2, 5)

    t_step, y_step = eng.step(G, T)
    assert y_step.shape[-1] == len(T)

    t_imp, y_imp = eng.impulse(G, T)
    assert y_imp.shape[-1] == len(T)

    U = np.ones_like(T)
    t_forced, y_forced, _ = eng.forced(G, U, T)
    assert y_forced.shape[-1] == len(T)

    info = eng.step_info_safe(G)
    assert "RiseTime" in info and "Overshoot" in info

def test_engine_ic1_ic2_equivalents():
    A = np.array([[0.0, 1.0], [-1.0, -1.0]])
    x0 = np.array([1.0, 0.5])
    T = np.linspace(0, 0.2, 5)

    eng = ResponseEngine()
    Xd = eng.ic_case1_direct(A, x0, T)
    Xs = eng.ic_case1_step_equiv(A, x0, T)
    assert Xd.shape == Xs.shape
    assert np.allclose(Xd, Xs, rtol=1e-4, atol=1e-6)

    C_sel = np.eye(2)
    Yd = eng.ic_case2_direct(A, C_sel, x0, T)
    Ys = eng.ic_case2_step_equiv(A, C_sel, x0, T)
    assert Yd.shape == Ys.shape
    assert np.allclose(Yd, Ys, rtol=1e-4, atol=1e-6)
