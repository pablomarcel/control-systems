from __future__ import annotations
import os
import numpy as np
from ..design import ModelSpec
from ..utils import ensure_dir

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except Exception:
    go = None

def _collect_vlines(spec: ModelSpec):
    def fmt(x: float) -> str:
        return f"{x:.3g}" if (x >= 100 or x < 0.1) else f"{x:.3f}".rstrip("0").rstrip(".")
    v = []
    for z in spec.zeros:  v.append((f"ω_z={fmt(float(z))}", float(z)))
    for p in spec.poles1: v.append((f"ω_p={fmt(float(p))}", float(p)))
    for wn in spec.wns:   v.append((f"ω_n={fmt(float(wn))}", float(wn)))
    return sorted(v, key=lambda t: t[1])

def plot_bode_plotly(bode, *, spec: ModelSpec, title: str, path_prefix: str,
                     overlay=None, markers=True, nmarkers=40, vlines=True) -> str:
    if go is None:
        raise RuntimeError("Plotly not available. Install plotly + kaleido for HTML/PNG export.")
    w, mag_db, phase_deg = bode.w, bode.mag_db, bode.phase_deg
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=("Magnitude (dB)", "Phase (deg)"))
    fig.add_trace(go.Scatter(x=w, y=mag_db, mode="lines", name="model",
                             hovertemplate="ω=%{x:.3g}<br>|G|=%{y:.3f} dB"), row=1, col=1)
    fig.add_trace(go.Scatter(x=w, y=phase_deg, mode="lines", name="model", showlegend=False,
                             hovertemplate="ω=%{x:.3g}<br>∠G=%{y:.2f}°"), row=2, col=1)
    if markers:
        idx = np.unique(np.clip(np.round(np.linspace(0, len(w)-1, max(8,int(nmarkers)))), 0, len(w)-1).astype(int))
        fig.add_trace(go.Scatter(x=w[idx], y=mag_db[idx], mode="markers", name="model pts",
                                 marker=dict(size=6)), row=1, col=1)
        fig.add_trace(go.Scatter(x=w[idx], y=phase_deg[idx], mode="markers", name="model pts",
                                 showlegend=False, marker=dict(size=6)), row=2, col=1)
    if overlay is not None:
        fig.add_trace(go.Scatter(x=overlay['w'], y=overlay['mag_db'], mode="lines",
                                 line=dict(dash='dash'), name=overlay.get('label','experimental')), row=1, col=1)
        fig.add_trace(go.Scatter(x=overlay['w'], y=overlay['phase_deg'], mode="lines",
                                 line=dict(dash='dash'), name=overlay.get('label','experimental')), row=2, col=1)
    if vlines:
        for lbl, x in _collect_vlines(spec):
            fig.add_vline(x=x, line_dash="dot", line_color="black", opacity=0.6, row="all", col=1)
            fig.add_annotation(x=x, y=1.02, xref="x",  yref="y domain",
                               text=lbl, showarrow=False, yanchor="bottom",
                               textangle=90, font=dict(size=10, color="black"))
            fig.add_annotation(x=x, y=1.02, xref="x2", yref="y2 domain",
                               text=lbl, showarrow=False, yanchor="bottom",
                               textangle=90, font=dict(size=10, color="black"))
    wmin, wmax = float(np.min(w)), float(np.max(w))
    log_range = [np.log10(wmin), np.log10(wmax)]
    fig.update_xaxes(type="log", range=log_range, title_text="ω (rad/s)", row=1, col=1,
                     showgrid=True, minor=dict(showgrid=True))
    fig.update_xaxes(type="log", range=log_range, matches="x", row=2, col=1,
                     showgrid=True, minor=dict(showgrid=True))
    fig.update_yaxes(title_text="dB", row=1, col=1, showgrid=True, minor=dict(showgrid=True))
    fig.update_yaxes(title_text="deg", row=2, col=1, showgrid=True, minor=dict(showgrid=True))
    box = (f"K={spec.K:g}, λ={spec.lam}, zeros={spec.zeros}, "
           f"poles1={spec.poles1}, pairs={list(zip(spec.wns,spec.zetas))}, T={spec.delay:g}s")
    fig.update_layout(title=f"{title}<br><sup>{box}</sup>", height=740, autosize=True)
    outdir = ensure_dir(os.path.dirname(path_prefix) or ".")
    html = os.path.join(outdir, f"{os.path.basename(path_prefix)}.html")
    fig.write_html(html, include_plotlyjs="cdn", full_html=True)
    try:
        fig.write_image(os.path.join(outdir, f"{os.path.basename(path_prefix)}.png"), scale=2)
    except Exception:
        pass
    return html
