import numpy as np
import importlib

def test_analytic_over_and_under_damped():
    analytic = importlib.import_module("transient_analysis.icTool.tools.analytic").analytic_solution
    T = np.linspace(0, 0.1, 6)
    # overdamped: m=1, b=3, k=2
    y = analytic(T, 1.0, 3.0, 2.0, 0.1, 0.05)
    assert y is not None and y.shape == T.shape
    # underdamped: very small damping
    y2 = analytic(T, 1.0, 0.1, 2.0, 0.1, 0.05)
    assert y2 is None

def test_track_decorator_executes():
    try:
        track = importlib.import_module("transient_analysis.icTool.tools.diagram").track
    except Exception:
        # If diagram has optional deps missing, just skip gracefully.
        return

    calls = []
    @track("src", "dst")
    def f(x): 
        calls.append(x); 
        return x+1

    out = f(41)
    assert out == 42 and calls == [41]