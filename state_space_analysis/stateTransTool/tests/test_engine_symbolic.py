# state_space_analysis/stateTransTool/tests/test_engine_symbolic.py
from __future__ import annotations
import sympy as sp
from state_space_analysis.stateTransTool.core import StateTransitionEngine

def test_diagonal_ogata_9_1_phi():
    eng = StateTransitionEngine(canonical="diagonal")
    num, den = eng.parse_inputs(tf=None, num=None, den=None, example="ogata_9_1")
    A = eng.build_A(num, den)
    t = sp.Symbol('t', real=True)
    Phi = eng.phi_symbolic(A)
    # Poles are -1 and -2 (order sorted by real part desc)
    expected = sp.diag(sp.exp(-1*t), sp.exp(-2*t))
    assert sp.simplify(Phi - expected) == sp.zeros(2)
