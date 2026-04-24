from __future__ import annotations
import numpy as np
from transient_analysis.responseTool.core import SSModel, TFModel, ResponseEngine


def test_ramp_ss_matches_augmented_vs_direct():
    A = np.array([[0, 1], [-1, -1]], float)
    B = np.array([[0], [1]], float)
    C = np.array([[1, 0]], float)
    D = np.array([[0]], float)
    eng = ResponseEngine()
    T, z, y_ramp = eng.ramp_ss(SSModel(A, B, C, D), tfinal=2.0, dt=0.01)
    assert T.shape == z.shape == y_ramp.shape
    # They should be (nearly) identical; allow small numerical tolerance
    err = float(np.max(np.abs(z - y_ramp)))
    assert err < 1e-3


def test_lsim_tf_ramp_shapes():
    eng = ResponseEngine()
    T, y, U = eng.lsim_tf(TFModel(num=np.array([2, 1]), den=np.array([1, 1, 1])), u="ramp", tfinal=1.0, dt=0.01)
    assert T.shape == y.shape == U.shape
    assert T.ndim == y.ndim == U.ndim == 1