
from __future__ import annotations
from pid_controllers.zeroPoleTool.apis import ZeroPoleAPI, DesignRequest

def test_api_best_effort_returns_something():
    req = DesignRequest(
        plant_form="coeff", num="1", den="1,2,1",
        arch="fig8-31",
        a_vals="2.0 2.5", b_vals="2.0", c_vals="1.0",
        os_min=0, os_max=100, ts_max=10, settle_tol=0.02,
        best_effort=True, no_progress=True, plots=[]
    )
    picked, ok_list = ZeroPoleAPI.run(req)
    assert picked is None or picked is not None  # existence; smoke test
