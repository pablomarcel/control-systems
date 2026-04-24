
from __future__ import annotations
import control as ct
from pid_controllers.zeroPoleTool.design import Designer

def test_designer_branch_paths_kc_nonpos_unstable_and_metricfail():
    # Plant: 1/(s^2+2s+1) -> B has degree 2
    Gp = ct.tf([1.0],[1.0,2.0,1.0])
    # Deliberately include tuples that cause: 
    # - Kc <= 0 (a,c small) 
    # - unstable roots (a=b=c=0) 
    # - metric failure (overshoot/time won't meet)
    a_grid = [0.0, 0.1, 2.0]
    b_grid = [0.0, 2.0]
    c_grid = [0.0, 0.1, 1.0]
    d = Designer(arch="fig8-31")
    best, oks, closest, counts = d.search(Gp, a_grid, b_grid, c_grid,
                                          os_min=0, os_max=1, ts_max=0.01, settle_tol=0.02,
                                          dist_peak_weight=0.0, show_progress=False, debug=False)
    # No OK designs expected
    assert best is None
    assert isinstance(closest, list) and len(closest) >= 1
    # We should have seen some kcnonpos and unstable increments
    assert counts["kcnonpos"] >= 1
    assert counts["unstable"] >= 1
    assert counts["metric_fails"] >= 1
