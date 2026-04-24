from __future__ import annotations
from typing import List, Tuple, Dict
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, LogFormatter
from ..design import ModelSpec
from ..utils import ensure_dir

def _log_grid(ax):
    ax.set_xscale('log')
    ax.xaxis.set_major_locator(LogLocator(base=10.0))
    ax.xaxis.set_major_formatter(LogFormatter(base=10.0, labelOnlyBase=False))
    ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2,10)*0.1))
    ax.xaxis.set_minor_formatter(LogFormatter(base=10.0, labelOnlyBase=False))
    ax.grid(True, which='major', ls='-', alpha=0.25)
    ax.grid(True, which='minor', ls=':', alpha=0.35)

def _markers_indices(n: int, nmarkers: int) -> np.ndarray:
    nmarkers = max(8, int(nmarkers))
    return np.unique(np.clip(np.round(np.linspace(0, n-1, nmarkers)), 0, n-1).astype(int))

def _collect_vlines(spec: ModelSpec):
    def fmt(x: float) -> str:
        return f"{x:.3g}" if (x >= 100 or x < 0.1) else f"{x:.3f}".rstrip("0").rstrip(".")
    v = []
    for z in spec.zeros:  v.append((f"ω_z={fmt(float(z))}", float(z)))
    for p in spec.poles1: v.append((f"ω_p={fmt(float(p))}", float(p)))
    for wn in spec.wns:   v.append((f"ω_n={fmt(float(wn))}", float(wn)))
    return sorted(v, key=lambda t: t[1])

def plot_bode_mpl(bode, *, spec: ModelSpec, title: str, path_prefix: str,
                  overlay=None, markers=True, nmarkers=40, vlines=True) -> str:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10.5, 7.6), constrained_layout=True)
    w, mag_db, phase_deg = bode.w, bode.mag_db, bode.phase_deg
    ax1.semilogx(w, mag_db, label="model", lw=2)
    ax2.semilogx(w, phase_deg, label="model", lw=2)
    if markers:
        idx = _markers_indices(len(w), nmarkers)
        ax1.semilogx(w[idx], mag_db[idx], 'o', ms=3, alpha=.9)
        ax2.semilogx(w[idx], phase_deg[idx], 'o', ms=3, alpha=.9)
    if overlay is not None:
        ax1.semilogx(overlay['w'], overlay['mag_db'], '--', lw=2, label=overlay.get('label','experimental'))
        ax2.semilogx(overlay['w'], overlay['phase_deg'], '--', lw=2, label=overlay.get('label','experimental'))
    if vlines:
        for lbl, x in _collect_vlines(spec):
            ax1.axvline(x, color='k', ls=':', lw=1)
            ax2.axvline(x, color='k', ls=':', lw=1)
            ax2.annotate(lbl, xy=(x, 0.98), xycoords=('data', 'axes fraction'),
                         rotation=90, va='top', ha='right', fontsize=9, color='k')
    ax1.set_ylabel("Magnitude (dB)"); ax2.set_ylabel("Phase (deg)"); ax2.set_xlabel("ω (rad/s)")
    _log_grid(ax1); _log_grid(ax2); ax1.legend(); ax2.legend()
    box = (f"K={spec.K:g}, λ={spec.lam}, zeros={spec.zeros}, "
           f"poles1={spec.poles1}, pairs={list(zip(spec.wns,spec.zetas))}, T={spec.delay:g}s")
    fig.suptitle(f"{title}\n{box}", fontsize=12)
    outdir = ensure_dir(os.path.dirname(path_prefix) or ".")
    png = os.path.join(outdir, f"{os.path.basename(path_prefix)}.png")
    fig.savefig(png, dpi=180); plt.close(fig); return png
