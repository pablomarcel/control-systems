from __future__ import annotations
import json, csv
from typing import List, Optional, Tuple

import numpy as np
import control as ct

from .core import rlocus_map
from .design import DesignPoint
from .utils import ensure_out_path

def plot_mpl(L, zetas, rays, s_star: complex | None = None,
             title: str = "Root Locus with ζ-rays",
             xlim: Optional[Tuple[float,float]] = None,
             ylim: Optional[Tuple[float,float]] = None,
             save: Optional[str] = None):
    import matplotlib.pyplot as plt
    branches, kv = rlocus_map(L)
    fig, ax = plt.subplots(figsize=(8.5,5.8))
    step = max(1, branches.shape[1]//25)
    for i in range(branches.shape[0]):
        ax.plot(branches[i,:].real, branches[i,:].imag, lw=2, label=f'branch {i+1}')
        ax.plot(branches[i,::step].real, branches[i,::step].imag, 'o', ms=3)
    poles = ct.poles(L); zeros = ct.zeros(L)
    ax.plot(np.real(poles), np.imag(poles), 'x', ms=9, mew=2, label='open-loop poles')
    if len(zeros):
        ax.plot(np.real(zeros), np.imag(zeros), 'o', mfc='none', ms=8, mew=1.5, label='open-loop zeros')
    for z, (sig, w) in rays:
        ax.plot(sig,  w, '--', color='0.5', lw=1.5)
        ax.plot(sig, -w, '--', color='0.5', lw=1.5)
        idx = int(0.7*len(w))
        ax.text(sig[idx], w[idx], f'ζ={z:.2f}', fontsize=8, color='0.5')
    if s_star is not None:
        ax.plot([s_star.real], [s_star.imag], marker='*', ms=12, mfc='r', mec='k', label='s*')
    ax.set_title(title); ax.set_xlabel('Real'); ax.set_ylabel('Imag')
    ax.grid(True, ls=':'); ax.legend(loc='best', fontsize=9, framealpha=0.9)
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
    if save:
        out = ensure_out_path(save)
        plt.savefig(out, dpi=160, bbox_inches='tight')
    return fig, ax

def plot_plotly(L, zetas, rays, s_row: dict | None = None,
                title: str = "Root Locus with ζ-rays",
                xlim: Optional[Tuple[float,float]] = None,
                ylim: Optional[Tuple[float,float]] = None,
                save: Optional[str] = None):
    import plotly.graph_objects as go
    branches, kv = rlocus_map(L)
    nB, nG = branches.shape
    fig = go.Figure()
    if kv.size == 0:
        kv = np.arange(nG)
    elif kv.size != nG:
        kv = np.linspace(kv.min() if kv.size else 0.0, kv.max() if kv.size else 1.0, nG)
    # branches
    for i in range(nB):
        custom = np.array(kv)
        hovertemplate = (
            "K=%{customdata:.4g}<br>σ=%{x:.4g}<br>ω=%{y:.4g}"
            f"<extra>branch {i+1}</extra>"
        )
        fig.add_trace(go.Scatter(
            x=branches[i,:].real, y=branches[i,:].imag,
            mode='lines+markers', marker=dict(size=4),
            name=f'branch {i+1}',
            customdata=custom, hovertemplate=hovertemplate
        ))
    poles = ct.poles(L); zeros = ct.zeros(L)
    if len(poles):
        fig.add_trace(go.Scatter(
            x=np.real(poles), y=np.imag(poles),
            mode='markers', name='open-loop poles',
            marker=dict(symbol='x', size=12, line=dict(width=2)),
            hovertemplate="pole<br>σ=%{x:.4g}<br>ω=%{y:.4g}<extra></extra>"
        ))
    if len(zeros):
        fig.add_trace(go.Scatter(
            x=np.real(zeros), y=np.imag(zeros),
            mode='markers', name='open-loop zeros',
            marker=dict(symbol='circle-open', size=12, line=dict(width=2)),
            hovertemplate="zero<br>σ=%{x:.4g}<br>ω=%{y:.4g}<extra></extra>"
        ))
    # rays
    for z, (sig, w) in rays:
        custom = np.full_like(sig, z, dtype=float)
        fig.add_trace(go.Scatter(
            x=sig, y=w, mode='lines', line=dict(dash='dash'),
            name=f'ζ {z:.2f}', customdata=custom,
            hovertemplate="ζ=%{customdata:.3f}<br>σ=%{x:.3g}<br>ω=%{y:.3g}<extra>ζ-ray</extra>"
        ))
        fig.add_trace(go.Scatter(
            x=sig, y=-w, mode='lines', line=dict(dash='dash'),
            name=f'ζ {z:.2f}', showlegend=False, customdata=custom,
            hovertemplate="ζ=%{customdata:.3f}<br>σ=%{x:.3g}<br>ω=%{y:.3g}<extra>ζ-ray</extra>"
        ))
    if s_row is not None:
        s_star = complex(s_row["sigma"], s_row["jw"])
        cd = [s_row["zeta"], s_row["omega"], s_row["a"], s_row["K"], s_row["Kp"], s_row["Ti"], s_row["Td"]]
        fig.add_trace(go.Scatter(
            x=[s_star.real], y=[s_star.imag], mode='markers',
            marker=dict(size=14, symbol='star'),
            name='s*', customdata=[cd],
            hovertemplate=("s*<br>ζ=%{customdata[0]:.4g}, ω=%{customdata[1]:.4g}"
                           "<br>a=%{customdata[2]:.4g} (zero at -a)"
                           "<br>K=%{customdata[3]:.4g}, Kp=%{customdata[4]:.4g}"
                           "<br>Ti=%{customdata[5]:.4g}, Td=%{customdata[6]:.4g}"
                           "<extra></extra>")
        ))
    lay = dict(
        title=title, xaxis_title='Real', yaxis_title='Imag',
        autosize=True, margin=dict(l=60, r=30, t=60, b=50),
        legend=dict(orientation="v", x=1.02, y=1)
    )
    if xlim: lay["xaxis"] = dict(range=list(xlim))
    if ylim: lay["yaxis"] = dict(range=list(ylim))
    fig.update_layout(**lay)
    if save:
        out = ensure_out_path(save if str(save).lower().endswith(".html") else str(save)+".html")
        fig.write_html(out, include_plotlyjs='cdn', full_html=True, config={"responsive": True},
                       default_width="100%", default_height="100%")
    return fig

def export_json(path: str, payload: dict):
    out = ensure_out_path(path)
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)
    return out

def export_csv(path: str, rows: List[DesignPoint]):
    out = ensure_out_path(path)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["zeta","omega","a","K","Kp","Ti","Td","sigma","jw"])
        for r in rows:
            w.writerow([r.zeta,r.omega,r.a,r.K,r.Kp,r.Ti,r.Td,r.sigma,r.jw])
    return out
