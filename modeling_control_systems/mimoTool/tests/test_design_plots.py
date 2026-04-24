
from __future__ import annotations
import numpy as np
from modeling_control_systems.mimoTool.design import MIMOPlotter, PlotConfig
from modeling_control_systems.mimoTool.core import StepOut, SigmaOut

def test_plot_steps_and_sigma_no_show():
    T = np.linspace(0,1,5)
    Y = np.vstack([T, T**2])
    steps = (StepOut(T=T, Y=Y),)
    MIMOPlotter.steps_per_input(steps, PlotConfig(title_prefix="Test", show=False))

    w = np.logspace(-2, 2, 10)
    sv = np.vstack([np.ones_like(w), 0.1*np.ones_like(w)])
    sout = SigmaOut(w=w, sv=sv)
    MIMOPlotter.sigma(sout, PlotConfig(sigma_title="Test σ", show=False))
