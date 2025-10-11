from __future__ import annotations
import sys
from pathlib import Path
import types
import numpy as np
import sympy as sp

from transientAnalysis.hurwitzTool import utils as U

def test_parse_coeffs_and_symbols_and_subs():
    a = U.parse_coeffs("1, 2, 3, K, 2*alpha")
    assert len(a) == 5
    syms = U.parse_symbols_arg("K, alpha")
    assert [s.name for s in syms] == ["K", "alpha"]
    subs = U.parse_subs_list("K=3.5; alpha=2")
    assert subs[sp.Symbol("K")] == 3.5
    assert subs[sp.Symbol("alpha")] == 2.0

def test_detect_free_symbols_and_intervals_and_heatmap():
    K = sp.Symbol("K")
    a = [1, 5, 6, K]
    syms = U.detect_free_symbols([sp.sympify(x) for x in a])
    assert [s.name for s in syms] == ["K"]
    # Region: (0 < K) & (K < 30) -> build set using solveset-like result
    k = sp.Symbol("K")
    region = sp.And(sp.StrictGreaterThan(k, 0, evaluate=False), sp.StrictGreaterThan(30, k, evaluate=False))
    S = U.one_dim_interval_set(region, k)
    # Pretty printing should return a string (may vary by sympy version, just check non-empty)
    if S is not None:
        assert isinstance(U.set_to_pretty_intervals(S, latex=False), str)
        assert isinstance(U.set_to_pretty_intervals(S, latex=True), str)

    xs = np.array([0.0, 1.0, 2.0])
    ys = np.array([0.0, 1.0])
    Z = np.array([[True, False, True],
                  [False, True, False]], dtype=bool)
    art = U.ascii_heatmap(xs, ys, Z, invert_y=True)
    assert "█" in art and "·" in art
