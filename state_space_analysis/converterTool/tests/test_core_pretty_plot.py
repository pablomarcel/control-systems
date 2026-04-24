from __future__ import annotations
import numpy as np
import os
from state_space_analysis.converterTool.core import SystemConverter, PrettyPrinter, Plotter
from state_space_analysis.converterTool.io import default_out

def test_pretty_and_sympy_and_plots(tmp_path):
    conv = SystemConverter()
    num = [1, 0]
    den = [1, 14, 56, 160]
    res = conv.tf_to_ss(num, den)
    pp = PrettyPrinter()
    txt = pp.tf(res.G)
    assert "Transfer function" in txt
    # sympy pretty string should be printable (SymPy may not be installed; handle text result)
    s = pp.sympy_tf(res.G)
    assert isinstance(s, str)
    # Plot save files
    plotter = Plotter(backend="Agg")
    f1 = default_out("test_tf_plot.png")
    plotter.step_tf(res.G, tfinal=0.1, dt=0.05, save=f1, show=False)
    assert f1.exists()
    f2 = default_out("test_ss_plot.png")
    plotter.step_ss(res.SS, iu=0, tfinal=0.1, dt=0.05, save=f2, show=False)
    assert f2.exists()
