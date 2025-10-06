import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from stateSpaceDesign.robustTool.tools.plot import Plotter

def test_plotter_bode_and_step(monkeypatch):
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)
    monkeypatch.setattr(go.Figure, "show", lambda self, *a, **k: None)

    w = np.logspace(-2, 2, 10)
    curves = [
        ("A", {"mag": np.zeros_like(w), "phs": np.zeros_like(w)}),
        ("B", {"mag": np.ones_like(w), "phs": np.ones_like(w)}),
    ]
    Plotter.bode_mpl(w, curves, title="X")
    Plotter.bode_plotly(w, curves, title="X")

    t = np.linspace(0,1,11)
    y = np.sin(t); u = np.cos(t)
    Plotter.step_mpl(t,y,u)
    Plotter.step_plotly(t,y,u)
