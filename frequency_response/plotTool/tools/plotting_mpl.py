from __future__ import annotations
from typing import Optional, Sequence, Tuple, List
import os
import numpy as np

def _ensure_agg_backend():
    # Make tests headless-safe
    import matplotlib
    try:
        matplotlib.use("Agg")
    except Exception:
        pass

_ensure_agg_backend()
import matplotlib.pyplot as plt  # noqa

from ..core import bode_data, db, nichols_M_grid, nichols_N_grid
from ..core import Margins, CLMetrics

def bode_plot(L, w, margins: Margins, title: str, show_S: bool, show_T: bool,
              save_png: Optional[str], wmarks: Optional[List[float]]):
    import control as ct
    mag, ph, ww = bode_data(L, w)
    ph_deg = np.degrees(ph)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 6.6), sharex=True)

    ax1.semilogx(ww, db(mag), lw=2, label="|L|")
    if show_S or show_T:
        Ttf = ct.minreal(ct.feedback(L, 1), verbose=False)
        Stf = ct.minreal(1/(1 + L), verbose=False)
        Sm, _, _ = bode_data(Stf, ww); Tm, _, _ = bode_data(Ttf, ww)
        if show_S: ax1.semilogx(ww, db(Sm), "--", label="|S|")
        if show_T: ax1.semilogx(ww, db(Tm), ":", label="|T|")

    ax1.grid(True, which="both", ls=":"); ax1.set_ylabel("Magnitude (dB)"); ax1.set_title(title)
    if np.isfinite(margins.wgc): ax1.axvline(margins.wgc, color="k", ls="--", lw=0.9)
    if np.isfinite(margins.wpc): ax1.axvline(margins.wpc, color="gray", ls="--", lw=0.9)
    if wmarks:
        for wm in wmarks: ax1.axvline(wm, color="k", ls=":", lw=0.8)
    ax1.legend(loc="best", fontsize=9)

    ax2.semilogx(ww, ph_deg, lw=2)
    ax2.grid(True, which="both", ls=":"); ax2.set_xlabel(r"$\omega$ (rad/s)"); ax2.set_ylabel("Phase (deg)")
    if np.isfinite(margins.wgc): ax2.axvline(margins.wgc, color="k", ls="--", lw=0.9)
    if np.isfinite(margins.wpc): ax2.axvline(margins.wpc, color="gray", ls="--", lw=0.9)
    if wmarks:
        for wm in wmarks: ax2.axvline(wm, color="k", ls=":", lw=0.8)

    fig.tight_layout()
    if save_png:
        os.makedirs(os.path.dirname(save_png) or ".", exist_ok=True)
        fig.savefig(save_png, dpi=150)
        plt.close(fig)

def _nyq_symmetric_limits(track: np.ndarray, pad: float = 0.05):
    re = np.real(track); im = np.imag(track)
    R = max(np.max(np.abs(re)), np.max(np.abs(im)), 1.0); R *= (1.0 + pad)
    return -R, R

def nyquist_plot(L, w, title: str, markers: bool, save_png: Optional[str]):
    from ..core import _eval_tf
    Hjw = _eval_tf(L, w)
    track = np.concatenate([Hjw, np.conjugate(Hjw[-2:0:-1])])
    fig, ax = plt.subplots(1, 1, figsize=(7.0, 7.0)); ax.set_box_aspect(1)
    ax.plot(track.real, track.imag, lw=2, label="L(jω)")
    if markers: ax.plot(Hjw.real, Hjw.imag, ".", ms=3, alpha=0.7)
    ax.plot([-1], [0], "x", ms=8, mew=1.5, label="-1+j0", color="k")
    ax.axhline(0, color="k", lw=0.6); ax.axvline(0, color="k", lw=0.6)
    ax.grid(True, ls=":"); ax.set_aspect("equal", adjustable="box")
    x0, x1 = _nyq_symmetric_limits(np.concatenate([track, np.array([-1+0j])]))
    ax.set_xlim(x0, x1); ax.set_ylim(x0, x1)
    ax.set_xlabel("Re"); ax.set_ylabel("Im"); ax.set_title(title); ax.legend(loc="best", fontsize=9)
    if save_png:
        os.makedirs(os.path.dirname(save_png) or ".", exist_ok=True)
        fig.savefig(save_png, dpi=150); plt.close(fig)

def nichols_plot(L, w, margins: Margins, cl: CLMetrics, title: str, grid: bool, closedloop: bool,
                 save_png: Optional[str], nich_range: Optional[Tuple[float, float, float, float]],
                 m_levels_db: Sequence[float], n_alphas_deg: Sequence[float]):
    from ..core import bode_data
    mag, ph, ww = bode_data(L, w)
    ph_deg = np.degrees(ph); g_db = db(mag)
    if nich_range: xmin, xmax, ymin, ymax = nich_range
    else:          xmin, xmax, ymin, ymax = -270, -30, -40, 20

    fig, ax = plt.subplots(1,1, figsize=(7.6, 5.8))
    if grid:
        X = np.linspace(xmin, xmax, 1200)
        for x, y, _ in nichols_M_grid(X, m_levels_db, y_limits=(ymin, ymax)):
            ax.plot(x, y, ":", color="0.7", lw=1)
        for x, y, _ in nichols_N_grid(X, n_alphas_deg, y_limits=(ymin, ymax)):
            ax.plot(x, y, ":", color="0.85", lw=1)
    ax.plot(ph_deg, g_db, lw=2, label="L(jω)")
    if np.isfinite(margins.wgc):
        ax.scatter(np.interp(margins.wgc, ww, ph_deg), 0.0, marker="s", c="tab:orange", label="w_gc")
    if np.isfinite(margins.wpc):
        ax.scatter(np.interp(margins.wpc, ww, ph_deg), np.interp(margins.wpc, ww, g_db),
                   marker="o", c="tab:green", label="w_pc")
    if closedloop:
        ax.scatter(cl.L_wr_phi, cl.L_wr_db, marker="D", c="crimson", label="Mr point")
        if np.isfinite(cl.wb):
            ax.scatter(cl.L_wb_phi, cl.L_wb_db, marker="v", c="purple", label="-3 dB BW")
    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax)
    ax.grid(True, ls=":"); ax.set_xlabel("Phase (deg)"); ax.set_ylabel("Gain (dB)")
    ax.set_title(f"Nichols — {title}"); ax.legend(loc="best", fontsize=9)
    if save_png:
        os.makedirs(os.path.dirname(save_png) or ".", exist_ok=True)
        fig.savefig(save_png, dpi=150); plt.close(fig)
