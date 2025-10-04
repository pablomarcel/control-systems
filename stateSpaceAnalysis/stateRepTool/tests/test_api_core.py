from stateSpaceAnalysis.stateRepTool.apis import StateRepAPIRequest, StateRepService
from stateSpaceAnalysis.stateRepTool.core import CanonicalFormCalculator, TransferFunctionSpec
import sympy as sp

def test_api_builds_and_runs():
    req = StateRepAPIRequest(example="ogata_9_1", which="controllable")
    resp = StateRepService.run(req)
    assert "controllable" in resp.results
    A = resp.results["controllable"]["A"]
    assert isinstance(A, list) and len(A) == 2

def test_core_verification_and_shapes():
    spec = TransferFunctionSpec.from_tf_string("(s+3)/(s^2+3*s+2)")
    calc = CanonicalFormCalculator(tf=spec)
    reals = calc.compute(which="all")
    cc = reals["controllable"]
    assert cc.A.shape == (2,2) and cc.B.shape == (2,1) and cc.C.shape == (1,2)
