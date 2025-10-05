#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py — app orchestration for regulatorTool (handles plotting choices).
"""

from __future__ import annotations
import logging
from typing import Optional, Tuple
import numpy as np

from .apis import RegulatorRunRequest, RegulatorService
from .design import RegulatorDesigner
from .utils import HAS_MPL, HAS_PLOTLY
from .io import out_path

def _maybe_plot(service: RegulatorService, show: bool = True, save_prefix: Optional[str] = None,
                rl_axes: Tuple[float, float, float, float] = (-14, 2, -8, 8), rl_k: str = "auto",
                backend: str = "both", ply_width: int = 0) -> None:
    res = service.designer.run()
    (mag_ol, ph_ol), (mag_cl, ph_cl), w_ol, w_cl = service.designer.bode_open_closed(res)
    rlist, kvals = service.designer.root_locus(res, rl_k)

    # Open/closed loop PZ for optional markers
    Lnum = np.squeeze(np.array(res.L.num[0][0], float))
    Lden = np.squeeze(np.array(res.L.den[0][0], float))
    poles_ol = np.roots(Lden)
    zeros_ol = np.roots(Lnum)

    rl_xmin, rl_xmax, rl_ymin, rl_ymax = rl_axes

    want_mpl = backend in ("mpl", "both") and HAS_MPL
    want_ply = backend in ("plotly", "both") and HAS_PLOTLY

    if want_mpl:
        import matplotlib.pyplot as plt  # local import
        # Bode — open loop
        fig2, (axm, axp) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
        axm.semilogx(w_ol, mag_ol); axp.semilogx(w_ol, ph_ol)
        axm.set_ylim(-100, 100); axp.set_ylim(-200, -50); axp.set_xlim(1e-3, 1e2)
        axm.set_ylabel("Magnitude (dB)"); axp.set_ylabel("Phase (deg)"); axp.set_xlabel("Frequency (rad/sec)")
        axm.set_title("Bode Diagram — Open Loop"); axm.grid(True, ls=":", lw=0.6); axp.grid(True, ls=":", lw=0.6)
        fig2.tight_layout()
        if save_prefix:
            fig2.savefig(out_path(f"{save_prefix}_bode_open.png"))
        if show:
            plt.show()

        # Bode — closed loop
        fig3, (axm2, axp2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
        axm2.semilogx(w_cl, mag_cl); axp2.semilogx(w_cl, ph_cl)
        axm2.set_ylim(-60, 20); axp2.set_ylim(-200, 0); axp2.set_xlim(1e-1, 1e2)
        axm2.set_ylabel("Magnitude (dB)"); axp2.set_ylabel("Phase (deg)"); axp2.set_xlabel("Frequency (rad/sec)")
        axm2.set_title("Bode Diagram — Closed Loop"); axm2.grid(True, ls=":", lw=0.6); axp2.grid(True, ls=":", lw=0.6)
        fig3.tight_layout()
        if save_prefix:
            fig3.savefig(out_path(f"{save_prefix}_bode_closed.png"))
        if show:
            plt.show()

        # Root locus
        fig4, ax4 = plt.subplots(figsize=(9, 7))
        colors = plt.rcParams['axes.prop_cycle'].by_key().get('color', None)
        for i in range(rlist.shape[0]):
            xi = np.real(rlist[i, :]); yi = np.imag(rlist[i, :])
            ax4.plot(xi, yi, lw=1.8, color=None if colors is None else colors[i % len(colors)], solid_capstyle='round')
        ax4.set_xlim(rl_xmin, rl_xmax); ax4.set_ylim(rl_ymin, rl_ymax)
        ax4.axhline(0, color='k', lw=0.6); ax4.axvline(0, color='k', lw=0.6)
        ax4.grid(True, ls=":", lw=0.6); ax4.set_aspect('equal', adjustable='box')
        ax4.set_title("Root Locus of L(s)=Gc(s)G(s) with scalar gain k")
        ax4.set_xlabel("Real"); ax4.set_ylabel("Imag")
        if save_prefix:
            fig4.savefig(out_path(f"{save_prefix}_root_locus.png"))
        if show:
            plt.show()

    if want_ply:
        from plotly.subplots import make_subplots
        import plotly.graph_objects as go
        width = None if ply_width <= 0 else ply_width

        # Bode OPEN
        fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                             subplot_titles=("Bode Diagram — Open Loop (Magnitude)",
                                             "Bode Diagram — Open Loop (Phase)"))
        fig2.add_trace(go.Scatter(x=w_ol, y=mag_ol, mode="lines", name="|L| (dB)"), row=1, col=1)
        fig2.add_trace(go.Scatter(x=w_ol, y=ph_ol,  mode="lines", name="∠L (deg)"), row=2, col=1)
        fig2.update_xaxes(type="log", range=[-3, 2], matches='x', row=1, col=1)
        fig2.update_xaxes(type="log", range=[-3, 2], matches='x', row=2, col=1, title_text="Frequency (rad/sec)")
        fig2.update_yaxes(title="Magnitude (dB)", range=[-100, 100], row=1, col=1)
        fig2.update_yaxes(title="Phase (deg)",     range=[-200, -50], row=2, col=1)
        if save_prefix:
            fig2.write_html(out_path(f"{save_prefix}_bode_open.html"), include_plotlyjs="cdn")
        if show:
            fig2.show(config={"responsive": True})

        # Bode CLOSED
        fig3 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                             subplot_titles=("Bode Diagram — Closed Loop (Magnitude)",
                                             "Bode Diagram — Closed Loop (Phase)"))
        fig3.add_trace(go.Scatter(x=w_cl, y=mag_cl, mode="lines", name="|T| (dB)"), row=1, col=1)
        fig3.add_trace(go.Scatter(x=w_cl, y=ph_cl,  mode="lines", name="∠T (deg)"), row=2, col=1)
        fig3.update_xaxes(type="log", range=[-1, 2], matches='x', row=1, col=1)
        fig3.update_xaxes(type="log", range=[-1, 2], matches='x', row=2, col=1, title_text="Frequency (rad/sec)")
        fig3.update_yaxes(title="Magnitude (dB)", range=[-60, 20], row=1, col=1)
        fig3.update_yaxes(title="Phase (deg)",     range=[-200, 0], row=2, col=1)
        if save_prefix:
            fig3.write_html(out_path(f"{save_prefix}_bode_closed.html"), include_plotlyjs="cdn")
        if show:
            fig3.show(config={"responsive": True})

        # Root locus
        fig4 = go.Figure()
        for i in range(rlist.shape[0]):
            xi = np.real(rlist[i, :]); yi = np.imag(rlist[i, :])
            fig4.add_trace(go.Scatter(x=xi, y=yi, mode="lines",
                                      name=f"branch {i+1}", connectgaps=False))
        fig4.update_xaxes(range=[rl_xmin, rl_xmax], title="Real", scaleanchor="y")
        fig4.update_yaxes(range=[rl_ymin, rl_ymax], title="Imag", scaleratio=1)
        fig4.update_layout(title="Root Locus of L(s)=Gc(s)G(s) with scalar gain k",
                           autosize=(width is None), width=width, height=650)
        if save_prefix:
            fig4.write_html(out_path(f"{save_prefix}_root_locus.html"), include_plotlyjs="cdn")
        if show:
            fig4.show(config={"responsive": True})

def run_app(req: RegulatorRunRequest) -> None:
    service = RegulatorService(req)
    result = service.run()
    # Plotting
    if req.plots != "none":
        _maybe_plot(service,
                    show=True, save_prefix=req.save_prefix,
                    rl_axes=req.rl_axes, rl_k=req.rl_k,
                    backend=req.plots, ply_width=req.ply_width)
    logging.info("Done.")
