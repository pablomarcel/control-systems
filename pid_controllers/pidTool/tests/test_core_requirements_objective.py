from pid_controllers.pidTool.core import Metrics, Requirements, meets_requirements, objective_value

def test_meets_requirements_true_false():
    m = Metrics(overshoot=5, settling_time=2, rise_time=1, ess=0, itae=3, ise=4, tfinal_used=5)
    r_ok = Requirements(max_overshoot=10, max_settling=3, max_rise=2, max_ess=0.1)
    r_bad = Requirements(max_overshoot=1, max_settling=1, max_rise=0.5, max_ess=1e-6)
    assert meets_requirements(m, r_ok) is True
    assert meets_requirements(m, r_bad) is False

def test_objective_variants_and_default():
    m = Metrics(overshoot=5, settling_time=2, rise_time=1, ess=0, itae=3, ise=4, tfinal_used=5)
    assert objective_value(m, "ts") == 2
    assert objective_value(m, "mp") == 5
    assert objective_value(m, "itae") == 3
    assert objective_value(m, "ise") == 4
    val = objective_value(m, "weighted", 1,2,3,4)
    assert isinstance(float(val), float)  # ensure numeric
    # Unknown maps to itae (default branch)
    assert objective_value(m, "unknownzzz") == 3
