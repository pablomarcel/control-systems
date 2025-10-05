from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class SystemSpec:
    A: np.ndarray
    C: np.ndarray
    B: np.ndarray | None = None  # optional

    def __post_init__(self):
        A = np.asarray(self.A)
        C = np.atleast_2d(self.C)
        if A.shape[0] != A.shape[1]:
            raise ValueError("A must be square.")
        if C.shape[0] != 1 or C.shape[1] != A.shape[0]:
            raise ValueError("C must be 1×n (p=1).")

    @property
    def n(self) -> int:
        return int(self.A.shape[0])

    def with_B(self, B: np.ndarray | None) -> "SystemSpec":
        return SystemSpec(A=self.A, C=self.C, B=B)

def transform_from_C(C: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    C = np.atleast_2d(C)
    if C.shape[0] != 1:
        raise ValueError("Only p=1 supported.")
    n = C.shape[1]
    normC = np.linalg.norm(C)
    Cn = C / (normC if normC > 0 else 1.0)
    _, _, Vh = np.linalg.svd(Cn, full_matrices=True)
    T = np.vstack([C, Vh[1:, :]])
    T = np.asarray(T, dtype=float)
    Tinv = np.linalg.inv(T)
    return np.real_if_close(T, 1e8), np.real_if_close(Tinv, 1e8)

def partition_bar(Abar: np.ndarray, Bbar: np.ndarray | None):
    n = Abar.shape[0]; r = n - 1
    Aaa = Abar[0, 0]
    Aab = Abar[0, 1:].reshape(1, r)
    Aba = Abar[1:, 0].reshape(r, 1)
    Abb = Abar[1:, 1:].reshape(r, r)
    if Bbar is None:
        return Aaa, Aab, Aba, Abb, None, None
    Bbar = np.atleast_2d(Bbar)
    Ba = Bbar[0:1, :]
    Bb = Bbar[1:, :]
    return Aaa, Aab, Aba, Abb, Ba, Bb

def poly_from_roots(roots: np.ndarray) -> np.ndarray:
    coeff = np.poly(roots)
    return np.real_if_close(coeff, 1e8).astype(float)

def phi_of_A(A: np.ndarray, coeff: np.ndarray) -> np.ndarray:
    r = len(coeff) - 1
    I = np.eye(A.shape[0])
    out = np.zeros_like(A, dtype=float)
    out += np.linalg.matrix_power(A, r)
    for k in range(1, r):
        out += coeff[k] * np.linalg.matrix_power(A, r - k)
    out += coeff[-1] * I
    return out

def build_S(Aab: np.ndarray, Abb: np.ndarray) -> np.ndarray:
    r = Abb.shape[0]
    rows = [Aab @ np.linalg.matrix_power(Abb, i) for i in range(r)]
    S = np.vstack(rows)
    return S

class MinOrderObserverDesigner:
    def __init__(self, sys: SystemSpec):
        self.sys = sys

    def compute_T(self) -> tuple[np.ndarray, np.ndarray]:
        return transform_from_C(self.sys.C)

    def compute_bar(self, T, Tinv):
        Abar = T @ self.sys.A @ Tinv
        Bbar = None if self.sys.B is None else T @ self.sys.B
        return Abar, Bbar

    def ke_acker(self, Abb: np.ndarray, Aab: np.ndarray, poles: np.ndarray, allow_pinv: bool=False) -> np.ndarray:
        r = Abb.shape[0]
        if r == 0:
            return np.zeros((0,1))
        coeff = poly_from_roots(poles)
        S = build_S(Aab, Abb)
        rankS = np.linalg.matrix_rank(S)
        if rankS < r and not allow_pinv:
            raise ValueError("Singular S: (Abb,Aab) not observable. Use a different C or --allow_pinv.")
        Sinv = np.linalg.inv(S) if rankS == r else np.linalg.pinv(S)
        er = np.zeros((r,1)); er[-1,0] = 1.0
        Ke = phi_of_A(Abb, coeff) @ Sinv @ er
        return np.real_if_close(Ke, 1e8).astype(float)

    def design(self, poles: np.ndarray, allow_pinv: bool=False):
        T, Tinv = self.compute_T()
        Abar, Bbar = self.compute_bar(T, Tinv)
        Aaa, Aab, Aba, Abb, Ba, Bb = partition_bar(Abar, Bbar)
        Ke = self.ke_acker(Abb, Aab, poles, allow_pinv=allow_pinv)
        Ahat = Abb - Ke @ Aab
        Bhat = Ahat @ Ke + Aba - Ke * Aaa
        Fhat = None
        if self.sys.B is not None and Ba is not None and Bb is not None:
            Fhat = Bb - Ke @ Ba
        Ccap = np.vstack([np.zeros((1, self.sys.n-1)), np.eye(self.sys.n-1)])
        Dcap = np.vstack([np.ones((1, 1)), Ke])
        Ctil = Tinv @ Ccap
        Dtil = Tinv @ Dcap
        return {
            "T": T, "Tinv": Tinv, "Abar": Abar, "Bbar": Bbar,
            "Aaa": Aaa, "Aab": Aab, "Aba": Aba, "Abb": Abb,
            "Ke": Ke, "Ahat": Ahat, "Bhat": Bhat, "Fhat": Fhat,
            "Ctil": Ctil, "Dtil": Dtil
        }
