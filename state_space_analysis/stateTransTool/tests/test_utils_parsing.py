
from __future__ import annotations
import sympy as sp
import numpy as np
from state_space_analysis.stateTransTool import utils as U

def test_parse_poly_csv_and_expr():
    assert U.parse_poly("1, 3, 2") == [sp.Integer(1), sp.Integer(3), sp.Integer(2)]
    coeffs = U.parse_poly("s^2 + 3*s + 2")
    assert coeffs == [1, 3, 2]

def test_parse_tf_string_and_normalize():
    # NOTE: utils.parse_tf_string expects explicit '*' (no implicit multiplication)
    num, den = U.parse_tf_string("(s+3)/(s^2+3*s+2)")
    numN, denN = U.normalize_monic(num, den)
    assert denN[0] == 1
    assert numN[0] == 1  # leading num remains 1 after monic normalize

def test_ensure_proper_and_coeffs_asc():
    # Proper of equal degree -> extracts D and reduces numerator
    num = [1, 0]     # s
    den = [1, 1]     # s + 1
    n2, d2, D = U.ensure_proper(num, den)
    assert D == 1    # s/(s+1) -> 1 - 1/(s+1)
    # coeffs_asc pads to n
    asc = U.coeffs_asc([1, 2, 3], 5)
    assert asc == [3, 2, 1, 0, 0]

def test_square_free_and_numeric_pretty():
    s = U.sym_s()
    D1 = sp.Poly((s+1)*(s+2), s)
    D2 = sp.Poly((s+1)**2, s)
    assert U.square_free(D1) is True
    assert U.square_free(D2) is False
    M = sp.Matrix([[1, s],[0, 1]])
    # pretty returns a string; to_numeric returns ndarray
    assert isinstance(U.pretty_matrix(M), str)
    arr = U.to_numeric(M.subs(s, 2), 6)
    assert isinstance(arr, np.ndarray) and arr.shape == (2,2)
