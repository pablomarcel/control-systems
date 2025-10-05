from __future__ import annotations
import numpy as np

def plot_mpl_initial(T, x, y, u, title: str = "LQR initial-condition response"):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    for i in range(x.shape[0]):
        axs[0].plot(T, x[i, :], label=f"x{i+1}")
    for j in range(y.shape[0]):
        axs[0].plot(T, y[j, :], "--", label=f"y{j+1}")
    axs[0].set_ylabel("states / y")
    axs[0].grid(True); axs[0].legend()
    axs[1].plot(T, u.flatten(), label="u1")
    axs[1].set_xlabel("time (s)"); axs[1].set_ylabel("control")
    axs[1].grid(True); axs[1].legend()
    fig.suptitle(title)
    plt.tight_layout()
    return fig

def plot_mpl_step(T, x, y, u, title: str = "LQR unit-step response (servo)"):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    for i in range(x.shape[0]):
        axs[0].plot(T, x[i, :], label=f"x{i+1}")
    for j in range(y.shape[0]):
        axs[0].plot(T, y[j, :], "--", label=f"y{j+1}")
    axs[0].set_ylabel("states / y")
    axs[0].grid(True); axs[0].legend()
    axs[1].plot(T, u.flatten(), label="u1")
    axs[1].set_xlabel("time (s)"); axs[1].set_ylabel("control")
    axs[1].grid(True); axs[1].legend()
    fig.suptitle(title)
    plt.tight_layout()
    return fig

def plot_plotly_initial(T, x, y, u, title: str = "LQR initial-condition response"):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("States / y", "Control"))
    for i in range(x.shape[0]):
        fig.add_trace(go.Scatter(x=T, y=x[i, :], name=f"x{i+1}"), row=1, col=1)
    for j in range(y.shape[0]):
        fig.add_trace(go.Scatter(x=T, y=y[j, :], name=f"y{j+1}", line=dict(dash="dash")), row=1, col=1)
    fig.add_trace(go.Scatter(x=T, y=u.flatten(), name="u1"), row=2, col=1)
    fig.update_xaxes(title_text="time (s)", row=2, col=1)
    fig.update_yaxes(title_text="states / y", row=1, col=1)
    fig.update_yaxes(title_text="control", row=2, col=1)
    fig.update_layout(title=title, height=600)
    return fig

def plot_plotly_step(T, x, y, u, title: str = "LQR unit-step response (servo)"):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("States / y", "Control"))
    for i in range(x.shape[0]):
        fig.add_trace(go.Scatter(x=T, y=x[i, :], name=f"x{i+1}"), row=1, col=1)
    for j in range(y.shape[0]):
        fig.add_trace(go.Scatter(x=T, y=y[j, :], name=f"y{j+1}", line=dict(dash="dash")), row=1, col=1)
    fig.add_trace(go.Scatter(x=T, y=u.flatten(), name="u1"), row=2, col=1)
    fig.update_xaxes(title_text="time (s)", row=2, col=1)
    fig.update_yaxes(title_text="states / y", row=1, col=1)
    fig.update_yaxes(title_text="control", row=2, col=1)
    fig.update_layout(title=title, height=600)
    return fig
