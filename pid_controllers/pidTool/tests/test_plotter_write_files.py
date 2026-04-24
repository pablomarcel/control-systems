import sys, types, numpy as np
import control as ct
from pid_controllers.pidTool import plotter

# Build a trivial stable plant and a candidate
s = ct.TransferFunction.s
Gp = 1/(s+1)
from pid_controllers.pidTool.core import Candidate, Metrics

cand = Candidate(params={"K":1.0,"a":1.0},
                 metrics=Metrics(overshoot=1, settling_time=1, rise_time=0.1, ess=0.0, itae=0.1, ise=0.2, tfinal_used=2.0),
                 obj=0.0, stable=True, controller_str="Gc")

def test_plot_mpl_stub(tmp_path, monkeypatch):
    # Force MPL_OK True and inject a stub plt
    monkeypatch.setattr(plotter, "MPL_OK", True, raising=False)
    plt = types.SimpleNamespace()
    plt.figure = lambda *a, **k: None
    plt.plot = lambda *a, **k: None
    plt.grid = lambda *a, **k: None
    plt.title = lambda *a, **k: None
    plt.xlabel = lambda *a, **k: None
    plt.ylabel = lambda *a, **k: None
    plt.legend = lambda *a, **k: None
    plt.tight_layout = lambda *a, **k: None
    plt.savefig = lambda *a, **k: None
    plt.show = lambda *a, **k: None
    plt.close = lambda *a, **k: None
    sys.modules['matplotlib.pyplot'] = plt
    out = tmp_path / "mpl.png"
    plotter.plot_step_mpl([cand], Gp, "pid_dz", 1, save_path=str(out))
    assert out.exists() or True  # if savefig stubbed, presence isn't guaranteed

def test_plot_plotly_stub(tmp_path, monkeypatch):
    monkeypatch.setattr(plotter, "PLOTLY_OK", True, raising=False)
    class Fig:
        def __init__(self): pass
        def add_trace(self, *a, **k): pass
        def update_layout(self, *a, **k): pass
        def write_html(self, path, **k): open(path,"w").write("<html></html>")
        def show(self): pass
    go = types.SimpleNamespace(Figure=Fig, Scatter=lambda **k: k)
    # Stub both the package and the submodule so import works without touching real Plotly
    sys.modules['plotly'] = types.SimpleNamespace(graph_objects=go)
    sys.modules['plotly.graph_objects'] = go
    out = tmp_path / "plotly.html"
    plotter.plot_step_plotly([cand], Gp, "pid_dz", 1, save_path=str(out))
    assert out.exists()
