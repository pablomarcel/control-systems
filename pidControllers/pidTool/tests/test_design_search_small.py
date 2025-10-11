import control as ct
from pidControllers.pidTool.design import search_candidates
from pidControllers.pidTool.core import Requirements

def test_search_candidates_small():
    s = ct.TransferFunction.s
    Gp = 1/(s+1)
    grids = {"K":[1.0, 2.0], "a":[0.5, 1.0]}
    req = Requirements(max_overshoot=100.0, max_settling=10.0, settle_tol=0.02)
    cands = search_candidates(Gp, "pid_dz", grids, req,
                              tfinal=5.0, dt=0.01,
                              objective="itae", wts=(1,1,1,0))
    assert len(cands) >= 1
