
from __future__ import annotations
from stateSpaceAnalysis.stateTransTool.apis import StateTransRequest, StateTransResult
import sympy as sp

def test_request_dataclass_defaults_and_override():
    req = StateTransRequest(example="ogata_9_1", canonical="observable", eval_time=0.5, numeric=True, pretty=True)
    assert req.canonical == "observable"
    assert req.eval_time == 0.5
    assert req.numeric is True
    assert req.pretty is True

def test_result_dataclass_instantiation():
    A = sp.eye(2)
    res = StateTransResult(A=A, canonical="controllable", Phi=A)
    assert res.A.shape == (2,2)
    assert res.canonical == "controllable"
