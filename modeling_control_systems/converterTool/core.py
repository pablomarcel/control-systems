
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import control as ct

@dataclass(slots=True)
class TFModel:
    num: np.ndarray
    den: np.ndarray

    def to_ct(self) -> ct.TransferFunction:
        return ct.TransferFunction(self.num, self.den)

@dataclass(slots=True)
class SSModel:
    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: np.ndarray

    def to_ct(self) -> ct.StateSpace:
        return ct.ss(self.A, self.B, self.C, self.D)

class ConverterEngine:
    """Pure conversion and normalization logic (no plotting, no I/O)."""
    @staticmethod
    def coeffs_from_tf(G) -> tuple[np.ndarray, np.ndarray]:
        try:
            num, den = ct.tfdata(G, squeeze=True)
        except TypeError:
            num, den = ct.tfdata(G)
            def _flat(a):
                while isinstance(a, (list, tuple)) and len(a) > 0:
                    a = a[0]
                return a
            num, den = _flat(num), _flat(den)
        return np.asarray(num, float).ravel(), np.asarray(den, float).ravel()

    @staticmethod
    def normalize(num, den) -> tuple[np.ndarray, np.ndarray]:
        den = np.asarray(den, float).ravel()
        num = np.asarray(num, float).ravel()
        k = 0
        while k < len(den) and abs(den[k]) == 0:
            k += 1
        den = den[k:]
        if den.size == 0:
            raise ValueError("Denominator is all zeros.")
        lead = den[0]
        den = den / lead
        num = num / lead
        if len(num) < len(den):
            num = np.pad(num, (len(den) - len(num), 0))
        return num, den

    def tf_to_ss(self, tfm: TFModel) -> SSModel:
        G = tfm.to_ct()
        ssys = ct.tf2ss(G)
        return SSModel(ssys.A, ssys.B, ssys.C, ssys.D)

    def ss_to_tf(self, ssm: SSModel):
        n = ssm.A.shape[0]
        if ssm.A.shape[1] != n:
            raise ValueError("A must be square (n x n).")
        if ssm.B.shape[0] != n:
            raise ValueError("B must have n rows.")
        if ssm.C.shape[1] != n:
            raise ValueError("C must have n columns.")
        if ssm.D.shape[0] != ssm.C.shape[0] or ssm.D.shape[1] != ssm.B.shape[1]:
            raise ValueError("D must be (m x r) with m=C.rows and r=B.cols.")
        G = ct.ss2tf(ssm.to_ct())
        return G
