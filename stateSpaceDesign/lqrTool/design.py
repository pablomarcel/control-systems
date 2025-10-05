from __future__ import annotations
from dataclasses import dataclass
from typing import Union
import numpy as np
import control as ct
from .core import StateSpaceModel, LQRDesignResult

QType = Union[float, np.ndarray]
RType = Union[float, np.ndarray]

@dataclass
class LQRDesigner:
    model: StateSpaceModel

    def design(self, Q: QType, R: RType) -> LQRDesignResult:
        K, P, E = ct.lqr(self.model.A, self.model.B, Q, R)
        return LQRDesignResult(K=np.asarray(K), P=np.asarray(P), eig_cl=np.asarray(E))

    def prefilter(self, K: np.ndarray, mode: str, C: np.ndarray | None = None) -> float:
        mode = (mode or "none").lower()
        Ceff = C if C is not None else self.model.C
        if mode == "ogata":
            return float(K.ravel()[0])
        if mode == "dcgain":
            Acl = self.model.A - self.model.B @ K
            G0_arr = Ceff @ np.linalg.solve(Acl, self.model.B)
            g0 = np.asarray(G0_arr).reshape(()).item()
            return -1.0 / g0
        return 0.0
