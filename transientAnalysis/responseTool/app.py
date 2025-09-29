# transientAnalysis/responseTool/app.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from .core import SSModel, TFModel, ResponseEngine
from .io import IOConfig, save_json, save_plot


@dataclass(slots=True)
class ResponseResult:
    T: np.ndarray
    y: np.ndarray
    u: np.ndarray | None = None


@dataclass(slots=True)
class ResponseToolApp:
    # If None, default to the package directory: .../transientAnalysis/responseTool
    root: Path | None = None
    show_plots: bool = False

    # declare slot fields so we can assign them in __post_init__
    io: IOConfig = field(init=False)
    engine: ResponseEngine = field(init=False)

    def __post_init__(self):
        if self.root is None:
            # package directory: .../transientAnalysis/responseTool
            self.root = Path(__file__).resolve().parent
        self.io = IOConfig(self.root / "in", self.root / "out").ensure()
        self.engine = ResponseEngine()

    # ---------- SS ramp via augmentation ----------
    def compute_unit_ramp_ss(
        self, A, B, C, D, *, tfinal: float = 10.0, dt: float = 0.01, title_suffix: str = ""
    ) -> ResponseResult:
        model = SSModel(
            np.asarray(A, float),
            np.asarray(B, float),
            np.asarray(C, float),
            np.asarray(D, float),
        )
        T, z, y_ramp = self.engine.ramp_ss(model, tfinal=tfinal, dt=dt)
        if self.show_plots:
            plt.figure(figsize=(8.6, 4.6))
            plt.plot(T, z, label="augmented step → z(t)")
            plt.plot(T, y_ramp, "--", label="direct ramp → y(t)")
            plt.plot(T, T, ":", label="u(t)=t")
            plt.title(f"Unit-ramp via augmentation vs direct (SS){title_suffix}")
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude")
            plt.grid(True)
            plt.legend()
            save_plot(self.io.out_dir / "ramp_ss.png")
        save_json(
            self.io.out_dir / "ramp_ss.json",
            {"T": T.tolist(), "z": z.tolist(), "y_ramp": y_ramp.tolist()},
        )
        return ResponseResult(T=T, y=y_ramp, u=T)

    # ---------- TF arbitrary input ----------
    def simulate_tf_input(
        self,
        num,
        den,
        *,
        u: str = "ramp",
        tfinal: float = 10.0,
        dt: float = 0.01,
        title: str | None = None,
    ) -> ResponseResult:
        model = TFModel(np.asarray(num, float), np.asarray(den, float))
        T, y, U = self.engine.lsim_tf(model, u=u, tfinal=tfinal, dt=dt)
        if self.show_plots:
            plt.figure(figsize=(8.6, 4.6))
            plt.plot(T, y, label="output y(t)")
            plt.plot(T, U, ":", label=f"u(t)={u}")
            plt.title(title or f"Arbitrary input response (TF): {u}")
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude")
            plt.grid(True)
            plt.legend()
            save_plot(self.io.out_dir / f"lsim_tf_{u}.png")
        save_json(
            self.io.out_dir / f"lsim_tf_{u}.json",
            {"T": T.tolist(), "y": y.tolist(), "u": U.tolist()},
        )
        return ResponseResult(T=T, y=y, u=U)
