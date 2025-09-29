# ---------------------------------
# File: transientAnalysis/icTool/app.py
# ---------------------------------
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from .core import ICProblem, ICSolver
from .utils import ensure_dir
from .io import dump_json  # <- use existing dumper
from .tfcore import TfProblem, TfSolver  # NEW: TF path
try:
    from .tools.analytic import analytic_solution  # optional overlay
except Exception:
    analytic_solution = None


@dataclass(slots=True)
class IcToolApp:
    """High-level orchestrator with conventional in/out directories."""
    in_dir: Path
    out_dir: Path

    def __init__(self, base_dir: Path | None = None) -> None:
        base = Path(base_dir) if base_dir else Path(__file__).resolve().parent
        self.in_dir = ensure_dir(base / "in")
        self.out_dir = ensure_dir(base / "out")

    # ---------- plotting helpers ----------

    def _plot_compare(self, res, title: str, save_basename: str | None = None) -> None:
        d, s = res.direct, res.step_equiv
        r = d.Y.shape[0]
        plt.figure(figsize=(8.4, 4.8))
        for i in range(r):
            plt.plot(d.T, d.Y[i, :], label=f"{d.label_rows[i]} (direct)")
            plt.plot(s.T, s.Y[i, :], "--", alpha=0.9, label=f"{s.label_rows[i]} (step-eq.)")
        plt.title(title)
        plt.xlabel("Time (s)"); plt.ylabel("Amplitude")
        plt.grid(True); plt.legend(ncol=2); plt.tight_layout()
        if save_basename:
            p = self.out_dir / f"{save_basename}.png"
            plt.savefig(p, dpi=160)
        plt.close()

    def _plot_single(self, res, title: str, save_basename: str | None = None, overlays: list[tuple[np.ndarray, np.ndarray, str, str]] | None = None) -> None:
        r = res.Y.shape[0]
        plt.figure(figsize=(8.4, 4.8))
        for i in range(r):
            plt.plot(res.T, res.Y[i, :], label=res.label_rows[i])
        if overlays:
            for T_ov, y_ov, label, style in overlays:
                plt.plot(T_ov, y_ov, style, label=label, linewidth=2.0)
        plt.title(title)
        plt.xlabel("Time (s)"); plt.ylabel("Amplitude")
        plt.grid(True); plt.legend(); plt.tight_layout()
        if save_basename:
            p = self.out_dir / f"{save_basename}.png"
            plt.savefig(p, dpi=160)
        plt.close()

    # ---------- state-space public API ----------

    def run_compare1(self, A: np.ndarray, x0: np.ndarray, T: np.ndarray, *, save: bool = False):
        res = ICSolver(ICProblem(A=A, x0=x0)).compare1(T)
        if save:
            self._plot_compare(res, "Case 1 — states (direct vs step-eq.)", "compare1")
        return res

    def run_compare2(self, A: np.ndarray, C: np.ndarray, x0: np.ndarray, T: np.ndarray, *, save: bool = False):
        res = ICSolver(ICProblem(A=A, x0=x0, C=C)).compare2(T)
        if save:
            self._plot_compare(res, "Case 2 — outputs (direct vs step-eq.)", "compare2")
        return res

    def run_case1(self, A: np.ndarray, x0: np.ndarray, T: np.ndarray, *, save: bool = False):
        res = ICSolver(ICProblem(A=A, x0=x0)).case1_direct(T)
        if save:
            self._plot_single(res, "Case 1 — states (direct)", "case1")
        return res

    def run_case2(self, A: np.ndarray, C: np.ndarray, x0: np.ndarray, T: np.ndarray, *, save: bool = False):
        res = ICSolver(ICProblem(A=A, x0=x0, C=C)).case2_direct(T)
        if save:
            self._plot_single(res, "Case 2 — outputs (direct)", "case2")
        return res

    # ---------- TF public API (NEW) ----------

    def run_tf_step_ogata(self, m: float, b: float, k: float, x0: float, v0: float, T: np.ndarray,
                          *, save: bool = False, save_json: bool = False, overlay_analytic: bool = False,
                          basename: str = "tf_step_ogata"):
        pb = TfProblem(den=np.array([m, b, k], float), m=m, b=b, k=k, x0=x0, v0=v0)
        T_out, Y = TfSolver(pb).step_equiv_output(T)
        # package as a simple struct
        class _Res: pass
        res = _Res(); res.T = T_out; res.Y = Y; res.label_rows = ("y1",)
        overlays = []
        if overlay_analytic and analytic_solution is not None:
            y_analytic = analytic_solution(T_out, m, b, k, x0, v0)
            if y_analytic is not None:
                overlays.append((T_out, y_analytic, "Analytic (Ogata)", ":"))
        if save:
            self._plot_single(res, "TF step-equivalent output (Ogata parameters)", basename, overlays=overlays)
        if save_json:
            dump_json(self.out_dir / f"{basename}.json", {"T": T_out.tolist(), "Y": Y.tolist(), "labels": ["y1"]})
        return T_out, Y

    def run_tf_step_generic(self, num_ic: np.ndarray, den: np.ndarray, T: np.ndarray,
                            *, save: bool = False, save_json: bool = False, basename: str = "tf_step"):
        pb = TfProblem(den=np.asarray(den, float), num_ic=np.asarray(num_ic, float))
        T_out, Y = TfSolver(pb).step_equiv_output(T)
        class _Res: pass
        res = _Res(); res.T = T_out; res.Y = Y; res.label_rows = ("y1",)
        if save:
            self._plot_single(res, "TF step-equivalent output (generic G_ic)", basename)
        if save_json:
            dump_json(self.out_dir / f"{basename}.json", {"T": T_out.tolist(), "Y": Y.tolist(), "labels": ["y1"]})
        return T_out, Y
