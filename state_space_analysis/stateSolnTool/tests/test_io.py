
import pytest
import sympy as sp
from state_space_analysis.stateSolnTool.io import (
    parse_poly, parse_tf_string, normalize_monic, ensure_proper,
    coeffs_asc, parse_vec_csv
)
from state_space_analysis.stateSolnTool.utils import sym_s

def test_parse_poly_csv_and_expr():
    coeffs_csv = parse_poly("1, 3, 2")
    assert [int(c) for c in coeffs_csv] == [1,3,2]
    coeffs_expr = parse_poly("s^2 + 3*s + 2")
    assert [int(c) for c in coeffs_expr] == [1,3,2]

def test_parse_tf_and_normalize():
    num, den = parse_tf_string("(s+3)/(s^2+3*s+2)")
    n2, d2 = normalize_monic(num, den)
    assert d2[0] == 1 and n2[0] == num[0]/den[0]

def test_ensure_proper_and_coeffs_asc():
    s = sym_s()
    num, den = [1, 0], [1, 1]  # deg equal -> constant feedthrough expected 1
    n3, d3, D = ensure_proper(num, den)
    assert D == 1
    asc = coeffs_asc([1,2,3], 2)
    assert asc == [3,2]

def test_parse_vec_csv():
    v = parse_vec_csv("1,2", 2)
    assert list(map(int, list(v))) == [1,2]
    with pytest.raises(ValueError):
        parse_vec_csv("1", 2)
