
from __future__ import annotations
import numpy as np
from control_systems.converterTool.core import TFModel, SSModel, ConverterEngine

def test_tf_to_ss_roundtrip_siso():
    eng = ConverterEngine()
    tfm = TFModel(np.array([1.0, 0.0]), np.array([1.0,14.0,56.0,160.0]))
    ss = eng.tf_to_ss(tfm)
    G = eng.ss_to_tf(ss)
    n1,d1 = eng.normalize(*eng.coeffs_from_tf(tfm.to_ct()))
    n2,d2 = eng.normalize(*eng.coeffs_from_tf(G))
    assert np.allclose(n1, n2, atol=1e-9)
    assert np.allclose(d1, d2, atol=1e-9)
