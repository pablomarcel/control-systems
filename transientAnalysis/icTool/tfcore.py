# ---------------------------------
# File: transientAnalysis/icTool/tfcore.py
# ---------------------------------
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
import numpy as np
import control as ct

from .utils import _to_2d

@dataclass(slots=True)
class TfProblem:
    """SISO transfer-function problem for step-equivalent IC outputs.

    Either provide:
    - num_ic / den: a transfer G_ic(s) whose step response equals y(t) from ICs, or
    - physical params (m,b,k,x0,v0) for the standard 2nd-order mass-spring-damper, from
      which we construct G_ic(s) automatically.
    """
    den: np.ndarray
    num_ic: np.ndarray | None = None
    # Optional convenience for Ogata Ex.5-8 form
    m: float | None = None
    b: float | None = None
    k: float | None = None
    x0: float | None = None
    v0: float | None = None

    def build_Gic(self) -> ct.TransferFunction:
        if self.num_ic is not None:
            return ct.tf(self.num_ic, self.den)
        if None in (self.m, self.b, self.k, self.x0, self.v0):
            raise ValueError("Either num_ic or (m,b,k,x0,v0) must be provided")
        m,b,k,x0,v0 = self.m, self.b, self.k, self.x0, self.v0
        # Ogata trick: X(s) = [m x0 s^2 + (m v0 + b x0) s] / (m s^2 + b s + k) * (1/s)
        # so G_ic(s) = [m x0, m v0 + b x0, 0] / [m, b, k]
        num = np.array([m*x0, m*v0 + b*x0, 0.0], float)
        den = np.array([m, b, k], float)
        return ct.tf(num, den)


class TfSolver:
    """Compute y(t) via step response of G_ic(s)."""
    def __init__(self, pb: TfProblem) -> None:
        self.pb = pb

    def step_equiv_output(self, T: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        Gic = self.pb.build_Gic()
        T_out, y = ct.step_response(Gic, T=T)
        return np.asarray(T_out, float), _to_2d(y)