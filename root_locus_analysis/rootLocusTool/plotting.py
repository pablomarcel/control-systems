from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
import csv, math, logging, os
import numpy as np

# Plotly is optional. If missing, we fall back to an HTML stub and CSV only.
try:  # pragma: no cover
    import plotly.graph_objects as go  # type: ignore
    _PLOTLY_OK = True
except Exception:  # pragma: no cover
    go = None  # type: ignore
    _PLOTLY_OK = False

from .core import tf_siso_arrays, poles_and_zeros, real_axis_intervals, break_points_poly, jw_crossings
from .geometry import asymptotes_centroid, compute_bounds

def _click_js():
    return r"""
var gd = document.getElementsByClassName('plotly-graph-div')[0];
if(!gd){return;}
gd.on('plotly_click', function(e){
    if(!e || !e.points || !e.points.length){return;}
    var pt = e.points[0];
    var x = pt.x, y = pt.y;
    var K = (pt.customdata !== undefined ? pt.customdata : null);
    var wn = Math.sqrt(x*x + y*y);
    var zeta = (wn>0) ? (-x/wn) : null;
    var text = 'σ=' + x.toFixed(4) + ', ω=' + y.toFixed(4);
    if(K!==null && !isNaN(K)){ text += ', K=' + Number(K).toPrecision(6); }
    if(zeta!==null){ text += ', ζ=' + zeta.toFixed(3) + ', ωₙ=' + wn.toFixed(3); }
    var ann = {x:x, y:y, text:text, showarrow:true, arrowhead:2, ax:40, ay:-40,
               bgcolor:'rgba(255,255,255,0.95)'};
    var anns = (gd.layout.annotations||[]);
    var keep = [];
    for(var i=0;i<anns.length;i++){
        if(anns[i].text && anns[i].text.indexOf('σ=')===0){continue;}
        keep.push(anns[i]);
    }
    keep.push(ann);
    Plotly.relayout(gd, {'annotations': keep});
});
"""

def ds_dK(num: np.ndarray, den: np.ndarray, s: complex, K: float) -> complex:
    N = np.poly1d(num); D = np.poly1d(den)
    dD = np.polyder(D); dN = np.polyder(N)
    denom = dD(s) + K * dN(s)
    if abs(denom) < 1e-14:
        return 0 + 0j
    return - N(s) / denom

def add_direction_arrows(fig, R: np.ndarray, K: np.ndarray,
                         num: np.ndarray, den: np.ndarray,
                         xlim: Tuple[float,float], ylim: Tuple[float,float],
                         every: int = 80, scale: float = 0.04) -> None:
    if not _PLOTLY_OK or R.size == 0:
        return
    span = max(abs(xlim[1] - xlim[0]), abs(ylim[1] - ylim[0]), 1.0)
    L = scale * span
    anns: List[dict] = []
    n = R.shape[1]
    for j in range(n):
        for t in range(0, len(K), every):
            s = R[t, j]; k = K[t]
            if not (xlim[0] <= s.real <= xlim[1] and ylim[0] <= s.imag <= ylim[1]):
                continue
            v = ds_dK(num, den, s, k)
            if v == 0:
                continue
            vx, vy = float(np.real(v)), float(np.imag(v))
            norm = math.hypot(vx, vy)
            if norm < 1e-14:
                continue
            vx, vy = (vx / norm) * L, (vy / norm) * L
            x2, y2 = s.real + vx, s.imag + vy
            x2 = max(min(x2, xlim[1]), xlim[0])
            y2 = max(min(y2, ylim[1]), ylim[0])
            anns.append(dict(
                x=x2, y=y2, ax=s.real, ay=s.imag,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=1.5,
                opacity=0.9
            ))
    existing = list(fig.layout.annotations) if fig.layout.annotations else []
    existing.extend(anns)
    fig.update_layout(annotations=existing)

def _write_html_stub(path: str, title: str, P: np.ndarray, Z: np.ndarray, K: np.ndarray, R: np.ndarray, log: logging.Logger) -> None:
    """Minimal HTML when Plotly is unavailable."""
    lines = [
        "<!doctype html><meta charset='utf-8'>",
        f"<title>{title} (no-plot fallback)</title>",
        f"<h2>{title}</h2>",
        "<p><em>Plotly not installed. This is a no-plot HTML stub written by rootLocusTool.</em></p>",
        "<h3>Open-loop Poles</h3>",
        f"<pre>{np.array2string(P, precision=5)}</pre>",
        "<h3>Open-loop Zeros</h3>",
        f"<pre>{np.array2string(Z, precision=5)}</pre>",
        "<h3>Sampled K grid</h3>",
        f"<pre>{np.array2string(K[:10], precision=5)} ... ({len(K)} samples)</pre>",
        "<h3>First few closed-loop roots</h3>",
        f"<pre>{np.array2string(R[:5,:], precision=5)}</pre>",
    ]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log.info(f"[saved] HTML (stub) -> {path}")

@dataclass(slots=True)
class PlotService:
    log: logging.Logger

    def plot(self, L0, R: np.ndarray, K: np.ndarray, klabels: List[float],
             title: str, html_out: str, png_out: Optional[str], csv_out: Optional[str],
             zgrid_overlay, cg_overlay,
             show_arrows: bool, arrow_every: int, arrow_scale: float,
             xlim: Optional[tuple[float,float]], ylim: Optional[tuple[float,float]]):

        num, den = tf_siso_arrays(L0)
        poles, zeros = poles_and_zeros(L0)

        # Always honor CSV, regardless of Plotly availability
        if csv_out:
            try:
                with open(csv_out, "w", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(["K"] + [f"root{i+1}" for i in range(R.shape[1])])
                    for t, k in enumerate(K):
                        w.writerow([k] + [complex(R[t, i]) for i in range(R.shape[1])])
                self.log.info(f"[saved] CSV -> {csv_out}")
            except Exception as e:
                self.log.warning(f"CSV save failed: {e}")

        if not _PLOTLY_OK:
            # Fallback: write an informative HTML (no figure)
            _write_html_stub(html_out, title, poles, zeros, K, R, self.log)
            if png_out:
                self.log.warning("PNG export requested but Plotly/Kaleido not available; skipping PNG.")
            return None

        # ---------- Plotly path (unchanged visuals) ----------
        ivs = real_axis_intervals(poles, zeros)
        brks = break_points_poly(num, den, ivs)
        jw   = jw_crossings(num, den)
        sigma_a, angs = asymptotes_centroid(poles, zeros)

        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis_title="σ = Re{s}",
            yaxis_title="ω = Im{s}",
            xaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor="#444",
                       showline=True, mirror=True, ticks="outside"),
            yaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor="#444",
                       showline=True, mirror=True, ticks="outside",
                       scaleanchor="x", scaleratio=1),
            legend=dict(bgcolor="rgba(255,255,255,0.75)"),
            hovermode="closest"
        )

        if xlim and ylim:
            xr, yr = xlim, ylim
        else:
            xr, yr = compute_bounds(R, poles, zeros, margin=0.12)
        fig.update_xaxes(range=list(xr))
        fig.update_yaxes(range=list(yr))

        if sigma_a is not None:
            fig.add_trace(go.Scatter(x=[sigma_a], y=[0], mode="markers",
                                     marker=dict(color="gray", size=9),
                                     name="centroid"))
            bound = max(abs(xr[0]-sigma_a), abs(xr[1]-sigma_a), abs(yr[0]), abs(yr[1])) * 1.05
            for th in angs:
                x1 = sigma_a + bound * math.cos(th); y1 = bound * math.sin(th)
                fig.add_shape(type="line", x0=sigma_a, y0=0, x1=x1, y1=y1,
                              line=dict(color="gray", width=1, dash="dash"))

        if zgrid_overlay:
            zgrid_overlay.add_to(fig, xr, yr)
        if cg_overlay:
            cg_overlay.add_to(fig, L0, xr, yr)

        n = R.shape[1]
        for j in range(n):
            x, y = R[:, j].real, R[:, j].imag
            fig.add_trace(go.Scatter(
                x=x, y=y, mode="lines",
                line=dict(width=2, color="#1f77b4"),
                name=f"branch {j+1}",
                customdata=K,
                hovertemplate="σ=%{x:.4g}, ω=%{y:.4g}<br>K=%{customdata:.6g}<extra></extra>",
            ))
            step = max(1, len(K) // 60)
            fig.add_trace(go.Scatter(
                x=x[::step], y=y[::step], mode="markers",
                marker=dict(size=4, color="#1f77b4"),
                showlegend=False,
                hovertemplate="σ=%{x:.4g}, ω=%{y:.4g}<br>K=%{customdata:.6g}<extra></extra>",
                customdata=K[::step]
            ))

        if len(poles):
            fig.add_trace(go.Scatter(x=poles.real, y=poles.imag, mode="markers",
                                     marker=dict(symbol="x", size=14, color="black"),
                                     name="open-loop poles"))
        if len(zeros):
            fig.add_trace(go.Scatter(x=zeros.real, y=zeros.imag, mode="markers",
                                     marker=dict(symbol="circle-open", size=12,
                                                 line=dict(width=2, color="black")),
                                     name="open-loop zeros"))

        for a,b in ivs:
            x0 = -10 if not np.isfinite(a) else a
            x1 =  10 if not np.isfinite(b) else b
            fig.add_shape(type="line", x0=x0, y0=0, x1=x1, y1=0,
                          line=dict(color="#1f77b4", width=4))

        for wv, Kv in jw:
            for y in (wv, -wv):
                fig.add_trace(go.Scatter(x=[0], y=[y], mode="markers+text",
                                         text=[f"K≈{Kv:.3g}"], textposition="middle right",
                                         marker=dict(color="#d62728", size=9),
                                         showlegend=False))
        for s0, K0 in brks:
            fig.add_trace(go.Scatter(x=[s0], y=[0], mode="markers+text",
                                     text=[f"BA K≈{K0:.3g}"], textposition="top center",
                                     marker=dict(color="#1f77b4", size=9),
                                     showlegend=False))

        for kval in (klabels or []):
            try:
                import control as _ctrl
                CL = _ctrl.feedback(kval * L0, 1)
                P = np.asarray(_ctrl.poles(CL) if hasattr(_ctrl, "poles") else _ctrl.pole(CL))
                fig.add_trace(go.Scatter(x=P.real, y=P.imag, mode="markers+text",
                                         text=[f"K={kval:g}"] * len(P), textposition="top center",
                                         marker=dict(color="#9467bd", size=9),
                                         showlegend=False))
            except Exception as e:
                self.log.warning(f"Could not label K={kval:g}: {e}")

        if show_arrows:
            add_direction_arrows(fig, R, K, num, den, xr, yr, every=arrow_every, scale=arrow_scale)

        try:
            fig.write_html(html_out, include_plotlyjs="cdn", post_script=_click_js())
            self.log.info(f"[saved] HTML -> {html_out}")
        except Exception as e:
            self.log.warning(f"HTML save failed: {e}")

        if png_out:
            try:
                fig.write_image(png_out, scale=2)
                self.log.info(f"[saved] PNG  -> {png_out}")
            except Exception as e:
                self.log.warning(f"PNG save failed (install 'kaleido'?): {e}")

        return fig
