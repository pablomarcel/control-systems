import pytest
from state_space_design.robustTool.apis import RunRequest
from state_space_design.robustTool.app import RobustApp

def test_basic_run_no_plots():
    req = RunRequest(
        num="10 20", den="1 10 24 0",
        pid="2,5,0.1,20",
        Wm_num="0.2 1", Wm_den="0.02 1",
        Ws_num="0.5 0", Ws_den="1 0.05 0",
        plots="none",
        step=False,
        npts=64
    )
    res = RobustApp().run(req)
    # We should at least have metrics keys
    assert "WmT" in res.metrics or "WsS" in res.metrics
