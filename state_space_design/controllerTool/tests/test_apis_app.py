# -*- coding: utf-8 -*-
import numpy as np
import control as ct
from state_space_design.controllerTool.apis import run, RunRequest
from state_space_design.controllerTool.app import ControllerToolApp, DesignInputs, BuildConfig

def test_apis_run_cfg1_only():
    rr = RunRequest(num="1", den="1 0 1 0",
                    K_poles="-1+1j,-1-1j,-8", obs_poles="-4,-4",
                    cfg="cfg1")
    resp = run(rr)
    assert resp.result.T1 is not None
    assert resp.result.T2 is None

def test_app_build_cfg2_only():
    din = DesignInputs(num=np.array([1.0]), den=np.array([1.0, 0.0, 1.0, 0.0]),
                       K_poles=np.array([-1+1j, -1-1j, -8], complex),
                       obs_poles=np.array([-4, -4], complex))
    app = ControllerToolApp(din, BuildConfig(cfg="cfg2"))
    res = app.build()
    assert res.T1 is None
    assert res.T2 is not None
    # Gc should be proper TF
    assert len(res.Gc.num[0][0]) > 0 and len(res.Gc.den[0][0]) > 0
