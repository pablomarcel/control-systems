
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from typing import Iterable
import matplotlib.pyplot as plt

from .core import StepOut, SigmaOut

@dataclass
class PlotConfig:
    title_prefix: str = "Step"
    sigma_title: str = r"$\sigma(G(j\omega))$"
    show: bool = True

class MIMOPlotter:
    """Plotting helpers (Matplotlib)."""

    @staticmethod
    def steps_per_input(steps: Iterable[StepOut], cfg: PlotConfig) -> None:
        for u, out in enumerate(steps, start=1):
            plt.figure()
            for k in range(out.Y.shape[0]):
                plt.plot(out.T, out.Y[k, :], label=f"y{k+1}")
            plt.grid(True)
            plt.xlabel("Time (s)")
            plt.ylabel("Output")
            plt.title(f"{cfg.title_prefix}: unit step on input u{u}")
            plt.legend()
            plt.tight_layout()

        if cfg.show:
            plt.show(block=False)

    @staticmethod
    def sigma(sout: SigmaOut, cfg: PlotConfig) -> None:
        plt.figure()
        for i in range(sout.sv.shape[0]):
            plt.semilogx(sout.w, 20.0 * np.log10(np.maximum(sout.sv[i, :], 1e-16)), label=f"σ{i+1}")
        plt.grid(True, which="both")
        plt.xlabel("ω [rad/s]")
        plt.ylabel("Magnitude [dB]")
        plt.title(cfg.sigma_title)
        plt.legend()
        plt.tight_layout()

        if cfg.show:
            plt.show(block=False)
