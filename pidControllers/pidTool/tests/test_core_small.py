
from pidControllers.pidTool.core import Metrics, objective_value, margins_report

def test_objective_branches():
    m = Metrics(overshoot=5, settling_time=2, rise_time=1, ess=0, itae=3, ise=4, tfinal_used=5)
    assert objective_value(m, "ts") == 2
    assert objective_value(m, "mp") == 5
    assert objective_value(m, "itae") == 3
    assert objective_value(m, "ise") == 4
    val = objective_value(m, "weighted", 1,2,3,4)
    # For these weights: 1*Ts + 2*OS + 3*ITAE + 4*ISE = 1*2 + 2*5 + 3*3 + 4*4 = 37
    assert abs(val - 37) < 1e-12

def test_margins_report_string_smoke():
    class Dummy: pass
    s = margins_report(Dummy())  # should not raise
    assert "Gain margin" in s and "Phase margin" in s
