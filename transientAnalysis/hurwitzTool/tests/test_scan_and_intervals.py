# =============================
# File: transientAnalysis/hurwitzTool/tests/test_scan_and_intervals.py
# =============================
from __future__ import annotations
from pathlib import Path
from transientAnalysis.hurwitzTool.apis import HurwitzService, SymbolicRegionRequest, Scan1DRequest, Scan2DRequest


def test_symbolic_region_and_intervals(tmp_path: Path):
    svc = HurwitzService(tmp_path)
    r = svc.symbolic_region(SymbolicRegionRequest(coeffs="1, 5, 6, K", symbols="K", solvefor="K", use_lienard=False, intervals_pretty=True))
    assert "K" in r.variables
    assert r.region
    assert r.pretty is None or isinstance(r.pretty, str)


def test_scan1d(tmp_path: Path):
    svc = HurwitzService(tmp_path)
    s1 = svc.scan1d(Scan1DRequest(coeffs="1, 5, 6, K", symbol="K", lo=-5, hi=5, step=1.0))
    assert len(s1.samples) == 11


def test_scan2d(tmp_path: Path):
    svc = HurwitzService(tmp_path)
    s2 = svc.scan2d(Scan2DRequest(coeffs="1, 2, 4+K, 9, 25", sx="K", sy="alpha", xlo=0, xhi=1, dx=0.5, ylo=-1, yhi=1, dy=1.0))
    assert s2.Z.shape == (3, 3)