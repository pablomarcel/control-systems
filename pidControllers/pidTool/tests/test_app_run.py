
import pytest
try:
    import control as ct
except Exception:
    ct = None

from pidControllers.pidTool.app import PIDDesignerApp
from pidControllers.pidTool.core import Requirements
from pidControllers.pidTool.design import make_grids
from types import SimpleNamespace

@pytest.mark.skipif(ct is None, reason="python-control not installed")
def test_app_run_small(tmp_path):
    app = PIDDesignerApp(out_dir=str(tmp_path))
    # small, very coarse PD problem to ensure it returns quickly
    args = SimpleNamespace(
        structure="pd",
        pd_Kp_vals=None, pd_Kd_vals=None,
        pd_Kp_range=[0.5,1.0], pd_Kd_range=[0.0,0.2],
        pd_Kp_n=2, pd_Kd_n=2,
        Kp_vals=None, Ki_vals=None, Kd_vals=None, Kp_range=None, Ki_range=None, Kd_range=None, Kp_n=None, Ki_n=None, Kd_n=None,
        pi_Kp_vals=None, pi_Ki_vals=None, pi_Kp_range=None, pi_Ki_range=None, pi_Kp_n=None, pi_Ki_n=None,
        K_vals=None, a_vals=None, K_range=None, a_range=None, K_n=None, a_n=None
    )
    Gp = ct.tf([1],[1,1,1])  # simple plant
    grids = make_grids(args)
    req = Requirements(max_overshoot=90.0, max_settling=10.0, settle_tol=0.05)
    n = app.run(Gp=Gp, structure="pd", req=req, grids=grids,
                objective="itae", weights=(1,0.1,1,0), tfinal=5.0, dt=0.01,
                backend="none", plot_top=2, save_prefix="run", export_json=False, export_csv=False)
    assert isinstance(n, int)
