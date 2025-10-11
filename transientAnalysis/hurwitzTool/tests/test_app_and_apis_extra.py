from __future__ import annotations
from pathlib import Path
import sympy as sp

from transientAnalysis.hurwitzTool.app import HurwitzApp
from transientAnalysis.hurwitzTool.apis import (
    HurwitzService, NumericCheckRequest, SymbolicRegionRequest, Scan1DRequest
)

def test_app_helpers_and_pretty(tmp_path: Path):
    app = HurwitzApp(tmp_path)
    p = app.polynomial_from_str("1, 5, 6, K")
    syms = app.detect_symbols(p.a_desc, "K", "K")
    assert [s.name for s in syms] == ["K"]
    ineqs, used = app.inequalities(p, use_lienard=False)
    region = app.reduce_region(ineqs, syms)
    pretty = app.pretty_intervals_1d(region, syms[0])
    assert used.startswith("Full Hurwitz")
    # pretty can be None if SymPy returns complex boolean forms; check type if present
    if pretty:
        pr, La = pretty
        assert isinstance(pr, str) and isinstance(La, str)

def test_apis_end_to_end(tmp_path: Path):
    svc = HurwitzService(tmp_path)
    # numeric
    res = svc.numeric_check(NumericCheckRequest(coeffs="1,5,6,7", subs={}))
    assert "Hurwitz" in res.used and isinstance(res.ok, bool)
    # symbolic
    sres = svc.symbolic_region(SymbolicRegionRequest(coeffs="1,5,6,K", symbols="K", solvefor="K", intervals_pretty=True))
    assert "Used:" not in sres.region  # just ensure it's a stringified sympy expr
    # scan1d
    scan = svc.scan1d(Scan1DRequest(coeffs="1,5,6,K", symbol="K", lo=-1, hi=1, step=1.0))
    assert len(scan.samples) >= 2
