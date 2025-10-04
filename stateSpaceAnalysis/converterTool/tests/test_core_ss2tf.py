from __future__ import annotations
import numpy as np
from stateSpaceAnalysis.converterTool.core import SystemConverter

def test_ss_to_tf_basic():
    conv = SystemConverter()
    A = np.array([[0,1,0],[0,0,1],[-5,-25,-5]], float)
    B = np.array([[0],[25],[-120]], float)
    C = np.array([[1,0,0]], float)
    D = np.array([[0]], float)
    res = conv.ss_to_tf(A,B,C,D)
    assert res.G is not None
    # check numerator/denominator lengths make sense
    num, den = res.G.num[0][0], res.G.den[0][0]
    assert len(den) == 4
    assert len(num) <= len(den)
