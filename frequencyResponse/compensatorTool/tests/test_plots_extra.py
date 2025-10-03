
from __future__ import annotations
import os
os.environ.setdefault("MPLBACKEND","Agg")

import numpy as np
import control as ct
import matplotlib
matplotlib.use("Agg")

# Import after setting backend
from frequencyResponse.compensatorTool import plots as P
from frequencyResponse.compensatorTool.core import get_margins

def test_bode_nyquist_nichols_mpl(tmp_path):
    w = np.logspace(-2, 2, 128)
    G = ct.tf([1.0], [1.0, 1.0])
    fig1 = P.plot_bode_mpl([("G", G)], w, "Bode")
    fig2 = P.plot_nyquist_mpl([("G", G)], w, "Nyquist", ogata_axes=True, Mlist=[1.2], freq_marks=[0.2, 1.0])
    fig3 = P.plot_nichols_mpl([("G", G)], w, "Nichols", templates=P.build_nichols_templates([-12,0,6], [-60,-120]))
    for i, fig in enumerate([fig1, fig2, fig3], start=1):
        p = tmp_path / f"fig{i}.png"
        fig.savefig(p)
        assert p.exists()

def test_step_and_ramp_mpl(tmp_path):
    w = np.logspace(-2, 2, 128)
    G = ct.tf([1.0], [1.0, 1.0])
    Gcl = ct.feedback(G,1)
    # show_unstable=False path
    fig_s = P.plot_step_mpl(G, G, w, ogata_axes=False, show_unstable=False)
    fig_r = P.plot_ramp_mpl(G, G, w, ogata_axes=True, show_unstable=True)
    fig_s.savefig(tmp_path/"step.png"); fig_r.savefig(tmp_path/"ramp.png")
    assert (tmp_path/"step.png").exists()
    assert (tmp_path/"ramp.png").exists()
