# =============================
# File: transient_analysis/hurwitzTool/tests/test_numeric_check.py
# =============================
from __future__ import annotations
import sympy as sp
from pathlib import Path
from transient_analysis.hurwitzTool.apis import HurwitzService, NumericCheckRequest


def test_numeric_ok(tmp_path: Path):
    svc = HurwitzService(tmp_path)
    res = svc.numeric_check(NumericCheckRequest(coeffs="1, 5, 6, 7", subs={}, use_lienard=False))
    assert res.ok is True
    assert res.a_numeric[0] == 1.0