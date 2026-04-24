from __future__ import annotations
import os, numpy as np
from typing import Optional
from .utils import ensure_out_dir, pick_tgrid_from_poles, forced_xy
from .design import Candidate
import control as ct

PLOTLY_OK = True
try:
    import plotly.graph_objects as go  # type: ignore
except Exception:
    PLOTLY_OK = False

def _save_plotly(fig: "go.Figure", path: str):
    fig.update_layout(margin=dict(l=50, r=20, t=60, b=50))
    fig.write_html(path, include_plotlyjs="cdn", full_html=True,
                   default_width="100%", default_height="520px")
    print(f"[saved] {path}")

def step_reference(prefix: str, cand: Candidate):
    if not PLOTLY_OK: 
        print("[warn] Plotly not available."); return
    from control.timeresp import step_response
    t = pick_tgrid_from_poles(ct.poles(cand.T_ref))
    t, y = step_response(cand.T_ref, t)
    y = np.squeeze(np.asarray(y, dtype=float))
    fig = go.Figure()
    info = (f"OS={cand.metrics_ref.overshoot:.2f}% Ts={cand.metrics_ref.settling_time:.3g}s")
    fig.add_trace(go.Scatter(x=t, y=y, mode="lines", name="Output y(t)",
                             hovertemplate="t=%{x:.3g}<br>y=%{y:.3g}<br>"+info))
    fig.update_layout(title="Step response (reference)", xaxis_title="t (s)", yaxis_title="y", template="plotly_white")
    _save_plotly(fig, os.path.join(ensure_out_dir(), f"{prefix}_step_ref.html"))

def step_disturbance(prefix: str, cand: Candidate):
    if not PLOTLY_OK: 
        print("[warn] Plotly not available."); return
    from control.timeresp import step_response
    t = pick_tgrid_from_poles(ct.poles(cand.T_dist))
    t, y = step_response(cand.T_dist, t)
    y = np.squeeze(np.asarray(y, dtype=float))
    fig = go.Figure()
    info = (f"Ts={cand.metrics_dist.settling_time:.3g}s")
    fig.add_trace(go.Scatter(x=t, y=y, mode="lines", name="Output y(t)",
                             hovertemplate="t=%{x:.3g}<br>y=%{y:.3g}<br>"+info))
    fig.update_layout(title="Disturbance step response", xaxis_title="t (s)", yaxis_title="y", template="plotly_white")
    _save_plotly(fig, os.path.join(ensure_out_dir(), f"{prefix}_step_dist.html"))

def ramp_reference(prefix: str, cand: Candidate):
    if not PLOTLY_OK: 
        print("[warn] Plotly not available."); return
    t = pick_tgrid_from_poles(ct.poles(cand.T_ref)); r = t
    t, y = forced_xy(cand.T_ref, t, r)
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=r, mode="lines", name="Unit ramp r(t)=t", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=t, y=y, mode="lines", name="Output y(t)"))
    fig.update_layout(title="Ramp response (reference)", xaxis_title="t (s)", yaxis_title="y", template="plotly_white")
    _save_plotly(fig, os.path.join(ensure_out_dir(), f"{prefix}_ramp_ref.html"))

def accel_reference(prefix: str, cand: Candidate):
    if not PLOTLY_OK: 
        print("[warn] Plotly not available."); return
    t = pick_tgrid_from_poles(ct.poles(cand.T_ref)); r = 0.5*t**2
    t, y = forced_xy(cand.T_ref, t, r)
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=r, mode="lines", name="Unit acc r(t)=0.5 t²", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=t, y=y, mode="lines", name="Output y(t)"))
    fig.update_layout(title="Acceleration response (reference)", xaxis_title="t (s)", yaxis_title="y", template="plotly_white")
    _save_plotly(fig, os.path.join(ensure_out_dir(), f"{prefix}_accel_ref.html"))
