import json, numpy as np, os, tempfile
from stateSpaceDesign.lqrTool.apis import LQRRunRequest
from stateSpaceDesign.lqrTool.app import LQRApp

def test_app_run_abcd_with_step_and_x0(tmp_path):
    rr = LQRRunRequest(
        A="0 1 0; 0 0 1; 0 -2 -3",
        B="0; 0; 1",
        C="1 0 0",
        Q="diag:100,1,1", R="0.01",
        x0="0 0 1",
        step=True, prefilter="dcgain",
        tfinal=1.0, dt=0.05, plots="none"
    )
    app = LQRApp(rr)
    res = app.run()
    assert res.prefilter_gain is not None
    assert len(res.K) > 0

def test_app_run_tf_path_no_step():
    rr = LQRRunRequest(num="1", den="1,1", plots="none", tfinal=0.5, dt=0.1)
    res = LQRApp(rr).run()
    assert len(res.K) > 0
