
from __future__ import annotations
import sympy as sp
from stateSpaceAnalysis.stateTool.utils import (
    parse_matrix, split_fraction_raw, parse_poly_text, parse_poly,
    normalize_monic, ensure_proper, coeffs_asc, pretty, to_numeric, to_expr_s, sym_s
)

def test_parse_matrix_formats():
    M1 = parse_matrix("0 1; -2 -3")
    M2 = parse_matrix("[[0,1],[-2,-3]]")
    assert M1.shape == (2,2) and M2.shape == (2,2)

def test_split_fraction_and_poly_text():
    n, d = split_fraction_raw("(s+1)/(s^2+1)")
    assert "s+1" in n and "s^2+1" in d
    coeffs = parse_poly_text("s^2 + 3*s + 2")
    assert list(map(sp.nsimplify, coeffs)) == [1,3,2]

def test_parse_poly_and_normalize_and_ensure_proper():
    num = parse_poly("s+3")
    den = parse_poly("s^2+3*s+2")
    num_m, den_m = normalize_monic(num, den)
    num_p, den_p, dfeed = ensure_proper(num_m, den_m)
    assert dfeed == 0 and len(den_p) == 3

def test_coeffs_asc_pretty_numeric():
    asc = coeffs_asc([2,3], 3)
    assert len(asc) == 3
    Ms = sp.Matrix([[1,2],[3,4]])
    assert isinstance(pretty(Ms), str)
    arr = to_numeric(Ms, 6)
    assert arr.shape == (2,2)

def test_to_expr_aliases():
    e = to_expr_s("X^2 + 1")
    assert str(sp.expand(e)) == "s**2 + 1"
    assert sym_s().name == "s"
