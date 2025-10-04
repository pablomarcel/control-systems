
from stateSpaceAnalysis.stateSolnTool.apis import SolveRequest, SolveResponse

def test_dataclasses_defaults_and_init():
    req = SolveRequest()
    assert req.canonical == "controllable" and req.u == "1"
    resp = SolveResponse(A="A", B="B", Phi="P", x_hom="xh", x_part="xp", x="x")
    assert resp.A == "A" and resp.x == "x"
