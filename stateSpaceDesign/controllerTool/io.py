# -*- coding: utf-8 -*-
"""
Output/plot services (Matplotlib/Plotly optional) for closed-loop responses.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple
import numpy as np
import control as ct

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLY = True
except Exception:
    HAS_PLY = False

from .utils import bode_data

@dataclass
class PlotConfig:
    plots: str = "both"  # "none", "mpl", "plotly", "both"
    save_prefix: Optional[str] = None
    ply_width: int = 0  # 0 => responsive

class PlotService:
    def __init__(self, cfg: PlotConfig):
        self.cfg = cfg

    def plot_closed_loop_bode_and_step(self, systems: Sequence[tuple[str, ct.TransferFunction]]):
        if not systems:
            return
        want_mpl = self.cfg.plots in ("mpl", "both") and HAS_MPL
        want_ply = self.cfg.plots in ("plotly", "both") and HAS_PLY

        w = np.logspace(-2, 2, 1200)
        mags, phs, labels = [], [], []
        for label, T in systems:
            mag, ph = bode_data(T, w)
            mags.append(mag); phs.append(ph); labels.append(label)

        if want_mpl:
            fig, (axm, axp) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
            for k, lab in enumerate(labels):
                axm.semilogx(w, mags[k], lw=2, label=lab)
                axp.semilogx(w, phs[k],  lw=2, label=lab)
            axm.set_ylabel("|T| (dB)"); axp.set_ylabel("∠T (deg)"); axp.set_xlabel("rad/s")
            axm.grid(True, ls=":", lw=0.6); axp.grid(True, ls=":", lw=0.6)
            axm.set_title("Closed-loop Bode"); axm.legend()
            fig.tight_layout()
            if self.cfg.save_prefix:
                fig.savefig(f"{self.cfg.save_prefix}_bode_closed_mpl.png", dpi=140)
            else:
                plt.show()

            fig2, ax2 = plt.subplots(figsize=(9, 4))
            for label, T in systems:
                t, y = ct.step_response(T)
                ax2.plot(t, y, label=label)
            ax2.grid(True, ls=":", lw=0.6); ax2.set_xlabel("t (sec)"); ax2.set_ylabel("y(t)")
            ax2.set_title("Closed-loop Step"); ax2.legend(); fig2.tight_layout()
            if self.cfg.save_prefix:
                fig2.savefig(f"{self.cfg.save_prefix}_step_closed_mpl.png", dpi=140)
            else:
                plt.show()

        if want_ply:
            width = None if self.cfg.ply_width <= 0 else self.cfg.ply_width
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                                subplot_titles=("Closed loop magnitude |T| (dB)", "Closed loop phase ∠T (deg)"))
            for k, lab in enumerate(labels):
                fig.add_trace(go.Scatter(x=w, y=mags[k], mode="lines", name=lab,
                                         legendgroup=lab, showlegend=True), row=1, col=1)
                fig.add_trace(go.Scatter(x=w, y=phs[k],  mode="lines", name=lab,
                                         legendgroup=lab, showlegend=False), row=2, col=1)
            fig.update_xaxes(type="log", showgrid=True, gridcolor="#e5e9f0", dtick=1, row=1, col=1, matches='x')
            fig.update_xaxes(type="log", showgrid=True, gridcolor="#e5e9f0", dtick=1, row=2, col=1, matches='x',
                             title_text="rad/s")
            fig.update_yaxes(title="dB",   showgrid=True, gridcolor="#e5e9f0", row=1, col=1)
            fig.update_yaxes(title="deg",  showgrid=True, gridcolor="#e5e9f0", row=2, col=1)
            fig.update_layout(autosize=(width is None), width=width, height=720,
                              legend=dict(orientation="h"), margin=dict(l=60, r=30, t=70, b=50))
            if self.cfg.save_prefix:
                fig.write_html(f"{self.cfg.save_prefix}_bode_closed_plotly.html")
            fig.show(config={"responsive": True})

            fig2 = go.Figure()
            for label, T in systems:
                t, y = ct.step_response(T)
                fig2.add_trace(go.Scatter(x=t, y=y, mode="lines", name=label))
            fig2.update_xaxes(title="t (sec)", showgrid=True, gridcolor="#e5e9f0")
            fig2.update_yaxes(title="y(t)", showgrid=True, gridcolor="#e5e9f0")
            fig2.update_layout(title="Closed-loop Step", autosize=(width is None), width=width, height=420,
                               legend=dict(orientation="h"), margin=dict(l=60, r=30, t=60, b=50))
            if self.cfg.save_prefix:
                fig2.write_html(f"{self.cfg.save_prefix}_step_closed_plotly.html")
            fig2.show(config={"responsive": True})
