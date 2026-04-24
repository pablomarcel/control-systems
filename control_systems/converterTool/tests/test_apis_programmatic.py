
from __future__ import annotations
import numpy as np
from control_systems.converterTool.apis import convert_tf_to_ss, convert_ss_to_tf

def test_programmatic_convert_roundtrip():
    num = np.array([1.0, 0.0])
    den = np.array([1.0, 14.0, 56.0, 160.0])
    ss = convert_tf_to_ss(num, den)
    G = convert_ss_to_tf(ss.A, ss.B, ss.C, ss.D)
    # Expect equal TF back (normalized)
    import control as ct
    def coeffs(G):
        try:
            n, d = ct.tfdata(G, squeeze=True)
        except TypeError:
            n, d = ct.tfdata(G)
            while isinstance(n, (list, tuple)): n = n[0]
            while isinstance(d, (list, tuple)): d = d[0]
        return np.asarray(n, float).ravel(), np.asarray(d, float).ravel()
    n1, d1 = coeffs(ct.TransferFunction(num, den))
    n2, d2 = coeffs(G)
    # Normalize leading coefficient to 1 for comparison
    n1, d1 = n1/d1[0], d1/d1[0]
    n2, d2 = n2/d2[0], d2/d2[0]
    assert np.allclose(n1, n2)
    assert np.allclose(d1, d2)
