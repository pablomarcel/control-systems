"""
Core OOP classes for MIMO analysis.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np
import matplotlib.pyplot as plt
import control as ct

from .utils import get_poles, coerce_outputs_m_by_N, get_logger

log = get_logger(__name__)

@dataclass
class MIMOSystem:
    """
    A thin OOP wrapper around a python-control StateSpace system.
    Provides convenience methods that are easy to unit test.
    """
    sys: ct.StateSpace

    @property
    def ninputs(self) -> int:
        return self.sys.ninputs

    @property
    def noutputs(self) -> int:
        return self.sys.noutputs

    @property
    def A(self):
        return self.sys.A

    @property
    def B(self):
        return self.sys.B

    @property
    def C(self):
        return self.sys.C

    @property
    def D(self):
        return self.sys.D

    def poles(self) -> np.ndarray:
        p = get_poles(self.sys)
        log.debug(f"Poles: {p}")
        return p

    def step_response_per_input(
        self, tfinal: float = 100.0, dt: float = 0.1, input_index: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute step response either for a specific input or for the default
        (let python-control choose). Returns (T, Y) with Y shaped (m, N).
        """
        T = np.arange(0.0, tfinal + dt, dt)
        if input_index is None:
            T_out, Y = ct.step_response(self.sys, T=T)
        else:
            T_out, Y = ct.step_response(self.sys, T=T, input=input_index)
        Y2 = coerce_outputs_m_by_N(Y, N_time=T_out.size)
        return T_out, Y2

    def sigma_over_frequency(self, w: np.ndarray) -> np.ndarray:
        """
        Compute singular values of G(jw). Returns (r, len(w)).
        """
        r = min(self.noutputs, self.ninputs)
        sv = np.zeros((r, len(w)))
        for i, wi in enumerate(w):
            G = ct.evalfr(self.sys, 1j * wi)
            s = np.linalg.svd(G, compute_uv=False)
            sv[:len(s), i] = s
        return sv

    # ---------------------
    # Plotting wrappers
    # ---------------------
    def plot_steps_for_each_input(self, tfinal=100.0, dt=0.1, title_prefix="Step"):
        T = np.arange(0.0, tfinal + dt, dt)
        for u in range(self.ninputs):
            T_out, Y = ct.step_response(self.sys, T=T, input=u)
            Y = coerce_outputs_m_by_N(Y, N_time=T_out.size)

            plt.figure()
            for k in range(Y.shape[0]):
                plt.plot(T_out, Y[k, :], label=f"y{k+1}")
            plt.grid(True)
            plt.xlabel("Time (s)")
            plt.ylabel("Output")
            plt.title(f"{title_prefix}: unit step on input u{u+1}")
            plt.legend()
            plt.tight_layout()

    def plot_sigma(self, title="σ(G(jω))"):
        w = np.logspace(-3, 1.5, 400)
        sv = self.sigma_over_frequency(w)

        plt.figure()
        for i in range(sv.shape[0]):
            plt.semilogx(w, 20.0 * np.log10(np.maximum(sv[i, :], 1e-16)), label=f"σ{i+1}")
        plt.grid(True, which="both")
        plt.xlabel("ω [rad/s]")
        plt.ylabel("Magnitude [dB]")
        plt.title(title)
        plt.legend()
        plt.tight_layout()
