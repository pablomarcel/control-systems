
import types
from pid_controllers.pidTool.design import make_grid, make_grids

class Args(types.SimpleNamespace):
    pass

def test_make_grid_vals():
    out = make_grid([1,3,2], None, None)
    assert out == [1,2,3]

def test_make_grids_pid():
    a = Args(structure="pid",
             Kp_vals=None, Ki_vals=None, Kd_vals=None,
             Kp_range=[0.5, 1.0], Ki_range=[0.1, 0.2], Kd_range=[0.0, 0.1],
             Kp_n=3, Ki_n=3, Kd_n=3,
             pi_Kp_vals=None, pi_Ki_vals=None, pi_Kp_range=None, pi_Ki_range=None, pi_Kp_n=None, pi_Ki_n=None,
             pd_Kp_vals=None, pd_Kd_vals=None, pd_Kp_range=None, pd_Kd_range=None, pd_Kp_n=None, pd_Kd_n=None,
             K_vals=None, a_vals=None, K_range=None, a_range=None, K_n=None, a_n=None)
    grids = make_grids(a)
    assert set(grids.keys()) == {"Kp","Ki","Kd"}
    assert len(grids["Kp"]) == 3 and grids["Kp"][0] == 0.5 and grids["Kp"][-1] == 1.0
