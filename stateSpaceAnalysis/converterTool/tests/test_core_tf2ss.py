from __future__ import annotations
import numpy as np
import control as ct
from stateSpaceAnalysis.converterTool.core import SystemConverter

def test_tf_to_ss_and_back_siso():
    conv = SystemConverter()
    num = [1, 0]
    den = [1, 14, 56, 160]
    res = conv.tf_to_ss(num, den)
    assert res.SS is not None
    # roundtrip
    G2 = ct.ss2tf(res.SS)
    # compare numerically ignoring scale
    n1, d1 = num, den
    from stateSpaceAnalysis.converterTool.utils import coeffs_from_tf
    n2, d2 = coeffs_from_tf(G2)
    assert len(d2) == len(d1)
    # check poles roughly equal
    p1 = np.sort(np.roots(d1))
    p2 = np.sort(np.roots(d2))
    assert np.allclose(p1, p2, atol=1e-8)
