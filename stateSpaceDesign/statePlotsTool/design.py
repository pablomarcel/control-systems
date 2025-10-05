# SPDX-License-Identifier: MIT
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np

from .utils import resolve_out_path, with_outdir
from .core import SimICResult, SimStepResult

@dataclass(frozen=True)
class CSVExporter:
    @with_outdir
    def save_ic(self, res: SimICResult, filename: str | None = None, out_dir: Path | None = None) -> Path:
        import numpy as np
        out = resolve_out_path(filename, "ic_state_response.csv", out_dir)
        M = np.column_stack([res.t] + [res.X[i,:] for i in range(res.X.shape[0])])
        header = "t," + ",".join(res.labels)
        np.savetxt(out, M, delimiter=",", header=header, comments="")
        return out

    @with_outdir
    def save_step(self, res: SimStepResult, filename: str | None = None, out_dir: Path | None = None) -> Path:
        import numpy as np
        out = resolve_out_path(filename, "step_response.csv", out_dir)
        M = np.column_stack([res.t] + res.series)
        header = "t," + ",".join(res.labels)
        np.savetxt(out, M, delimiter=",", header=header, comments="")
        return out

@dataclass(frozen=True)
class PlotBackend:
    subplots: bool = False

    @with_outdir
    def mpl(self, t, series, labels, title, ylab, filename_png: str | None = None, out_dir: Path | None = None):
        import matplotlib.pyplot as plt
        out_png = resolve_out_path(filename_png, "plot.png", out_dir) if filename_png is not None else None
        if self.subplots and len(series) > 1:
            h = max(5.0, 1.6*len(series))
            fig, axes = plt.subplots(len(series), 1, figsize=(8.0, h), sharex=True)
            axes = np.atleast_1d(axes)
            for i, ax in enumerate(axes):
                ax.plot(t, series[i])
                ax.grid(True, alpha=0.3)
                ax.set_ylabel(labels[i])
            axes[-1].set_xlabel("t (s)")
            fig.suptitle(title)
            fig.tight_layout()
        else:
            fig, ax = plt.subplots(1, 1, figsize=(8.0, 4.8))
            for s, lab in zip(series, labels):
                ax.plot(t, s, label=lab)
            ax.grid(True, alpha=0.3)
            ax.set_title(title)
            ax.set_xlabel("t (s)")
            ax.set_ylabel(ylab)
            if len(series) > 1:
                ax.legend()
            fig.tight_layout()
        if out_png is not None:
            fig.savefig(out_png, dpi=150, bbox_inches="tight")
        return out_png

    @with_outdir
    def plotly(self, t, series, labels, title, ylab, filename_html: str | None = None, out_dir: Path | None = None):
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except Exception as e:
            raise RuntimeError(f"Plotly requested but not available: {e}")
        out_html = resolve_out_path(filename_html, "plot.html", out_dir) if filename_html is not None else None
        if self.subplots and len(series) > 1:
            fig = make_subplots(rows=len(series), cols=1, shared_xaxes=True,
                                vertical_spacing=0.02, subplot_titles=labels)
            for i, s in enumerate(series, start=1):
                fig.add_trace(go.Scatter(x=t, y=s, mode="lines", name=labels[i-1]), row=i, col=1)
            fig.update_layout(title=title, template="plotly_white",
                              autosize=True, height=max(350, 180*len(series)))
            fig.update_xaxes(title_text="t (s)", row=len(series), col=1)
        else:
            fig = go.Figure()
            for s, lab in zip(series, labels):
                fig.add_trace(go.Scatter(x=t, y=s, mode="lines", name=lab))
            fig.update_layout(title=title, xaxis_title="t (s)", yaxis_title=ylab,
                              template="plotly_white",
                              legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                          xanchor="right", x=1),
                              autosize=True)
        if out_html is not None:
            html = fig.to_html(full_html=True, include_plotlyjs="cdn",
                               default_width="100%", default_height="70vh")
            with open(out_html, "w", encoding="utf-8") as fh:
                fh.write(html)
        return out_html
