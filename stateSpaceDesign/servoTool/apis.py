from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np
from .core import ServoMode, ServoIOModel
from .design import ServoSynthesizer
from .io import load_controller_json, save_io_json, save_csv
from .utils import parse_matrix, parse_time

@dataclass
class RunRequest:
    data_path: str
    mode_C: Optional[str] = None   # C string for K mode (e.g., "1 0 0")
    r: float = 1.0
    k_r_override: Optional[float] = None
    t: str = "0:0.01:5"
    save_csv: Optional[str] = None
    export_json: Optional[str] = None
    backend: str = "none"
    no_show: bool = False

@dataclass
class RunResponse:
    model: ServoIOModel
    io_json_path: Optional[str] = None
    csv_path: Optional[str] = None
    plot_html_path: Optional[str] = None

def run(req: RunRequest) -> RunResponse:
    payload = load_controller_json(req.data_path)
    C_override = parse_matrix(req.mode_C) if (req.mode_C and payload.mode == ServoMode.K) else None

    syn = ServoSynthesizer(payload, C_override=C_override)
    model = syn.build(r=req.r, k_r_override=req.k_r_override)

    io_json_path = None
    if req.export_json:
        io_json_path = save_io_json(req.export_json, model.to_jsonable())

    csv_path = None
    plot_html_path = None

    if req.save_csv or req.backend != "none":
        T = parse_time(req.t)
        T, Y = ServoSynthesizer.quick_step(model, T=T)

        if req.save_csv:
            csv_path = save_csv(req.save_csv, T=T, Y=Y, header="t,y")

        if req.backend in ("mpl", "both"):
            import matplotlib.pyplot as plt
            plt.figure(figsize=(7.2, 3.0))
            plt.plot(T, Y)
            plt.grid(True, alpha=0.3)
            plt.title("Servo unit-step response")
            plt.xlabel("t (s)")
            plt.ylabel("y")
            if not req.no_show:
                plt.show()

        if req.backend in ("plotly", "both"):
            try:
                import plotly.graph_objects as go
            except Exception as e:
                raise RuntimeError(f"Plotly not available: {e}")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=T, y=Y, mode="lines", name="y"))
            fig.update_layout(template="plotly_white", xaxis_title="t (s)", yaxis_title="y",
                              autosize=True, title="Servo unit-step response")
            from .io import ensure_out_path
            html_path = ensure_out_path("servo_plot.html", "servo_plot.html")
            with open(html_path, "w", encoding="utf-8") as fh:
                fh.write(fig.to_html(full_html=True, include_plotlyjs="cdn",
                                     default_width="100%", default_height="70vh"))
            plot_html_path = html_path

    return RunResponse(model=model, io_json_path=io_json_path, csv_path=csv_path, plot_html_path=plot_html_path)
