from __future__ import annotations
from state_space_analysis.converterTool.app import ConverterApp
from state_space_analysis.converterTool.apis import RunRequest

def test_app_detect_modes_and_run_no_plot():
    app = ConverterApp()
    # TF only
    req_tf = RunRequest(num="1,0", den="1,1,1", no_plot=True)
    assert app.detect_mode(req_tf) == "tf"
    assert app.run(req_tf).ok
    # SS only
    req_ss = RunRequest(A="0 1; -1 -1", B="0; 1", C="1 0", D="0", no_plot=True)
    assert app.detect_mode(req_ss) == "ss"
    assert app.run(req_ss).ok
    # Both
    req_both = RunRequest(num="1,0", den="1,1,1", A="0 1; -1 -1", B="0; 1", C="1 0", D="0", no_plot=True)
    assert app.detect_mode(req_both) == "both"
    assert app.run(req_both).ok

def test_app_with_plot_saves(tmp_path, monkeypatch):
    app = ConverterApp()
    # write plots under out/ with prefix
    req = RunRequest(num="1,0", den="1,1,1", out_prefix="unittest", no_plot=False, tfinal=0.1, dt=0.05)
    res = app.run(req)
    assert res.ok
