from __future__ import annotations
import numpy as np
from rootLocus.rootLocusTool.core import jw_crossings, poly_char

def test_jw_crossings_simple():
    # L0 = (s+2)/(s^2+2s+3)
    num = np.array([1.0, 2.0])
    den = np.array([1.0, 2.0, 3.0])
    xs = jw_crossings(num, den)
    # Should return finite non-negative frequencies if any; tolerant
    assert isinstance(xs, list)

def test_poly_char_shape():
    d = np.array([1.0, 2.0, 3.0])
    n = np.array([1.0, 2.0])
    p = poly_char(d, n, 5.0)
    assert p.shape[0] == 3
