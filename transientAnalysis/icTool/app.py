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


@dataclass(slots=True)
class IcToolApp:
    """High-level orchestrator with conventional in/out directories.

    Parameters
    ----------
    in_dir : Path
        Directory for optional input files (not required for CLI).
    out_dir : Path
        Directory for outputs (plots, JSON dumps, etc.).
    """
    in_dir: Path
    out_dir: Path

    def __init__(self, base_dir: Path | None = None) -> None:
        base = Path(base_dir) if base_dir else Path(__file__).resolve().parent
        self.in_dir = ensure_dir(base / "in")
        self.out_dir = ensure_dir(base / "out")

    # ------------- Run helpers ------------- #
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

    def _plot_single(self, res, title: str, save_basename: str | None = None) -> None:
        r = res.Y.shape[0]
        plt.figure(figsize=(8.4, 4.8))
        for i in range(r):
            plt.plot(res.T, res.Y[i, :], label=res.label_rows[i])
        plt.title(title)
        plt.xlabel("Time (s)"); plt.ylabel("Amplitude")
        plt.grid(True); plt.legend(); plt.tight_layout()
        if save_basename:
            p = self.out_dir / f"{save_basename}.png"
            plt.savefig(p, dpi=160)
        plt.close()

    # Public orchestration API
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