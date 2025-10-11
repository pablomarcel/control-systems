
from __future__ import annotations

import numpy as np

from rootLocus.systemResponseTool.utils import (
    parse_vector, parse_matrix, parse_poly, split_top_level,
    time_grid, default_palette
)

def test_parse_vector_and_matrix():
    v = parse_vector("[1, 2; 3]")
    assert v.shape == (3,)
    assert np.allclose(v, [1,2,3])

    M = parse_matrix("[1,2; 3,4]")
    assert M.shape == (2,2)
    assert np.allclose(M, [[1,2],[3,4]])

def test_parse_poly_numeric_and_factor():
    p1 = parse_poly("1, 3, 3, 1")
    assert np.allclose(p1, [1,3,3,1])

    # (s+1)^3 => 1,3,3,1
    p2 = parse_poly("(s+1)*(s+1)*(s+1)")
    assert np.allclose(p2, [1,3,3,1])

    # 2*(s+2)*(s+3) => 2*s^2 + 10*s + 12
    p3 = parse_poly("2*(s+2)*(s+3)")
    assert np.allclose(p3, [2,10,12])

def test_split_top_level_and_time_grid_palette():
    toks = split_top_level("tf; name=G; num=1,2; den=1,3,3,1")
    assert toks[0] == "tf"
    assert len(toks) >= 3

    T = time_grid(0.2, 0.05)
    assert np.isclose(T[0], 0.0) and np.isclose(T[-1], 0.2)
    assert len(T) == 5

    pal = default_palette()
    assert isinstance(pal, list) and len(pal) >= 5
