
from __future__ import annotations
from pathlib import Path
import json
import sympy as sp
from state_space_analysis.stateTransTool.apis import StateTransRequest
from state_space_analysis.stateTransTool.app import run as run_app

def test_app_report_and_export_json(tmp_path):
    out_json = tmp_path / "phi.json"
    req = StateTransRequest(example="ogata_9_1", canonical="controllable",
                            eval_time=1.0, numeric=True, pretty=False,
                            inverse=True, export_json=str(out_json))
    report = run_app(req)
    assert "State-Transition Matrix" in report
    assert out_json.exists()
    data = json.loads(out_json.read_text())
    assert "Phi(t)" in data and "Phi_inv(t)" in data
