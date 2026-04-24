
from __future__ import annotations
import os
import numpy as np
import control as ct
import matplotlib
matplotlib.use("Agg", force=True)  # make sure no window pops

from frequency_response.bodeTool.core import Analyzer, TFBuilder, FrequencyGrid
from frequency_response.bodeTool.design import BodePlotter, ClassicalPlotters

def test_bode_plotter_matplotlib_and_plotly(tmp_path, monkeypatch):
    tfb = TFBuilder()
    G = tfb.build_from_modes(num="1", den="1, 0.8, 1", gain=None, zeros=None, poles=None, fnum=None, fden=None, K=1.0)
    fg = FrequencyGrid(); w = fg.make(G, None, None, 256)
    az = Analyzer(); m = az.compute_margins(G, w)

    bp = BodePlotter(az)
    # Matplotlib path save (Agg backend)
    fig = bp.matplotlib(G, w, m, "Test", str(tmp_path/"bode.png"))
    assert (tmp_path/"bode.png").exists()

    # Plotly HTML save (no need to display in test)
    fig2 = bp.plotly(G, w, m, "Test", str(tmp_path/"bode.html"))
    assert (tmp_path/"bode.html").exists()

def test_classical_plotters(tmp_path):
    tfb = TFBuilder()
    G = tfb.build_from_modes(num="1", den="1, 0.8, 1", gain=None, zeros=None, poles=None, fnum=None, fden=None, K=1.0)
    fg = FrequencyGrid(); w = fg.make(G, None, None, 256)
    cp = ClassicalPlotters()
    fig_n = cp.nyquist_matplotlib(G, w, str(tmp_path/"nyquist.png"))
    assert (tmp_path/"nyquist.png").exists()
    fig_h = cp.nichols_matplotlib(G, w, str(tmp_path/"nichols.png"))
    assert (tmp_path/"nichols.png").exists()
