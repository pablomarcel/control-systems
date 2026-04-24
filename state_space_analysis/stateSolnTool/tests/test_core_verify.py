
# tests/test_core_verify.py
from __future__ import annotations
import sympy as sp
from state_space_analysis.stateSolnTool.core import StateSolnEngine

def test_engine_solve_and_verify():
    eng = StateSolnEngine(canonical="controllable")
    res = eng.run(example="ogata_9_1", u="1", pretty=False, verify=True)
    assert "PASS" in (res["verification"] or "")
    # spot-check that x(t) string contains expected symbols
    assert "t" in res["x"]
