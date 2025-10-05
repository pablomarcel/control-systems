# -*- coding: utf-8 -*-
import numpy as np
import control as ct
from stateSpaceDesign.controllerTool.core import controllable_companion_from_tf
from stateSpaceDesign.controllerTool.design import choose_N_for_feedback

def test_companion_realization_shapes():
    ss = controllable_companion_from_tf(np.array([1.0]), np.array([1.0, 0.0, 1.0, 0.0]))
    n = ss.A.shape[0]
    assert ss.A.shape == (n, n)
    assert ss.B.shape == (n, 1)
    assert ss.C.shape == (1, n)

def test_choose_N_integrator_case():
    G = ct.tf([1.0], [1.0, 0.0])  # 1/s
    Gc = ct.tf([1.0, 1.0], [1.0, 2.0])  # (s+1)/(s+2)
    N = choose_N_for_feedback(G, Gc)
    assert abs(N - 0.5) < 1e-9
