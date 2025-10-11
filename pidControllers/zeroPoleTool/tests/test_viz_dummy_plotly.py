
from __future__ import annotations
import sys, types
import control as ct
from pathlib import Path
from pidControllers.zeroPoleTool.design import Designer
from pidControllers.zeroPoleTool.viz import step_reference, step_disturbance, ramp_reference, accel_reference
import pidControllers.zeroPoleTool.viz as viz

def _build_good_candidate():
    Gp = ct.tf([1.0],[1.0,2.0,1.0])
    d = Designer(arch="fig8-31")
    best, ok_list, _, _ = d.search(Gp, [2.0],[2.0],[1.0], os_min=0, os_max=100, ts_max=10.0, settle_tol=0.02, show_progress=False)
    assert best is not None
    return best

class DummyFig:
    def __init__(self): self.traces = []
    def add_trace(self, *a, **k): self.traces.append((a,k))
    def update_layout(self, *a, **k): pass
    def write_html(self, path, **k): 
        Path(path).write_text("<html>ok</html>", encoding="utf-8")

class DummyScatter:
    def __init__(self, **kwargs): self.kw = kwargs

def test_viz_with_dummy_plotly(monkeypatch):
    # Build a minimal fake 'plotly' package so any 'import plotly.graph_objects as go'
    # resolves to our stub instead of the real library.
    fake_plotly = types.ModuleType("plotly")
    fake_go = types.ModuleType("plotly.graph_objects")
    fake_go.Figure = DummyFig
    fake_go.Scatter = DummyScatter
    # Register both
    sys.modules['plotly'] = fake_plotly
    sys.modules['plotly.graph_objects'] = fake_go

    # Also set the top-level flag in viz so step_reference path uses our existing viz.go if needed
    viz.PLOTLY_OK = True
    viz.go = fake_go

    cand = _build_good_candidate()
    step_reference("cov_viz", cand)
    step_disturbance("cov_viz", cand)
    ramp_reference("cov_viz", cand)
    accel_reference("cov_viz", cand)
