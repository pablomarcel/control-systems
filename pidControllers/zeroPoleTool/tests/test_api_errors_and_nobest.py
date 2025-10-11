
from __future__ import annotations
import pytest
import control as ct
from pidControllers.zeroPoleTool.apis import ZeroPoleAPI, DesignRequest

def test_api_build_gp_missing_params_errors():
    with pytest.raises(ValueError):
        ZeroPoleAPI.build_gp(DesignRequest(plant_form="coeff", num=None, den=None))
    with pytest.raises(ValueError):
        ZeroPoleAPI.build_gp(DesignRequest(plant_form="poly", num_poly=None, den_poly=None))
    # zpk path: utils returns [] for None; API defaults gain to 1.0 — should succeed.
    tf = ZeroPoleAPI.build_gp(DesignRequest(plant_form="zpk", zeros=None, poles=None, gain=None))
    assert isinstance(tf, ct.TransferFunction)

def test_api_run_no_best_effort_returns_none_and_prints(capsys):
    # Choose plant and grids that won't meet specs and no best_effort
    req = DesignRequest(
        plant_form="coeff", num="1", den="1,2,1",
        a_vals="0 0", b_vals="0", c_vals="0",
        os_min=0, os_max=1, ts_max=0.01,  # impossible
        plots=[], export_json=False, export_csv=False, best_effort=False,
    )
    best, ok_list = ZeroPoleAPI.run(req)
    cap = capsys.readouterr().out
    assert best is None
    assert ok_list == []
    assert "[RESULT] No candidate satisfied" in cap
