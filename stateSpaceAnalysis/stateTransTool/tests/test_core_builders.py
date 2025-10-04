
from __future__ import annotations
import sympy as sp
from stateSpaceAnalysis.stateTransTool.core import (
    controllable_A, observable_A_from, diagonal_A_pf, StateTransitionEngine, get_canonical_names
)
from stateSpaceAnalysis.stateTransTool.utils import parse_tf_string

def test_controllable_observable_shapes_and_values():
    num, den = parse_tf_string("(s+3)/(s^2+3*s+2)")
    A = controllable_A(num, den)  # 2x2 companion
    assert A.shape == (2,2)
    # last row equals negatives of ascending den coeffs (excluding leading 1): [a0, a1] -> [-a0, -a1]
    # den = s^2 + 3 s + 2  -> a_asc = [2, 3]
    assert list(A[1,:]) == [ -2, -3 ]
    Ao = observable_A_from(A)
    assert Ao == A.T

def test_diagonal_pf_and_fallback_for_repeated():
    # simple poles
    _, den = parse_tf_string("1/(s^2+3*s+2)")
    Ad = diagonal_A_pf(den)
    t = sp.Symbol('t', real=True)
    assert Ad == sp.diag(-1, -2) or Ad == sp.diag(-2, -1)
    # repeated poles -> None
    _, den_rep = parse_tf_string("1/((s+1)^2)")
    assert diagonal_A_pf(den_rep) is None
    # engine diagonal canonical must not crash on repeated poles
    eng = StateTransitionEngine(canonical="diagonal")
    num_rep, den_rep2 = parse_tf_string("(s+0)/((s+1)^2)")
    A = eng.build_A(num_rep, den_rep2)
    assert A.shape == (2,2)

def test_registry_contains_expected():
    names = set(get_canonical_names())
    assert {"controllable","observable","diagonal","jordan"}.issubset(names)
