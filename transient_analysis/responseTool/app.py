# transient_analysis/responseTool/app.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from .core import (
    SSModel, TFModel, ResponseEngine, MIMOStepEngine,
    SecondOrderModel, SecondOrderEngine, SecondOrderSurfaceEngine
)
from .io import IOConfig, save_json, save_plot


@dataclass(slots=True)
class ResponseResult:
    T: np.ndarray
    y: np.ndarray
    u: np.ndarray | None = None


@dataclass(slots=True)
class ResponseToolApp:
    # If None, default to the package directory: .../transient_analysis/responseTool
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

    # ---------- Second-order (single & sweep) ----------
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

    # ---------- Second-order (2D overlays & 3D mesh) ----------
    def second_order_overlays(
        self,
        *,
        wn: float,
        zetas: list[float] | None = None,
        tfinal: float = 10.0,
        dt: float = 0.01,
        save_prefix: str = "std2_overlays",
        title_suffix: str = ""
    ) -> dict:
        """Generate 2D overlay curves for selected ζ values; save JSON and optional PNG."""
        if not zetas:
            zetas = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        eng = SecondOrderSurfaceEngine()
        T, curves = eng.overlays(float(wn), [float(z) for z in zetas], tfinal=tfinal, dt=dt)

        # Save JSON as list for portability (zeta, y[] pairs)
        payload = {
            "wn": float(wn),
            "T": T.tolist(),
            "curves": [{"zeta": float(z), "y": curves[float(z)].tolist()} for z in zetas],
        }
        save_json(self.io.out_dir / f"{save_prefix}_2D.json", payload)

        if self.show_plots:
            plt.figure(figsize=(8.5, 5.0))
            for z in sorted(zetas):
                y = curves[float(z)]
                plt.plot(T, y, label=f"ζ={z:g}")
            ttl = rf"Unit-step overlay (standard 2nd-order), $\omega_n={wn:g}$"
            if title_suffix:
                ttl += f" — {title_suffix}"
            plt.title(ttl)
            plt.xlabel("Time (s)"); plt.ylabel("y(t)")
            plt.grid(True, alpha=0.35); plt.legend(loc="best", ncol=3, fontsize=9)
            save_plot(self.io.out_dir / f"{save_prefix}_2D.png")

        return payload

    def second_order_mesh(
        self,
        *,
        wn: float,
        zeta_min: float = 0.0,
        zeta_max: float = 1.0,
        zeta_steps: int = 41,
        tfinal: float = 10.0,
        dt: float = 0.01,
        save_prefix: str = "std2_surface",
        title_suffix: str = "",
        plot_heatmap: bool = True,
        plotly: bool = False
    ) -> dict:
        """Generate a 3D mesh Z(ζ, t) of step responses; save JSON and optional PNGs."""
        eng = SecondOrderSurfaceEngine()
        zeta_grid = np.linspace(float(zeta_min), float(zeta_max), int(zeta_steps))
        T, Z = eng.mesh(float(wn), zeta_grid, tfinal=tfinal, dt=dt)

        payload = {
            "wn": float(wn),
            "T": T.tolist(),
            "zeta_grid": zeta_grid.tolist(),
            "Z": Z.tolist(),  # (Nz, Nt)
        }
        save_json(self.io.out_dir / f"{save_prefix}_3D.json", payload)

        if self.show_plots:
            # 3D wireframe
            from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
            Tm, Zm = np.meshgrid(T, zeta_grid)
            fig = plt.figure(figsize=(9, 6))
            ax = fig.add_subplot(111, projection="3d")
            ax.plot_wireframe(Tm, Zm, Z, rstride=2, cstride=4, linewidth=0.7, color="k")
            ax.set_xlabel("Time $t$ (s)")
            ax.set_ylabel(r"Damping $\zeta$")
            ax.set_zlabel("Response")
            ttl = rf"3D mesh: standard 2nd-order, $\omega_n={wn:g}$"
            if title_suffix:
                ttl += f" — {title_suffix}"
            ax.set_title(ttl)
            ax.view_init(elev=25, azim=-60)
            save_plot(self.io.out_dir / f"{save_prefix}_3D.png")

            # Optional heatmap
            if plot_heatmap:
                plt.figure(figsize=(8.5, 4.7))
                plt.imshow(Z, aspect="auto", origin="lower",
                           extent=[T[0], T[-1], zeta_grid[0], zeta_grid[-1]])
                plt.colorbar(label="Response")
                plt.xlabel("Time $t$ (s)")
                plt.ylabel(r"Damping $\zeta$")
                plt.title(rf"Heatmap $y(t,\zeta)$, $\omega_n={wn:g}$")
                save_plot(self.io.out_dir / f"{save_prefix}_heatmap.png")

            # Optional interactive surface (best-effort / optional dep)
            if plotly:
                try:
                    import plotly.graph_objects as go
                    fig = go.Figure(data=[go.Surface(x=T, y=zeta_grid, z=Z)])
                    fig.update_layout(
                        title=rf"Plotly surface: $y(t,\zeta)$, $\omega_n={wn:g}$",
                        scene=dict(xaxis_title="t (s)", yaxis_title="zeta", zaxis_title="Response"),
                        width=900, height=600,
                    )
                    # Note: we do not save this to file; it opens a browser window when supported.
                    fig.show()
                except Exception:
                    # Silent fallback if plotly isn't installed/available
                    pass

        return payload

    # ---------- Second-order (Plotly interactive surface) ----------
    def second_order_plotly_surface(
        self,
        *,
        wn: float = 1.0,
        zeta_min: float = 0.0,
        zeta_max: float = 1.0,
        zeta_steps: int = 51,
        tfinal: float = 10.0,
        dt: float = 0.01,
        overlay: list[float] | None = None,
        title: str = "",
        save_prefix: str = "plotly_surface",
        save_html: str | None = None,
        save_png: str | None = None,
    ) -> dict:
        """
        Interactive Plotly 3D surface y(t, zeta) for the standard 2nd-order system.

        - Always writes JSON snapshot: <out>/<save_prefix>_plotly3D.json
        - If save_html is given, writes interactive HTML.
        - If save_png is given, attempts PNG (requires `kaleido`).
        """
        try:
            import plotly.graph_objects as go
        except Exception as e:
            raise RuntimeError(
                "Plotly is required for the interactive surface. "
                "Install with: pip install plotly"
            ) from e

        overlay = overlay or []
        # Build grids via the existing surface engine
        eng = SecondOrderSurfaceEngine()
        zeta_grid = np.linspace(zeta_min, zeta_max, int(zeta_steps))
        T, Z = eng.mesh(wn=float(wn), zeta_grid=zeta_grid, tfinal=float(tfinal), dt=float(dt))

        # Persist a portable snapshot (handy for tests / offline viewing)
        payload = {
            "wn": float(wn),
            "T": T.tolist(),
            "zeta_grid": zeta_grid.tolist(),
            "Z": Z.tolist(),  # Z.shape = (Nz, Nt)
            "overlay": [float(z) for z in overlay],
            "title": title,
        }
        save_json(self.io.out_dir / f"{save_prefix}_plotly3D.json", payload)

        # Compose the figure
        surf = go.Surface(
            x=T, y=zeta_grid, z=Z,
            colorscale="Viridis",
            showscale=True,
            contours=dict(z=dict(show=True, usecolormap=True, project_z=True)),
            name="surface",
            hovertemplate="t=%{x:.3g}<br>ζ=%{y:.3g}<br>y=%{z:.4g}<extra></extra>",
        )
        fig = go.Figure(data=[surf])
        base_title = (
            r"Unit-step surface $y(t,\zeta)$ for "
            r"$G(s)=\frac{\omega_n^2}{s^2+2\zeta\omega_n s+\omega_n^2}$"
            f", $\\omega_n={wn:g}$"
        )
        if title:
            base_title += f" — {title}"
        fig.update_layout(
            title=base_title,
            width=950, height=650,
            scene=dict(
                xaxis_title="Time t (s)",
                yaxis_title="Damping ζ",
                zaxis_title="Response y(t)",
                camera=dict(eye=dict(x=1.75, y=2.0, z=1.25)),
            ),
            margin=dict(l=0, r=0, t=60, b=0),
            legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.5)"),
        )

        # Optional overlay traces (zeta slices)
        palette = [
            "#E45756", "#4C78A8", "#72B7B2", "#F58518",
            "#54A24B", "#B279A2", "#FF9DA6", "#9D755D"
        ]
        for k, z in enumerate(overlay):
            sys = SecondOrderSurfaceEngine.std2_tf(float(wn), float(z))
            y = eng.step_response_1d(sys, T)  # same T grid
            fig.add_trace(
                go.Scatter3d(
                    x=T, y=np.full_like(T, float(z)), z=y,
                    mode="lines",
                    line=dict(width=6, color=palette[k % len(palette)]),
                    name=f"ζ = {float(z):g}",
                    hovertemplate="t=%{x:.3g}<br>ζ=%{y:.3g}<br>y=%{z:.4g}<extra></extra>",
                )
            )

        # Save artifacts (HTML always interactive; PNG requires kaleido)
        if save_html:
            fig.write_html(str(self.io.out_dir / save_html), include_plotlyjs="cdn")
        if save_png:
            try:
                fig.write_image(str(self.io.out_dir / save_png), scale=2)
            except Exception as e:
                # don't fail the run because kaleido is optional
                print("[plotly] PNG export requires 'kaleido' (pip install -U kaleido). Skipping. Error:", e)

        return payload
