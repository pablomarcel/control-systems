# rootLocus/systemResponseTool/app.py
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import numpy as np
import plotly.graph_objects as go

from .core import (
    SysSpec, Parser, TransferFunctionBuilder, SignalGenerator,
    ResponseEngine, ICMode
)
from .io import Exporter
from .utils import default_palette, make_logger, make_figure, add_trace

log = make_logger(__name__)

@dataclass(slots=True)
class SystemResponseApp:
    in_dir: Path
    out_dir: Path
    show_plots: bool = True

    # declare slotted fields so __post_init__ can assign them
    parser: Parser = field(init=False)
    tf_builder: TransferFunctionBuilder = field(init=False)
    signals: SignalGenerator = field(init=False)
    engine: ResponseEngine = field(init=False)
    export: Exporter = field(init=False)

    def __post_init__(self):
        self.in_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.parser = Parser()
        self.tf_builder = TransferFunctionBuilder()
        self.signals = SignalGenerator()
        self.engine = ResponseEngine()
        self.export = Exporter(self.out_dir)

    # -------- orchestrators --------
    def parse_systems(self, sys_args: Iterable[str]) -> List[SysSpec]:
        specs: List[SysSpec] = []
        for arg in sys_args:
            specs.append(self.parser.parse_sys_arg(arg))
        return specs

    def run_step(self, specs: List[SysSpec], T: np.ndarray,
                 title: str = "", out_prefix: Optional[str] = None) -> go.Figure:
        fig = make_figure(title or "STEP response", "Output y(t)")
        series: List[Tuple[str, np.ndarray]] = []
        palette = default_palette()

        print("\n=== Step metrics (SISO channels) ===")
        for k, spec in enumerate(specs):
            color = spec.style.color or palette[k % len(palette)]
            try:
                G = self.tf_builder.tf_for_io(spec)
                T_out, y = self.engine.step(G, T)
                y = np.squeeze(y)
                add_trace(fig, T_out, y, spec.style.name, color, spec.style.dash, spec.style.width)
                series.append((spec.style.name, y))

                info = self.engine.step_info_safe(G)
                print(f"  {spec.style.name:<16} Rise={info.get('RiseTime', float('nan')):.3g}s"
                      f"  Settling={info.get('SettlingTime', float('nan')):.3g}s"
                      f"  Overshoot={info.get('Overshoot', float('nan')):.3g}%")
            except Exception as e:  # pragma: no cover (visual)
                log.error("[step] %s: %s", spec.style.name, e)

        if self.show_plots:
            fig.show()
        if out_prefix:
            self.export.save_csv(f"{out_prefix}_step.csv", T, series)
            self.export.save_html(fig, f"{out_prefix}_step.html")
        return fig

    def run_impulse(self, specs: List[SysSpec], T: np.ndarray,
                    title: str = "", out_prefix: Optional[str] = None) -> go.Figure:
        fig = make_figure(title or "IMPULSE response", "Output y(t)")
        series: List[Tuple[str, np.ndarray]] = []
        palette = default_palette()

        for k, spec in enumerate(specs):
            color = spec.style.color or palette[k % len(palette)]
            try:
                G = self.tf_builder.tf_for_io(spec)
                T_out, y = self.engine.impulse(G, T)
                y = np.squeeze(y)
                add_trace(fig, T_out, y, spec.style.name, color, spec.style.dash, spec.style.width)
                series.append((spec.style.name, y))
            except Exception as e:
                log.error("[impulse] %s: %s", spec.style.name, e)

        if self.show_plots:
            fig.show()
        if out_prefix:
            self.export.save_csv(f"{out_prefix}_impulse.csv", T, series)
            self.export.save_html(fig, f"{out_prefix}_impulse.html")
        return fig

    def run_ramp(self, specs: List[SysSpec], T: np.ndarray, *,
                 title: str = "", out_prefix: Optional[str] = None,
                 show_input: bool = False) -> go.Figure:
        fig = make_figure(title or "RAMP response", "Output y(t)")
        series: List[Tuple[str, np.ndarray]] = []
        palette = default_palette()

        U, _ = self.signals.ramp(T)

        for k, spec in enumerate(specs):
            color = spec.style.color or palette[k % len(palette)]
            try:
                G = self.tf_builder.tf_for_io(spec)
                T_out, y, _ = self.engine.forced(G, U, T)
                y = np.squeeze(y)
                add_trace(fig, T_out, y, spec.style.name, color, spec.style.dash, spec.style.width)
                series.append((spec.style.name, y))
            except Exception as e:
                log.error("[ramp] %s: %s", spec.style.name, e)

        if show_input:
            fig.add_trace(dict(
                type="scatter", mode="lines", x=T, y=U, name="input u(t)=t",
                line=dict(color="rgba(0,0,0,0.5)", dash="dot", width=2)
            ))

        if self.show_plots:
            fig.show()
        if out_prefix:
            self.export.save_csv(f"{out_prefix}_ramp.csv", T, series)
            self.export.save_html(fig, f"{out_prefix}_ramp.html")
        return fig

    def run_arb(self, specs: List[SysSpec], T: np.ndarray, *,
                kind: str, amp: float, freq: float, duty: float,
                expr: str, file_path: str, show_input: bool,
                title: str = "", out_prefix: Optional[str] = None) -> go.Figure:
        fig = make_figure(title or "ARBITRARY response", "Output y(t)")
        series: List[Tuple[str, np.ndarray]] = []
        palette = default_palette()

        # resolve file path inside in_dir when kind=file and relative path given
        if kind == "file" and file_path and not Path(file_path).is_absolute():
            file_path = str(self.in_dir / file_path)

        U, label = self.signals.arb(kind, T, amp, freq, duty, expr, file_path)

        for k, spec in enumerate(specs):
            color = spec.style.color or palette[k % len(palette)]
            try:
                G = self.tf_builder.tf_for_io(spec)
                T_out, y, _ = self.engine.forced(G, U, T)
                y = np.squeeze(y)
                add_trace(fig, T_out, y, spec.style.name, color, spec.style.dash, spec.style.width)
                series.append((spec.style.name, y))
            except Exception as e:
                log.error("[arb] %s: %s", spec.style.name, e)

        if show_input:
            fig.add_trace(dict(
                type="scatter", mode="lines", x=T, y=U, name="input u(t)",
                line=dict(color="rgba(0,0,0,0.5)", dash="dot", width=2)
            ))

        fig.update_layout(title=title or f"ARBITRARY response — {label}")
        if self.show_plots:
            fig.show()
        if out_prefix:
            self.export.save_csv(f"{out_prefix}_arb.csv", T, series)
            self.export.save_html(fig, f"{out_prefix}_arb.html")
        return fig

    def run_ic(self, specs: List[SysSpec], T: np.ndarray, *,
               which: ICMode, compare: bool,
               title: str = "", out_prefix: Optional[str] = None) -> go.Figure:
        from .core import ICMode as _IC  # avoid circular import name resolution issues
        assert which in (_IC.IC1, _IC.IC2)
        ylab = "States x_i(t)" if which is _IC.IC1 else "Outputs y_j(t)"
        ttl = ("Case 1 — states from initial condition"
               if which is _IC.IC1 else "Case 2 — outputs from initial condition")
        if compare:
            ttl += " (direct vs step-equivalent)"
        fig = make_figure(title or ttl, ylab)
        series: List[Tuple[str, np.ndarray]] = []
        palette = default_palette()

        for k, spec in enumerate(specs):
            if spec.kind != "ss":
                log.error("[ic] System '%s' must be state-space (ss).", spec.style.name)
                continue
            if spec.x0 is None:
                log.error("[ic] System '%s' requires x0=...", spec.style.name)
                continue

            color = spec.style.color or palette[k % len(palette)]
            x0 = np.asarray(spec.x0).ravel()
            n = spec.A.shape[0]
            if x0.size != n:
                log.error("[ic] '%s': x0 length %d must match A dimension %d",
                          spec.style.name, x0.size, n)
                continue

            if which is _IC.IC1:
                Xd = self.engine.ic_case1_direct(spec.A, x0, T)
                for i in range(Xd.shape[0]):
                    name = f"{spec.style.name}: x{i+1}"
                    add_trace(fig, T, Xd[i, :], name, color, spec.style.dash, spec.style.width)
                    series.append((name, Xd[i, :]))
                if compare:
                    Xs = self.engine.ic_case1_step_equiv(spec.A, x0, T)
                    for i in range(Xs.shape[0]):
                        name = f"{spec.style.name}: x{i+1} (step-eq.)"
                        add_trace(fig, T, Xs[i, :], name, color, "dot",
                                  max(2.0, 0.8 * spec.style.width))
                        series.append((name, Xs[i, :]))
            else:
                outs = (spec.outs_sel if spec.outs_sel is not None else [spec.out_idx])
                C_sel = spec.C[outs, :] if len(outs) > 1 else spec.C[[outs[0]], :]
                Yd = self.engine.ic_case2_direct(spec.A, C_sel, x0, T)
                for r, j in enumerate(outs):
                    name = f"{spec.style.name}: y{j+1}"
                    add_trace(fig, T, Yd[r, :], name, color, spec.style.dash, spec.style.width)
                    series.append((name, Yd[r, :]))
                if compare:
                    Ys = self.engine.ic_case2_step_equiv(spec.A, C_sel, x0, T)
                    for r, j in enumerate(outs):
                        name = f"{spec.style.name}: y{j+1} (step-eq.)"
                        add_trace(fig, T, Ys[r, :], name, color, "dot",
                                  max(2.0, 0.8 * spec.style.width))
                        series.append((name, Ys[r, :]))

        if self.show_plots:
            fig.show()
        if out_prefix:
            tag = ("ic1" if which is _IC.IC1 else "ic2") + ("_compare" if compare else "")
            self.export.save_csv(f"{out_prefix}_{tag}.csv", T, series)
            self.export.save_html(fig, f"{out_prefix}_{tag}.html")
        return fig
