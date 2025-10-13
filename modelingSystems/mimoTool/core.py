
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
import numpy as np
import control as ct
from .utils import get_poles, coerce_outputs_m_by_N

# ---------------- Plants ----------------
class MIMOPlantBuilder:
    """Factory for small educational MIMO plants."""

    @staticmethod
    def two_tank() -> ct.StateSpace:
        A1, A2 = 0.05, 0.04
        k1, k2 = 0.0015, 0.0012
        kc = 0.0008
        A = np.array([
            [-(k1 + kc)/A1,  kc/A1],
            [ kc/A2,        -(k2 + kc)/A2]
        ])
        B = np.array([
            [1.0/A1, 0.0],
            [0.0,    1.0/A2]
        ])
        C = np.eye(2)
        D = np.zeros((2, 2))
        return ct.ss(A, B, C, D)

    @staticmethod
    def two_zone_thermal() -> ct.StateSpace:
        C1, C2 = 800.0, 600.0
        ka1, ka2 = 10.0, 8.0
        kc = 6.0
        A = np.array([
            [-(ka1 + kc)/C1,  kc/C1],
            [ kc/C2,         -(ka2 + kc)/C2]
        ])
        B = np.array([
            [1.0/C1, 0.0],
            [0.0,    1.0/C2]
        ])
        C = np.eye(2)
        D = np.zeros((2, 2))
        return ct.ss(A, B, C, D)

# ------------- Analysis -----------------
@dataclass(frozen=True)
class StepOut:
    T: np.ndarray
    Y: np.ndarray  # shape (m, N)

@dataclass(frozen=True)
class SigmaOut:
    w: np.ndarray
    sv: np.ndarray  # shape (r, len(w))

class MIMOAnalyzer:
    """Numerical analyses for MIMO LTI systems."""

    @staticmethod
    def poles(sys: ct.StateSpace) -> np.ndarray:
        return get_poles(sys)

    @staticmethod
    def step_for_each_input(sys: ct.StateSpace, tfinal: float, dt: float) -> Tuple[StepOut, ...]:
        T = np.arange(0.0, tfinal + dt, dt)
        outs = []
        for u in range(sys.ninputs):
            T_out, Y = ct.step_response(sys, T=T, input=u)
            Y = coerce_outputs_m_by_N(Y, N_time=T_out.size)
            outs.append(StepOut(T_out, Y))
        return tuple(outs)

    @staticmethod
    def sigma_over_frequency(sys: ct.StateSpace, w: np.ndarray) -> SigmaOut:
        r = min(sys.noutputs, sys.ninputs)
        sv = np.zeros((r, len(w)))
        for i, wi in enumerate(w):
            G = ct.evalfr(sys, 1j * wi)
            s = np.linalg.svd(G, compute_uv=False)
            sv[:len(s), i] = s
        return SigmaOut(w=w, sv=sv)
