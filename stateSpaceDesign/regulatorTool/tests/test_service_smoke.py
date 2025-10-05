import numpy as np
from stateSpaceDesign.regulatorTool.apis import RegulatorRunRequest, RegulatorService

def test_service_smoke_no_plots(tmp_path):
    req = RegulatorRunRequest(
        num=np.array([10.0, 20.0]), den=np.array([1.0, 10.0, 24.0, 0.0]),
        K_poles=None, obs_poles=None, ts=4.0, undershoot=(0.25, 0.35), obs_speed_factor=5.0,
        x0=np.array([1.0, 0.0, 0.0]), e0=np.array([1.0, 0.0]),
        t_final=1.0, dt=0.05, plots="none"
    )
    svc = RegulatorService(req)
    res = svc.run()
    assert "plant" in res and "design" in res and "sim" in res
    assert res["design"].Gc is not None
    assert res["sim"].X.shape[0] == 3
