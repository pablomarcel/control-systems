import sympy as sp
from stateSpaceAnalysis.stateRepTool import utils

def test_parse_poly_csv_and_expr():
    c_csv = utils.parse_poly("1, 3, 2")
    c_expr = utils.parse_poly("s^2 + 3*s + 2")
    assert c_csv == c_expr == [1, 3, 2]

def test_parse_tf_and_normalize_monic():
    num, den = utils.parse_tf_string("(s+3)/(s^2+3*s+2)")
    n2, d2 = utils.normalize_monic(num, den)
    assert d2[0] == 1 and n2[0] == 1

def test_ensure_proper_equal_degree_extracts_Dfeed():
    num = utils.parse_poly("s^2 + 2*s + 1")
    den = utils.parse_poly("s^2 + 1*s + 1")
    nmp, dmp, Dfeed, rem = utils.ensure_proper(num, den)
    assert Dfeed != 0
    assert len(nmp) <= len(dmp)

def test_coeffs_asc_square_free_and_tf_from_numden():
    asc = utils.coeffs_asc([1, 3, 2], 3)
    assert asc == [2, 3, 1]
    poly = sp.Poly([1, 3, 2], utils.sym_s())
    assert utils.square_free(poly) is True
    G = utils.tf_from_numden([1,3], [1,3,2])
    assert str(sp.together(G)) == str(sp.together(sp.sympify("(s+3)/(s^2+3*s+2)", locals={"s": utils.sym_s()})))
