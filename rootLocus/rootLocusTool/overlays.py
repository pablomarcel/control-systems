from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import math

# Plotly optional
try:  # pragma: no cover
    import plotly.graph_objects as go  # type: ignore
    _PLOTLY_OK = True
except Exception:  # pragma: no cover
    go = None  # type: ignore
    _PLOTLY_OK = False

from .core import tf_siso_arrays

@dataclass(slots=True)
class SGridOverlay:
    zetas: List[float]
    wns: List[float]
    label_zeta: bool = True
    label_wn: bool = True

    @staticmethod
    def parse_grid_spec(spec: Optional[str], default: Optional[List[float]]) -> List[float]:
        if spec is None:
            return default[:] if default is not None else []
        s = spec.strip().lower()
        if s in ("", "none"):
            return []
        if s.startswith("range:"):
            _, rest = s.split(":", 1)
            a, b, step = [float(x) for x in rest.split(":")]
            if step == 0: return []
            vals = list(np.arange(a, b + 0.5 * abs(step), step))
            return [float(v) for v in vals]
        if s.startswith("lin:"):
            _, rest = s.split(":", 1)
            a, b, N = [float(x) for x in rest.split(":")]
            N = max(2, int(N))
            return [float(v) for v in np.linspace(a, b, N)]
        if s.startswith("log:"):
            _, rest = s.split(":", 1)
            a, b, N = [float(x) for x in rest.split(":")]
            N = max(2, int(N))
            return [float(v) for v in np.logspace(math.log10(a), math.log10(b), N)]
        return [float(x) for x in spec.replace(";", ",").split(",") if x.strip() != ""]

    def add_to(self, fig, xlim, ylim) -> None:
        if not _PLOTLY_OK:
            return  # silently skip when Plotly not available
        L = max(abs(xlim[0]), abs(xlim[1]), abs(ylim[0]), abs(ylim[1]))
        first_z = True
        for z in self.zetas:
            if not (0.0 <= z <= 1.0): continue
            theta = math.acos(z)
            for sgn in (+1, -1):
                xs = np.array([0.0, -L * math.cos(theta)])
                ys = np.array([0.0,  sgn * L * math.sin(theta)])
                fig.add_trace(go.Scatter(
                    x=xs, y=ys, mode="lines",
                    line=dict(color="green", dash="dot", width=1),
                    name=("ζ-line" if first_z else None),
                    showlegend=first_z,
                    hovertemplate="ζ=%{customdata:.3f}<br>φ=%{text}°<extra></extra>",
                    customdata=[z, z],
                    text=[f"{math.degrees(theta):.1f}", f"{math.degrees(theta):.1f}"]
                ))
                first_z = False
            if self.label_zeta:
                xlab = -0.88 * L * math.cos(theta)
                ylab =  0.88 * L * math.sin(theta)
                fig.add_annotation(x=xlab, y=ylab, xref="x", yref="y",
                                   text=f"ζ={z:g}", showarrow=False,
                                   font=dict(color="green", size=12),
                                   bgcolor="rgba(255,255,255,0.6)")

        t = np.linspace(0, 2 * math.pi, 200)
        first_w = True
        for wn in self.wns:
            if wn <= 0: continue
            fig.add_trace(go.Scatter(
                x=wn * np.cos(t), y=wn * np.sin(t), mode="lines",
                line=dict(color="purple", dash="dot", width=1),
                name=("ωn-circle" if first_w else None),
                showlegend=first_w,
                hovertemplate="ωₙ=%{customdata:.3g}<extra></extra>",
                customdata=[wn] * len(t)
            ))
            first_w = False
            if self.label_wn:
                ang = math.radians(12.0)
                xlab = wn * math.cos(ang)
                ylab = wn * math.sin(ang)
                fig.add_annotation(x=xlab, y=ylab, xref="x", yref="y",
                                   text=f"ωₙ={wn:g}", showarrow=False,
                                   font=dict(color="purple", size=12),
                                   bgcolor="rgba(255,255,255,0.6)")

def _eval_absL_on_grid(L0, xr, yr, res):
    x = np.linspace(xr[0], xr[1], int(res))
    y = np.linspace(yr[0], yr[1], int(res))
    X, Y = np.meshgrid(x, y)
    S = X + 1j * Y
    num, den = tf_siso_arrays(L0)
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        L = np.polyval(num, S) / np.polyval(den, S)
    AbsL = np.abs(L).astype(float)
    AbsL[~np.isfinite(AbsL)] = np.nan
    Kgrid = np.divide(1.0, AbsL, out=np.full_like(AbsL, np.nan), where=(AbsL > 0))
    return x, y, AbsL, Kgrid

@dataclass(slots=True)
class ConstGainOverlay:
    kgains: Optional[List[float]] = None
    absL_levels: Optional[List[float]] = None
    res: int = 181

    def add_to(self, fig, L0, xr, yr) -> None:
        if not _PLOTLY_OK:
            return  # silently skip when Plotly not available
        levels_K = [k for k in (self.kgains or []) if k and k > 0]
        levels_abs = [a for a in (self.absL_levels or []) if a and a > 0]
        if not levels_K and not levels_abs:
            return

        x, y, AbsL, Kgrid = _eval_absL_on_grid(L0, xr, yr, max(32, int(self.res)))
        K_line   = dict(color="#555555", width=2, dash="dash")
        Abs_line = dict(color="#999999", width=2, dash="dot")

        def fmt_grid(g):
            out = np.where(np.isfinite(g), np.char.mod('%.3g', g), np.full_like(g, '', dtype=object))
            return out

        Ktxt  = fmt_grid(Kgrid)
        Ltxt  = fmt_grid(AbsL)
        textK = np.char.add(np.char.add('K=', Ktxt), np.char.add('<br>|L₀|=', Ltxt))
        textL = np.char.add(np.char.add('|L₀|=', Ltxt), np.char.add('<br>K=', Ktxt))

        def _add_contour(zgrid, custom, textgrid, level, label, line_style):
            eps = max(1e-12, 1e-9 * (abs(level) if np.isfinite(level) else 1.0))
            fig.add_trace(go.Contour(
                x=x, y=y, z=zgrid, customdata=custom, text=textgrid,
                contours=dict(start=level - eps, end=level + eps, size=eps,
                              coloring="lines", showlines=True),
                line=line_style, opacity=0.9,
                showscale=False, name=label,
                hovertemplate="%{text}<extra></extra>"
            ))

        for K in levels_K:
            _add_contour(Kgrid, Kgrid, textK, K, f"const-gain K={K:g}", K_line)
        for a in levels_abs:
            _add_contour(AbsL, Kgrid, textL, a, f"|L₀|={a:g}", Abs_line)
