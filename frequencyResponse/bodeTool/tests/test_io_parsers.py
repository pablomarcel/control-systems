from __future__ import annotations
import numpy as np
from frequencyResponse.bodeTool import io as io_mod

def test_parse_list_and_roots():
    arr = io_mod.parse_list("1, 0.8; 1")
    assert np.allclose(arr, [1.0, 0.8, 1.0])

    roots = io_mod.parse_roots("0.5, -1, 2+3j, 2-3i; j; -j")
    assert roots[0] == 0.5
    assert roots[1] == -1
    assert complex(2,3) in roots and complex(2,-3) in roots
    assert complex(0,1) in roots and complex(0,-1) in roots

def test_poly_from_s_expr_basic_and_s_over_tau():
    c = io_mod.poly_from_s_expr("s^2 + 4s + 5")
    assert np.allclose(c, [1,4,5])
    c2 = io_mod.poly_from_s_expr("( s^2 + 0.8 s + 1 )")
    assert np.allclose(c2, [1,0.8,1])
    c3 = io_mod.poly_from_s_expr("(s/5 + 1)")
    assert np.allclose(c3, [0.2, 1.0])

def test_parse_factors_parentheses_tokenizer_and_K():
    poly = io_mod.parse_factors("s (s/30 + 1) (s/3 + 1)")
    # degree should be 3 -> length 4
    assert len(poly) == 4, f"expected length 4 (degree+1), got {len(poly)}: {poly}"
    poly2 = io_mod.parse_factors("K (s+1)", Kval=4.2)
    assert np.allclose(poly2, [4.2, 4.2])

def test_tokenizer_edge_cases():
    # s * (s+1) * (s/2 + 1) => (0.5)s^3 + 1.5 s^2 + 1 s + 0
    poly = io_mod.parse_factors(" s  * (s+1)   * ( s/2 + 1 ) ")
    expected = np.array([0.5, 1.5, 1.0, 0.0])
    assert len(poly) == 4, f"degree mismatch; poly: {poly}"
    assert np.allclose(poly, expected), f"coeff mismatch; expected {expected}, got {poly}"
