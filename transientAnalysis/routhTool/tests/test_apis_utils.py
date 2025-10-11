
from __future__ import annotations
import importlib.util

from transientAnalysis.routhTool.apis import RouthRequest, array_api, solve_api
from transientAnalysis.routhTool.utils import parse_coeffs, coerce_tokens, fmt_cell

_SYMPY_AVAILABLE = importlib.util.find_spec("sympy") is not None

def test_utils_parse_and_fmt():
    toks = parse_coeffs("1, 0, 2, 0, 1")
    assert toks == ["1","0","2","0","1"]
    # fmt numeric
    assert fmt_cell(3.14159).strip().startswith("3.1415")

def test_array_api_numeric():
    req = RouthRequest(coeffs="1, 5, 6, 2", verify_numeric=True)
    resp = array_api(req)
    assert resp.degrees == [3,2,1,0]
    assert isinstance(resp.rhp_by_routh, int)

def test_solve_api_symbolic():
    if not _SYMPY_AVAILABLE:
        return
    resp = solve_api("1, 5, 6, K", "K")
    assert resp.stability_condition  # some non-empty description

def test_coerce_tokens_symbolic_or_numeric():
    # Works both with and without sympy; if sympy present, K is a symbol
    toks = ["1","5","6","K"]
    vals = coerce_tokens(toks, ["K"])
    assert len(vals) == 4
