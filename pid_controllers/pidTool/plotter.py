from __future__ import annotations
from typing import List, Optional
import numpy as np
try:
    import control as ct
    from control.timeresp import step_response
except Exception:  # pragma: no cover
    ct = None
    step_response = None  # type: ignore

from .core import PLOTLY_OK, MPL_OK
from .core import Candidate, controller_tf

def plot_step_mpl(cands: List[Candidate], Gp: "ct.TransferFunction",
                  structure: str, top: int, save_path: Optional[str]):
    if not MPL_OK:
        print("[warn] Matplotlib not available.")
        return
    import matplotlib.pyplot as plt  # local import
    plt.figure(figsize=(8.5, 5.2))
    for i, cand in enumerate(cands[:top]):
        Gc = controller_tf(structure, cand.params)
        T = ct.feedback(Gc * Gp, 1)
        t, y = step_response(T, np.linspace(0, cand.metrics.tfinal_used, 1200))
        lab = (f"{i+1}: {cand.params} | OS={cand.metrics.overshoot:.2f}% Ts={cand.metrics.settling_time:.3g}s")
        plt.plot(t, y, label=lab)
    plt.grid(True, which="both", ls=":")
    plt.title("Unit-step response (top candidates)")
    plt.xlabel("Time (s)"); plt.ylabel("Output")
    plt.legend(fontsize=8)
    if save_path:
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.tight_layout(); plt.savefig(save_path, dpi=160)
        print(f"[saved] Matplotlib plot -> {save_path}")
    else:
        plt.show()
    plt.close()

def plot_step_plotly(cands: List[Candidate], Gp: "ct.TransferFunction",
                     structure: str, top: int, save_path: Optional[str]):
    if not PLOTLY_OK:
        print("[warn] Plotly not available.")
        return
    import plotly.graph_objects as go  # local import
    fig = go.Figure()
    for i, cand in enumerate(cands[:top]):
        Gc = controller_tf(structure, cand.params)
        T = ct.feedback(Gc * Gp, 1)
        t, y = step_response(T, np.linspace(0, cand.metrics.tfinal_used, 1200))
        info = (f"OS={cand.metrics.overshoot:.2f}% Ts={cand.metrics.settling_time:.3g}s "
                f"Tr={cand.metrics.rise_time:.3g}s ESS={cand.metrics.ess:.3g} ITAE={cand.metrics.itae:.3g}")
        fig.add_trace(go.Scatter(x=t, y=y, mode="lines",
                                 name=f"{i+1}: {cand.params}",
                                 hovertemplate="t=%{x:.3g}<br>y=%{y:.3g}<br>"+info))
    fig.update_layout(title="Unit-step response (top candidates)",
                      xaxis_title="Time (s)", yaxis_title="Output",
                      template="plotly_white", autosize=True)
    if save_path:
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.write_html(save_path, include_plotlyjs="cdn",
                       full_html=True, default_width="100%", default_height="520px")
        print(f"[saved] Plotly plot -> {save_path}")
    else:
        fig.show()
