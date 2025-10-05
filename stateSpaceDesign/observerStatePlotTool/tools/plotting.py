from __future__ import annotations
from dataclasses import dataclass
from typing import List
import numpy as np
from ..utils import ensure_out_path

@dataclass
class MplPlotter:
    title: str = "Observer/Controller simulation"
    y_label: str = "value"
    subplots: bool = False
    no_show: bool = False

    def plot(self, t: np.ndarray, series: List[np.ndarray], labels: List[str],
             save_png: str | None) -> str | None:
        import matplotlib.pyplot as plt
        png_path = None
        if self.subplots and len(series) > 1:
            h = max(5.0, 1.6*len(series))
            fig, axes = plt.subplots(len(series), 1, figsize=(8.0, h), sharex=True)
            axes = np.atleast_1d(axes)
            for i, ax in enumerate(axes):
                ax.plot(t, series[i])
                ax.grid(True, alpha=0.3)
                ax.set_ylabel(labels[i])
            axes[-1].set_xlabel("t (s)")
            fig.suptitle(self.title)
            fig.tight_layout()
        else:
            fig, ax = plt.subplots(1, 1, figsize=(8.0, 4.8))
            for s, lab in zip(series, labels):
                ax.plot(t, s, label=lab)
            ax.grid(True, alpha=0.3)
            ax.set_title(self.title)
            ax.set_xlabel("t (s)")
            ax.set_ylabel(self.y_label)
            if len(series) > 1:
                ax.legend()
            fig.tight_layout()
        if save_png is not None:
            png_path = ensure_out_path(save_png, "observer_plot.png")
            fig.savefig(png_path, dpi=150, bbox_inches="tight")
        if not self.no_show:
            plt.show()
        return png_path

@dataclass
class PlotlyPlotter:
    title: str = "Observer/Controller simulation"
    y_label: str = "value"
    subplots: bool = False

    def plot(self, t: np.ndarray, series: List[np.ndarray], labels: List[str],
             save_html: str | None) -> str:
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except Exception as e:
            raise RuntimeError(f"Plotly requested but not available: {e}")
        if self.subplots and len(series) > 1:
            fig = make_subplots(rows=len(series), cols=1, shared_xaxes=True,
                                vertical_spacing=0.02, subplot_titles=labels)
            for i, s in enumerate(series, start=1):
                fig.add_trace(go.Scatter(x=t, y=s, mode="lines", name=labels[i-1]),
                              row=i, col=1)
            fig.update_layout(title=self.title, template="plotly_white",
                              autosize=True, height=max(350, 180*len(series)))
            fig.update_xaxes(title_text="t (s)", row=len(series), col=1)
        else:
            fig = go.Figure()
            for s, lab in zip(series, labels):
                fig.add_trace(go.Scatter(x=t, y=s, mode="lines", name=lab))
            fig.update_layout(title=self.title, xaxis_title="t (s)", yaxis_title=self.y_label,
                              template="plotly_white",
                              legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                          xanchor="right", x=1),
                              autosize=True)
        html_path = ensure_out_path(save_html, "observer_plot.html")
        html = fig.to_html(full_html=True, include_plotlyjs="cdn",
                           default_width="100%", default_height="70vh")
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        return html_path
