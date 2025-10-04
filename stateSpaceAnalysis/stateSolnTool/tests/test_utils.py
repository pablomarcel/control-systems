
import sympy as sp
from stateSpaceAnalysis.stateSolnTool import utils

def test_symbols_and_expr():
    s = utils.sym_s()
    t = utils.sym_t()
    assert str(s) == "s"
    assert str(t) == "t"
    e_s = utils.to_expr_s("s^2 + 3*s + 2")
    assert e_s.subs({s:1}) == 6
    e_t = utils.to_expr_t("exp(-t) + sin(t)")
    assert e_t.subs({t:0}) == 1

def test_pretty_and_numeric():
    M = sp.Matrix([[1,2],[3,4]])
    s = utils.pretty_matrix(M)
    assert "⎡" in s or "[" in s
    arr = utils.to_numeric(M, digits=6)
    assert arr.shape == (2,2) and float(arr[0,0]) == 1.0

def test_square_free():
    s = utils.sym_s()
    p1 = sp.Poly((s+1)*(s+2), s)
    p2 = sp.Poly((s+1)**2, s)
    assert utils.is_square_free(p1) is True
    assert utils.is_square_free(p2) is False
