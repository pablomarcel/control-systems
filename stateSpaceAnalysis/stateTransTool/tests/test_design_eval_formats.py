
from __future__ import annotations
from stateSpaceAnalysis.stateTransTool.apis import StateTransRequest
from stateSpaceAnalysis.stateTransTool.app import run as run_app

def test_eval_numeric_and_pretty_paths(tmp_path):
    # numeric + eval
    r1 = StateTransRequest(example="ogata_9_1", eval_time=1.0, numeric=True)
    out1 = run_app(r1)
    assert "Φ(1.0)" in out1 or "Phi(1.0)" in out1
    # pretty symbolic path (no eval)
    r2 = StateTransRequest(example="ogata_9_1", pretty=True, inverse=True)
    out2 = run_app(r2)
    assert "Φ(t)" in out2 or "Phi(t)" in out2
    assert "Φ^(-1)(t)" in out2 or "Phi" in out2
