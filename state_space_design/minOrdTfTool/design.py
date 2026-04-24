
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Any, Dict
import numpy as np
from numpy.linalg import inv, matrix_rank, eigvals
from scipy import signal

try:
    import control as ct
    HAS_CTRL = True
except Exception:
    HAS_CTRL = False

from .utils import poly_from_roots, phi_of_A, build_S, parse_cplx_tokens

@dataclass(frozen=True)
class ObserverBlocks:
    Ahat: np.ndarray
    Bhat: np.ndarray
    Fhat: np.ndarray

@dataclass(frozen=True)
class ControllerRealization:
    Atil: np.ndarray
    Btil: np.ndarray
    Ctil: np.ndarray
    Dtil: np.ndarray

@dataclass(frozen=True)
class ControllerTF:
    num: np.ndarray
    den: np.ndarray

class MinOrderObserverDesigner:
    def __init__(self, A: np.ndarray, B: np.ndarray, C: np.ndarray):
        self.A = np.asarray(A, float)
        self.B = np.asarray(B, float)
        self.C = np.asarray(C, float).reshape(1, -1)
        if self.A.shape[0] != self.A.shape[1]:
            raise ValueError("A must be square.")
        if self.C.shape[1] != self.A.shape[1] or self.C.shape[0] != 1:
            raise ValueError("C must be 1×n (p=1) for this tool.")
        if self.B.shape[0] != self.A.shape[0]:
            raise ValueError("B must have n rows.")
        self.n = self.A.shape[0]
        self.r = self.n - 1
        self.m = self.B.shape[1]
        if self.m != 1:
            raise ValueError("Only single-input plants are supported for min-order controller (m=1).")

    def transform_from_C(self) -> tuple[np.ndarray, np.ndarray]:
        C = self.C
        normC = np.linalg.norm(C)
        Cn = C / (normC if normC > 0 else 1.0)
        _, _, Vh = np.linalg.svd(Cn, full_matrices=True)
        T = np.vstack([C, Vh[1:, :]]).astype(float)
        Tinv = inv(T)
        return np.real_if_close(T, 1e8), np.real_if_close(Tinv, 1e8)

    @staticmethod
    def partition_bar(Abar: np.ndarray, Bbar: Optional[np.ndarray] = None):
        n = Abar.shape[0]
        Aaa = float(Abar[0, 0])
        Aab = Abar[0:1, 1:]
        Aba = Abar[1:, 0:1]
        Abb = Abar[1:, 1:]
        if Bbar is None:
            return Aaa, Aab, Aba, Abb, None, None
        Ba = Bbar[0:1, :]
        Bb = Bbar[1:, :]
        return Aaa, Aab, Aba, Abb, Ba, Bb

    def compute_Ke(self, Abb: np.ndarray, Aab: np.ndarray, obs_poles: np.ndarray, allow_pinv: bool=False) -> np.ndarray:
        r = Abb.shape[0]
        if r == 0:
            return np.zeros((0, 1))
        coeff = poly_from_roots(obs_poles)
        S = build_S(Aab, Abb)
        rankS = matrix_rank(S)
        if rankS < r and not allow_pinv:
            raise ValueError("Singular S (rank < r). (Abb,Aab) not observable.")
        Sinv = np.linalg.inv(S) if rankS == r else np.linalg.pinv(S)
        er = np.zeros((r,1)); er[-1,0] = 1.0
        Ke = phi_of_A(Abb, coeff) @ Sinv @ er
        return np.real_if_close(Ke, 1e8).astype(float)

    def build_observer_blocks(self, Aaa, Aab, Aba, Abb, Ba, Bb, Ke) -> ObserverBlocks:
        Ahat = Abb - Ke @ Aab
        Bhat = Ahat @ Ke + Aba - Ke * Aaa
        Fhat = Bb - Ke @ Ba
        return ObserverBlocks(np.asarray(Ahat, float), np.asarray(Bhat, float), np.asarray(Fhat, float))

    def design_K(self, K_row: np.ndarray | None, K_poles: np.ndarray | None):
        if K_row is not None:
            K = np.atleast_2d(np.asarray(K_row, float))
            if K.shape != (1, self.n):
                raise ValueError(f"--K must be 1×{self.n}.")
            return K
        if K_poles is None:
            raise ValueError("Provide --K or --K_poles.")
        if not HAS_CTRL:
            raise RuntimeError("python-control is required for --K_poles.")
        K = np.real_if_close(ct.acker(self.A, self.B, K_poles), 1e8).astype(float)
        return np.atleast_2d(K)

    def realize_controller(self, Tinv: np.ndarray, obs_blocks: ObserverBlocks, K: np.ndarray, Ke: np.ndarray | None = None) -> Tuple[ControllerRealization, ControllerTF, Dict[str, Any]]:
        Ahat, Bhat, Fhat = obs_blocks.Ahat, obs_blocks.Bhat, obs_blocks.Fhat
        Kbar = (K @ Tinv).astype(float)
        if Kbar.ndim == 1:
            Kbar = Kbar.reshape(1, -1)
        Ka = float(Kbar[0, 0])
        Kb = Kbar[0:1, 1:]
        alpha = float(Ka + (Kb @ Ke).ravel()[0]) if Ke is not None else float(Ka)

        Atil = Ahat - Fhat @ Kb          # r×r
        Btil = Bhat - Fhat * alpha       # r×1
        Ctil = -Kb                       # 1×r
        Dtil = -np.array([[alpha]], dtype=float)  # 1×1

        num, den = signal.ss2tf(np.asarray(Atil, float),
                                np.asarray(Btil, float),
                                np.asarray(Ctil, float),
                                np.asarray(Dtil, float))
        num = (-np.asarray(num[0], float))
        den = np.asarray(den, float)

        diag = {"Kbar": Kbar.tolist(), "Ka": Ka, "Kb": Kb.tolist(), "alpha": alpha}
        return (ControllerRealization(Atil, Btil, Ctil, Dtil), ControllerTF(num, den), diag)

    def full_design(self, obs_poles: np.ndarray, K_row: np.ndarray | None = None,
                    K_poles_tokens: list[str] | None = None, allow_pinv: bool=False):
        T, Tinv = self.transform_from_C()
        Abar = T @ self.A @ Tinv
        Bbar = T @ self.B
        Aaa, Aab, Aba, Abb, Ba, Bb = self.partition_bar(Abar, Bbar)

        Ke = self.compute_Ke(Abb, Aab, obs_poles, allow_pinv=allow_pinv)
        ob = self.build_observer_blocks(Aaa, Aab, Aba, Abb, Ba, Bb, Ke)

        K_poles = None
        if K_row is None and K_poles_tokens:
            K_poles = parse_cplx_tokens(K_poles_tokens)
            if K_poles.size != self.n:
                raise ValueError(f"--K_poles needs n={self.n} poles.")
        K = self.design_K(K_row, K_poles)

        realization, tf, diag = self.realize_controller(Tinv, ob, K, Ke)

        eigAhat = np.real_if_close(eigvals(ob.Ahat), 1e8)
        coeffAhat = poly_from_roots(eigAhat)

        payload = {
            "A": self.A.tolist(), "B": self.B.tolist(), "C": self.C.tolist(),
            "T": np.asarray(T, float).tolist(), "Tinv": np.asarray(Tinv, float).tolist(),
            "Abar": np.asarray(Abar, float).tolist(), "Bbar": np.asarray(Bbar, float).tolist(),
            "Ahat": np.asarray(ob.Ahat, float).tolist(), "Bhat": np.asarray(ob.Bhat, float).tolist(),
            "Fhat": np.asarray(ob.Fhat, float).tolist(), "Ke": np.asarray(Ke, float).tolist(),
            "K": np.asarray(K, float).tolist(), "Kbar": diag["Kbar"], "Ka": diag["Ka"], "Kb": diag["Kb"], "alpha": diag["alpha"],
            "Atil": np.asarray(realization.Atil, float).tolist(), "Btil": np.asarray(realization.Btil, float).tolist(),
            "Ctil": np.asarray(realization.Ctil, float).tolist(), "Dtil": np.asarray(realization.Dtil, float).tolist(),
            "tf_num": np.asarray(tf.num, float).tolist(), "tf_den": np.asarray(tf.den, float).tolist(),
            "eig_Ahat": [[float(np.real(z)), float(np.imag(z))] for z in eigAhat],
            "charpoly_Ahat": np.asarray(coeffAhat, float).tolist(),
        }
        return realization, tf, payload
