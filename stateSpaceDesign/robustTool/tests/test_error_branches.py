import pytest
from stateSpaceDesign.robustTool.apis import RunRequest
from stateSpaceDesign.robustTool.app import RobustApp
import stateSpaceDesign.robustTool.core as core

def test_hinf_error_path(monkeypatch):
    # Force FrequencyTools.hinf_sweep to raise, ensuring metrics record error
    monkeypatch.setattr(core.FrequencyTools, "hinf_sweep", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    req = RunRequest(
        num="10 20", den="1 10 24 0",
        pid="1,2,0.1,10",
        Wm_num="0.2 1", Wm_den="0.02 1",
        plots="none", npts=8
    )
    res = RobustApp().run(req)
    assert "WmT" in res.metrics and res.metrics["WmT"].error
