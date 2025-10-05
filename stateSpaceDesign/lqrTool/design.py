from __future__ import annotations
from dataclasses import dataclass
from typing import Union
import numpy as np
import control as ct
from .core import StateSpaceModel, LQRDesignResult

QType = Union[float, np.ndarray]
RType = Union[float, np.ndarray]

def _validate_R_shape(R, m: int):
    if np.isscalar(R):
        return
    R_arr = np.asarray(R)
    if R_arr.ndim != 2 or R_arr.shape != (m, m):
        raise ValueError(f"R shape mismatch: expected ({m},{m}) for {m} input(s) but got {R_arr.shape}. "
                         f"Use a scalar (e.g., '1') for SISO or an ({m},{m}) matrix for MIMO.")

@dataclass
class LQRDesigner:
    model: StateSpaceModel

    def design(self, Q: QType, R: RType) -> LQRDesignResult:
        _validate_R_shape(R, self.model.m)
        K, P, E = ct.lqr(self.model.A, self.model.B, Q, R)
        return LQRDesignResult(K=np.asarray(K), P=np.asarray(P), eig_cl=np.asarray(E))

    def prefilter(self, K: np.ndarray, mode: str, C: np.ndarray | None = None, eps: float = 1e-9) -> float:
        mode = (mode or "none").lower()
        Ceff = C if C is not None else self.model.C
        if mode == "ogata":
            return float(K.ravel()[0])
        if mode == "dcgain":
            Acl = self.model.A - self.model.B @ K
            try:
                G0_arr = Ceff @ np.linalg.solve(Acl, self.model.B)
            except np.linalg.LinAlgError:
                print("WARN: Acl is singular during prefilter computation; using N=0.")
                return 0.0
            G0 = np.asarray(G0_arr)
            if G0.size == 1:
                g0 = float(G0.reshape(()))
                if abs(g0) < eps:
                    print("WARN: DC gain ~ 0; using N=0 to avoid division by zero.")
                    return 0.0
                return -1.0 / g0
            else:
                G0H = G0.conj().T
                denom = float(np.trace(G0H @ G0).real)
                if denom < eps:
                    print("WARN: DC gain matrix near zero; using N=0.")
                    return 0.0
                num = float(np.trace(G0H).real)
                return - num / denom
        return 0.0
