
from __future__ import annotations
import sympy as sp
from state_space_analysis.stateTransTool.core import StateTransitionEngine
import pytest

def test_parse_inputs_paths_and_phi_inverse():
    eng = StateTransitionEngine("controllable")
    # example path
    num, den = eng.parse_inputs(tf=None, num=None, den=None, example="ogata_9_1")
    A = eng.build_A(num, den)
    t = sp.Symbol('t', real=True)
    Phi = eng.phi_symbolic(A)
    Phi_inv = eng.phi_inverse_symbolic(A)
    # Check Φ(t)*Φ(-t) == I
    I = sp.eye(A.shape[0])
    assert sp.simplify(Phi * Phi_inv - I) == sp.zeros(*A.shape)

def test_parse_inputs_errors():
    eng = StateTransitionEngine("controllable")
    with pytest.raises(ValueError):
        eng.parse_inputs(tf=None, num=None, den=None, example=None)
    # Improper TF should raise
    with pytest.raises(ValueError):
        eng.parse_inputs(tf=None, num="1,0,1", den="1,0", example=None)
