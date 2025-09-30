# transientAnalysis/responseTool/app.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from .core import (
    SSModel, TFModel, ResponseEngine, MIMOStepEngine,
    SecondOrderModel, SecondOrderEngine
)
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

    io: IOConfig = field(init=False)
    engine: ResponseEngine = field(init=False)

    def __post_init__(self):
        if self.root is None:
            self.root = Path(__file__).resolve().parent
        self.io = IOConfig(self.root / "in", self.root / "out").ensure()
        self.engine = ResponseEngine()

    # ---------- SS ramp via augmentation (SISO) ----------
    def compute_unit_ramp_ss(
        self, A, B, C, D, *, tfinal: float = 10.0, dt: float = 0.01, title_suffix: str = ""
    ) -> ResponseResult:
        model = SSModel(np.asarray(A, float), np.asarray(B, float),
                        np.asarray(C, float), np.asarray(D, float))
        T, z, y_ramp = self.engine.ramp_ss(model, tfinal=tfinal, dt=dt)
        if self.show_plots:
            plt.figure(figsize=(8.6, 4.6))
            plt.plot(T, z, label="augmented step → z(t)")
            plt.plot(T, y_ramp, "--", label="direct ramp → y(t)")
            plt.plot(T, T, ":", label="u(t)=t")
            plt.title(f"Unit-ramp via augmentation vs direct (SS){title_suffix}")
            plt.xlabel("Time (s)"); plt.ylabel("Amplitude"); plt.grid(True); plt.legend()
            save_plot(self.io.out_dir / "ramp_ss.png")
        save_json(self.io.out_dir / "ramp_ss.json",
                  {"T": T.tolist(), "z": z.tolist(), "y_ramp": y_ramp.tolist()})
        return ResponseResult(T=T, y=y_ramp, u=T)

    # ---------- TF arbitrary input (SISO) ----------
    def simulate_tf_input(
        self, num, den, *, u: str = "ramp", tfinal: float = 10.0, dt: float = 0.01, title: str | None = None
    ) -> ResponseResult:
        model = TFModel(np.asarray(num, float), np.asarray(den, float))
        T, y, U = self.engine.lsim_tf(model, u=u, tfinal=tfinal, dt=dt)
        if self.show_plots:
            plt.figure(figsize=(8.6, 4.6))
            plt.plot(T, y, label="output y(t)")
            plt.plot(T, U, ":", label=f"u(t)={u}")
            plt.title(title or f"Arbitrary input response (TF): {u}")
            plt.xlabel("Time (s)"); plt.ylabel("Amplitude"); plt.grid(True); plt.legend()
            save_plot(self.io.out_dir / f"lsim_tf_{u}.png")
        save_json(self.io.out_dir / f"lsim_tf_{u}.json",
                  {"T": T.tolist(), "y": y.tolist(), "u": U.tolist()})
        return ResponseResult(T=T, y=y, u=U)

    # ---------- MIMO step on SS ----------
    def step_ss_from_input(
        self, A, B, C, D, *, input_index: int, tfinal: float = 10.0, dt: float = 0.01,
        title: str | None = None, save_prefix: str = "ex5_3_from_u"
    ) -> ResponseResult:
        model = SSModel(np.asarray(A, float), np.asarray(B, float),
                        np.asarray(C, float), np.asarray(D, float))
        T, Y = MIMOStepEngine.step_from_input(model, input_index=input_index, tfinal=tfinal, dt=dt)
        save_json(self.io.out_dir / f"{save_prefix}{input_index+1}.json",
                  {"T": T.tolist(), "Y": Y.tolist(), "input_index": int(input_index)})
        if self.show_plots:
            plt.figure(figsize=(8.0, 4.6))
            for k in range(Y.shape[0]):
                plt.plot(T, Y[k, :], label=f"Y{k+1}")
            plt.title(title or f"Step: input u{input_index+1}")
            plt.xlabel("Time (s)"); plt.ylabel("Amplitude"); plt.grid(True); plt.legend()
            save_plot(self.io.out_dir / f"{save_prefix}{input_index+1}.png")
        return ResponseResult(T=T, y=Y[0, :], u=None)

    def step_ss_states(
        self, A, B, C, D, *, input_index: int, tfinal: float = 10.0, dt: float = 0.01,
        save_name: str = "ex5_3_states_u"
    ) -> ResponseResult:
        model = SSModel(np.asarray(A, float), np.asarray(B, float),
                        np.asarray(C, float), np.asarray(D, float))
        T, Y, X = MIMOStepEngine.forced_step_states(model, input_index=input_index, tfinal=tfinal, dt=dt)
        save_json(self.io.out_dir / f"{save_name}{input_index+1}.json",
                  {"T": T.tolist(),
                   "Y": (Y.tolist() if Y is not None else None),
                   "X": (X.tolist() if X is not None else None),
                   "input_index": int(input_index)})
        if self.show_plots and X is not None:
            plt.figure(figsize=(8.0, 4.6))
            for k in range(X.shape[0]):
                plt.plot(T, X[k, :], label=f"x{k+1}")
            plt.title(f"States: step on u{input_index+1}")
            plt.xlabel("Time (s)"); plt.ylabel("State"); plt.grid(True); plt.legend()
            save_plot(self.io.out_dir / f"{save_name}{input_index+1}.png")
        y0 = (Y[0, :] if Y is not None else np.zeros_like(T))
        return ResponseResult(T=T, y=y0, u=None)

    def ss_step_metrics(self, A, B, C, D) -> dict:
        model = SSModel(np.asarray(A, float), np.asarray(B, float),
                        np.asarray(C, float), np.asarray(D, float))
        G = MIMOStepEngine.ss2tf_matrix(model)
        metrics = MIMOStepEngine.step_metrics(G)
        save_json(self.io.out_dir / "ex5_3_step_metrics.json", metrics)
        return metrics

    # ---------- Second-order (new) ----------
    def second_order_single(
        self,
        *,
        wn: float | None = None,
        zeta: float | None = None,
        K: float | None = None,
        coeffs: tuple[float, float, float, float] | None = None,
        tfinal: float | None = None,
        dt: float = 1e-3,
        save_prefix: str = "second_order",
    ) -> ResponseResult:
        """Single step response + metrics. Either (wn,zeta[,K]) or coeffs=(K,a2,a1,a0)."""
        if coeffs is not None:
            Kc, a2, a1, a0 = [float(x) for x in coeffs]
            wn2, zeta2, K_eq = SecondOrderEngine.infer_from_coeffs(Kc, a2, a1, a0)
            model = SecondOrderModel(wn=wn2, zeta=zeta2, K=K_eq)
        else:
            if wn is None or zeta is None:
                raise ValueError("Provide (wn, zeta[, K]) or coeffs=(K,a2,a1,a0).")
            model = SecondOrderModel(wn=float(wn), zeta=float(zeta), K=(None if K is None else float(K)))

        t = SecondOrderEngine.auto_time(model.wn, model.zeta, tfinal, dt)
        T, y = SecondOrderEngine.step(model, t)

        # Metrics (analytic + measured)
        am = SecondOrderEngine.analytic_metrics(model.wn, model.zeta)
        mm = SecondOrderEngine.measure_step(T, y)

        payload = {
            "params": {"wn": model.wn, "zeta": model.zeta, "K": (model.K if model.K is not None else model.wn**2)},
            "T": T.tolist(),
            "y": y.tolist(),
            "analytic": am,
            "measured": mm,
            "class": SecondOrderEngine.classify(model.zeta),
        }
        save_json(self.io.out_dir / f"{save_prefix}_single.json", payload)

        if self.show_plots:
            plt.figure(figsize=(8.0, 4.6))
            plt.plot(T, y, label="step response")
            plt.title(f"2nd-order step: wn={model.wn:g}, zeta={model.zeta:g}")
            plt.xlabel("Time (s)"); plt.ylabel("y(t)"); plt.grid(True); plt.legend()
            save_plot(self.io.out_dir / f"{save_prefix}_single.png")

        return ResponseResult(T=T, y=y, u=None)

    def second_order_sweep(
        self,
        *,
        wn: float,
        zetas: list[float],
        tfinal: float | None = None,
        dt: float = 1e-3,
        save_prefix: str = "second_order",
    ) -> dict:
        """Zeta sweep step responses (stores all curves)."""
        t = SecondOrderEngine.auto_time(float(wn), float(zetas[0]) if zetas else 0.4, tfinal, dt)
        data = SecondOrderEngine.sweep_zeta(float(wn), [float(z) for z in zetas], t)
        save_json(self.io.out_dir / f"{save_prefix}_sweep.json", data)

        if self.show_plots:
            plt.figure(figsize=(8.0, 4.6))
            for c in data["curves"]:
                plt.plot(data["T"], c["y"], label=f"ζ={c['zeta']:.2f}")
            plt.title(f"2nd-order sweep: wn={wn:g}")
            plt.xlabel("Time (s)"); plt.ylabel("y(t)"); plt.grid(True); plt.legend()
            save_plot(self.io.out_dir / f"{save_prefix}_sweep.png")

        return data
