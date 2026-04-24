from __future__ import annotations
import numpy as np

from .apis import Margins
from .core import Analyzer

class BodePlotter:
    def __init__(self, analyzer: Analyzer | None = None):
        self.analyzer = analyzer or Analyzer()

    def matplotlib(self, L, w, margins: Margins, title: str, save_png: str | None):
        import matplotlib
        import platform
        _backend = (matplotlib.get_backend() or "").lower()
        if _backend in {"agg","pdf","svg","template","cairo"}:
            try:
                if platform.system() == "Darwin":
                    matplotlib.use("MacOSX", force=True)
                else:
                    matplotlib.use("TkAgg", force=True)
            except Exception:
                pass
        import matplotlib.pyplot as plt
        mag, phase, ww = self.analyzer.bode_data(L, w)
        phase_deg = np.degrees(np.unwrap(phase))
        fig, (ax1, ax2) = plt.subplots(2,1, figsize=(7.5,6.2), sharex=True)
        ax1.semilogx(ww, 20*np.log10(np.maximum(mag, 1e-16)), lw=2)
        ax1.grid(True, which="both", ls=":")
        ax1.set_ylabel("Magnitude (dB)")
        ax1.set_title(title)
        if np.isfinite(margins.wgc):
            ax1.axvline(margins.wgc, color="k", ls="--", lw=0.9)
            ax1.text(margins.wgc, ax1.get_ylim()[1]*0.9, " w_gc", rotation=90, va="top")
        if np.isfinite(margins.wpc):
            ax1.axvline(margins.wpc, color="gray", ls="--", lw=0.9)
            ax1.text(margins.wpc, ax1.get_ylim()[1]*0.8, " w_pc", rotation=90, va="top", color="gray")
        ax2.semilogx(ww, phase_deg, lw=2)
        ax2.grid(True, which="both", ls=":")
        ax2.set_xlabel(r"$\omega$ (rad/s)")
        ax2.set_ylabel("Phase (deg)")
        if np.isfinite(margins.wgc): ax2.axvline(margins.wgc, color="k", ls="--", lw=0.9)
        if np.isfinite(margins.wpc): ax2.axvline(margins.wpc, color="gray", ls="--", lw=0.9)
        fig.tight_layout()
        if save_png:
            fig.savefig(save_png, dpi=150)
        plt.show()
        return fig

    def plotly(self, L, w, margins: Margins, title: str, save_html: str | None):
        import plotly.graph_objects as go
        mag, phase, ww = self.analyzer.bode_data(L, w)
        phase_deg = np.degrees(np.unwrap(phase))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ww, y=20*np.log10(np.maximum(mag, 1e-16)),
                                 mode="lines", name="|L| (dB)", yaxis="y1"))
        fig.add_trace(go.Scatter(x=ww, y=phase_deg, mode="lines",
                                 name="∠L (deg)", yaxis="y2"))
        shapes=[]
        if np.isfinite(margins.wgc):
            shapes.append(dict(type="line", x0=margins.wgc, x1=margins.wgc,
                               y0=0, y1=1, xref="x", yref="paper",
                               line=dict(dash="dash")))
        if np.isfinite(margins.wpc):
            shapes.append(dict(type="line", x0=margins.wpc, x1=margins.wpc,
                               y0=0, y1=1, xref="x", yref="paper",
                               line=dict(dash="dot")))
        fig.update_layout(
            title=title,
            xaxis=dict(type="log", title="ω (rad/s)"),
            yaxis=dict(title="Magnitude (dB)"),
            yaxis2=dict(title="Phase (deg)", overlaying="y", side="right"),
            shapes=shapes, template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        if save_html:
            fig.write_html(save_html)
        fig.show()
        return fig

class ClassicalPlotters:
    def nyquist_matplotlib(self, L, w, save_png: str | None):
        import matplotlib
        import platform
        _backend = (matplotlib.get_backend() or "").lower()
        if _backend in {"agg","pdf","svg","template","cairo"}:
            try:
                if platform.system() == "Darwin":
                    matplotlib.use("MacOSX", force=True)
                else:
                    matplotlib.use("TkAgg", force=True)
            except Exception:
                pass
        import matplotlib.pyplot as plt
        import numpy as np
        from .utils import tf_arrays
        n, d = tf_arrays(L)
        jw = 1j*w
        Ljw = np.polyval(n, jw)/np.polyval(d, jw)
        track = np.concatenate([Ljw, np.conjugate(Ljw[-2:0:-1])])
        fig, ax = plt.subplots(1,1, figsize=(6.2,5.6))
        ax.plot(track.real, track.imag, lw=2)
        ax.axhline(0, color="k", lw=0.6); ax.axvline(0, color="k", lw=0.6)
        ax.plot([-1],[0],"kx", ms=8, mew=1.5)
        ax.set_xlabel("Re"); ax.set_ylabel("Im")
        ax.set_title("Nyquist plot"); ax.grid(True, ls=":")
        if save_png:
            fig.savefig(save_png, dpi=150)
        plt.show()
        return fig

    def nichols_matplotlib(self, L, w, save_png: str | None, analyzer: Analyzer | None = None):
        import matplotlib
        import platform
        _backend = (matplotlib.get_backend() or "").lower()
        if _backend in {"agg","pdf","svg","template","cairo"}:
            try:
                if platform.system() == "Darwin":
                    matplotlib.use("MacOSX", force=True)
                else:
                    matplotlib.use("TkAgg", force=True)
            except Exception:
                pass
        import matplotlib.pyplot as plt
        import numpy as np
        analyzer = analyzer or Analyzer()
        mag, phase, ww = analyzer.bode_data(L, w)
        phase_deg = np.degrees(np.unwrap(phase))
        fig, ax = plt.subplots(1,1, figsize=(6.8,5.2))
        ax.plot(phase_deg, 20*np.log10(np.maximum(mag, 1e-16)), lw=2)
        ax.set_xlabel("Phase (deg)"); ax.set_ylabel("Gain (dB)")
        ax.grid(True, ls=":"); ax.set_title("Nichols chart (basic)")
        if save_png:
            fig.savefig(save_png, dpi=150)
        plt.show()
        return fig
