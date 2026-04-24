
from __future__ import annotations
import json
from pathlib import Path
from state_space_analysis.stateTool.app import StateToolApp
from state_space_analysis.stateTool.apis import RunOptions, AnalyzerMode

def test_app_run_from_state_and_export():
    app = StateToolApp()
    out_file = "app_state_summary.json"
    opts = RunOptions(mode=AnalyzerMode.ALL, export_json=out_file, digits=6)
    res = app.run_from_state(A="0 1; -2 -3", B="0;1", C="3 1", D="0", options=opts)
    assert "results" in res
    p = Path("state_space_analysis/stateTool/out") / out_file
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["mode"] == "all"

def test_app_run_from_tf():
    app = StateToolApp()
    opts = RunOptions(mode=AnalyzerMode.OBSSPLANE)
    res = app.run_from_tf(tf="(s+3)/(s^2+3*s+2)", num=None, den=None, options=opts)
    assert "obssplane" in res["results"]
