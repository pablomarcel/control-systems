
from __future__ import annotations
import numpy as np
from frequencyResponse.bodeTool.utils import pretty_poly, pretty_tf, tf_arrays
import control as ct

def test_pretty_poly_and_tf_arrays():
    G = ct.tf([1, 0.8, 1], [1, 3, 3, 1])
    n, d = tf_arrays(G)
    assert n.tolist() == [1,0.8,1]
    assert d.tolist() == [1,3,3,1]
    s = pretty_poly(n)
    assert "s^2" in s and "0.8s" in s and "+ 1" in s
    s_tf = pretty_tf(G)
    assert s_tf.startswith("(") and ") / (" in s_tf
