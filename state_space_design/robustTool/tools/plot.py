from __future__ import annotations
import numpy as np
import control as ct

class Plotter:
    @staticmethod
    def bode_mpl(w, curves, title="Closed-loop Bode"):
        import matplotlib.pyplot as plt
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12,6), sharex=True)
        ax1.set_title(title)
        for label, data in curves:
            ax1.semilogx(w, data["mag"], lw=2, label=label)
        ax1.axhline(0, color='k', lw=1, ls='--', alpha=0.6)
        ax1.set_ylabel("dB"); ax1.grid(True, which='both', ls=':')
        ax1.legend()
        for label, data in curves:
            if data.get("phs") is not None:
                ax2.semilogx(w, data["phs"], lw=1.8)
        ax2.set_xlabel("rad/s"); ax2.set_ylabel("deg"); ax2.grid(True, which='both', ls=':')
        fig.tight_layout(); plt.show()

    @staticmethod
    def bode_plotly(w, curves, title="Closed-loop Bode"):
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=(f"{title} — magnitude", f"{title} — phase"))
        for label, data in curves:
            fig.add_trace(go.Scatter(x=w, y=data["mag"], mode="lines", name=label), row=1, col=1)
        fig.add_trace(go.Scatter(x=w, y=np.zeros_like(w), mode="lines",
                                 line=dict(dash="dash", width=1, color="black"),
                                 name="0 dB"), row=1, col=1)
        for label, data in curves:
            if data.get("phs") is not None:
                fig.add_trace(go.Scatter(x=w, y=data["phs"], mode="lines", name=f"{label} (phase)",
                                         showlegend=False), row=2, col=1)
        fig.update_xaxes(type="log", row=1, col=1); fig.update_xaxes(type="log", row=2, col=1)
        fig.update_yaxes(title_text="dB", row=1, col=1); fig.update_yaxes(title_text="deg", row=2, col=1)
        fig.update_layout(height=520, width=1200); fig.show()

    @staticmethod
    def step_mpl(t, y, u):
        import matplotlib.pyplot as plt
        fig, (ax1, ax2) = plt.subplots(2,1, figsize=(12,6), sharex=True)
        ax1.plot(t, y, lw=2, label="y (output)"); ax1.grid(True, ls=':'); ax1.set_ylabel("y"); ax1.legend()
        ax2.plot(t, u, lw=2, label="u (control)"); ax2.grid(True, ls=':'); ax2.set_xlabel("time (s)"); ax2.set_ylabel("u"); ax2.legend()
        fig.tight_layout(); plt.show()

    @staticmethod
    def step_plotly(t, y, u):
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=("Output y", "Control u"))
        fig.add_trace(go.Scatter(x=t, y=y, mode="lines", name="y"), row=1, col=1)
        fig.add_trace(go.Scatter(x=t, y=u, mode="lines", name="u"), row=2, col=1)
        fig.update_xaxes(title_text="time (s)", row=2, col=1)
        fig.update_yaxes(title_text="y", row=1, col=1); fig.update_yaxes(title_text="u", row=2, col=1)
        fig.update_layout(height=520, width=1200); fig.show()
