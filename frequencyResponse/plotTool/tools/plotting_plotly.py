from __future__ import annotations
from typing import Optional, Sequence, Tuple, List
import numpy as np
from ..core import db, bode_data, Margins, CLMetrics, nichols_M_grid, nichols_N_grid

def bode_plot(L, w, margins: Margins, title: str, show_S: bool, show_T: bool,
              save_html: Optional[str], wmarks: Optional[List[float]]):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import control as ct
    mag, ph, ww = bode_data(L, w)
    ph_deg = np.degrees(ph)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.09,
                        subplot_titles=("Magnitude (dB)", "Phase (deg)"))
    fig.add_trace(go.Scatter(x=ww, y=db(mag), mode="lines", name="|L| (dB)"), row=1, col=1)
    if show_S or show_T:
        Ttf = ct.minreal(ct.feedback(L, 1), verbose=False)
        Stf = ct.minreal(1/(1 + L), verbose=False)
        Sm, _, _ = bode_data(Stf, ww); Tm, _, _ = bode_data(Ttf, ww)
        if show_S: fig.add_trace(go.Scatter(x=ww, y=db(Sm), mode="lines", name="|S| (dB)", line=dict(dash="dash")), row=1, col=1)
        if show_T: fig.add_trace(go.Scatter(x=ww, y=db(Tm), mode="lines", name="|T| (dB)", line=dict(dash="dot")), row=1, col=1)
    fig.add_trace(go.Scatter(x=ww, y=ph_deg, mode="lines", name="∠L (deg)"), row=2, col=1)
    shapes = []
    if np.isfinite(margins.wgc):
        shapes.append(dict(type="line", x0=margins.wgc, x1=margins.wgc, y0=0, y1=1, xref="x1", yref="paper", line=dict(dash="dash")))
    if np.isfinite(margins.wpc):
        shapes.append(dict(type="line", x0=margins.wpc, x1=margins.wpc, y0=0, y1=1, xref="x1", yref="paper", line=dict(dash="dot")))
    if wmarks:
        for wm in wmarks:
            shapes.append(dict(type="line", x0=wm, x1=wm, y0=0, y1=1, xref="x1", yref="paper", line=dict(dash="dot", width=1)))
    fig.update_layout(title=title, shapes=shapes, template="plotly_white",
                      legend=dict(orientation="h", y=1.08, x=1.0, xanchor="right"))
    fig.update_xaxes(type="log", row=1, col=1); fig.update_xaxes(type="log", row=2, col=1)
    fig.update_yaxes(title_text="Magnitude (dB)", row=1, col=1)
    fig.update_yaxes(title_text="Phase (deg)", row=2, col=1)
    if save_html: fig.write_html(save_html)

def nyquist_plot(L, w, title: str, markers: bool, nyq_samples: int, save_html: Optional[str]):
    import plotly.graph_objects as go
    from ..core import _eval_tf
    Hjw = _eval_tf(L, w)
    track = np.concatenate([Hjw, np.conjugate(Hjw[-2:0:-1])])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=track.real, y=track.imag, mode="lines", name="L(jω)"))
    if markers or nyq_samples > 0:
        if nyq_samples <= 0: nyq_samples = 11
        idxs = np.unique(np.clip(np.round(np.logspace(0, np.log10(len(w)-1), nyq_samples)).astype(int), 0, len(w)-1))
        fig.add_trace(go.Scatter(x=Hjw.real[idxs], y=Hjw.imag[idxs], mode="markers+text", name="ω samples",
                                 text=[f"ω={w[i]:.3g}" for i in idxs], textposition="top center"))
    fig.add_trace(go.Scatter(x=[-1], y=[0], mode="markers", marker=dict(symbol="x", size=12), name="-1+j0"))
    re_all = np.concatenate([track.real, np.array([-1.0])])
    im_all = np.concatenate([track.imag, np.array([0.0])])
    def _span(arr, pad=0.08):
        amin = float(np.nanmin(arr)) if arr.size else -1.0
        amax = float(np.nanmax(arr)) if arr.size else 1.0
        if not np.isfinite(amin) or not np.isfinite(amax): return -1.0, 1.0
        if abs(amax-amin) < 1e-12:
            delta = 1.0 if abs(amin) < 1.0 else 0.05*abs(amin)
            return amin-delta, amax+delta
        rng = amax - amin; return amin - pad*rng, amax + pad*rng
    x0, x1 = _span(re_all); y0, y1 = _span(im_all)
    fig.update_layout(title=title, xaxis_title="Re", yaxis_title="Im", template="plotly_white",
                      xaxis=dict(range=[x0, x1]), yaxis=dict(range=[y0, y1]))
    if save_html: fig.write_html(save_html)

def nichols_plot(L, w, margins: Margins, cl: CLMetrics, title: str, grid: bool, closedloop: bool,
                 save_html: Optional[str], nich_range: Optional[Tuple[float,float,float,float]],
                 m_levels_db: Sequence[float], n_alphas_deg: Sequence[float], label_grid: bool):
    import plotly.graph_objects as go
    import control as ct
    mag, ph, ww = bode_data(L, w)
    ph_deg = np.degrees(ph); g_db = db(mag)
    if nich_range: xmin, xmax, ymin, ymax = nich_range
    else:          xmin, xmax, ymin, ymax = -270, -30, -40, 20
    fig = go.Figure()
    if grid:
        X = np.linspace(xmin, xmax, 1501)
        GRID = "rgba(120,120,120,0.55)"; LAB = "rgba(90,90,90,0.9)"
        def _anchor(x,y, side="right"):
            x = np.asarray(x, float); y = np.asarray(y, float)
            m = np.isfinite(x) & np.isfinite(y)
            if not np.any(m): return None, None
            xi = x[m]; yi = y[m]; k = np.nanargmin(xi) if side=="left" else np.nanargmax(xi)
            return xi[k], yi[k]
        for x,y,label in nichols_M_grid(X, m_levels_db, (ymin,ymax)):
            fig.add_trace(go.Scatter(x=x,y=y,mode="lines", line=dict(dash="dot", width=1.2, color=GRID),
                                     hoverinfo="skip", showlegend=False))
            if label_grid:
                lx,ly=_anchor(x,y,"right")
                if lx is not None: fig.add_trace(go.Scatter(x=[lx],y=[ly],mode="text",text=[label],
                                                            textposition="middle right", textfont=dict(color=LAB,size=10),
                                                            hoverinfo="skip", showlegend=False))
        for x,y,label in nichols_N_grid(X, n_alphas_deg, (ymin,ymax)):
            fig.add_trace(go.Scatter(x=x,y=y,mode="lines", line=dict(dash="dash", width=1.0, color=GRID),
                                     hoverinfo="skip", showlegend=False))
            if label_grid:
                lx,ly=_anchor(x,y,"left")
                if lx is not None: fig.add_trace(go.Scatter(x=[lx],y=[ly],mode="text",text=[f"∠T={label}"],
                                                            textposition="middle left", textfont=dict(color=LAB,size=10),
                                                            hoverinfo="skip", showlegend=False))
    Ttf = ct.minreal(ct.feedback(L, 1), verbose=False)
    from ..core import bode_data as _bd
    magT, _, _ = _bd(Ttf, ww)
    fig.add_trace(go.Scatter(x=ph_deg, y=g_db, mode="lines", name="L(jω)", line=dict(width=3)))
    if np.isfinite(margins.wgc):
        x = float(np.interp(margins.wgc, ww, ph_deg))
        fig.add_trace(go.Scatter(x=[x], y=[0.0], mode="markers", name="w_gc", marker=dict(symbol="square", size=11)))
    if np.isfinite(margins.wpc):
        x = float(np.interp(margins.wpc, ww, ph_deg)); y = float(np.interp(margins.wpc, ww, g_db))
        fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers", name="w_pc", marker=dict(symbol="circle", size=10)))
    if closedloop:
        fig.add_trace(go.Scatter(x=[cl.L_wr_phi], y=[cl.L_wr_db], mode="markers", name="Mr point",
                                 marker=dict(symbol="diamond", size=12)))
        if np.isfinite(cl.wb):
            fig.add_trace(go.Scatter(x=[cl.L_wb_phi], y=[cl.L_wb_db], mode="markers", name="-3 dB BW",
                                     marker=dict(symbol="triangle-down", size=12)))
    fig.update_layout(title=f"Nichols — {title}", template="plotly_white",
                      xaxis=dict(title="Phase (deg)", range=[xmin, xmax], zeroline=False, showgrid=True, gridcolor="#eee"),
                      yaxis=dict(title="Gain (dB)",  range=[ymin, ymax], zeroline=True,  showgrid=True, gridcolor="#eee"),
                      legend=dict(orientation="h", y=1.07, x=1.0, xanchor="right"))
    if save_html: fig.write_html(save_html)
