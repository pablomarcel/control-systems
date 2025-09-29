from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional
import numpy as np
from .utils import mk_ss, mk_tf, step_response, forced_response, time_grid

# ---------- Models ----------

@dataclass(slots=True)
class SSModel:
    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: np.ndarray

    def system(self):
        return mk_ss(self.A, self.B, self.C, self.D)


@dataclass(slots=True)
class TFModel:
    num: np.ndarray
    den: np.ndarray

    def system(self):
        return mk_tf(self.num, self.den)


# ---------- Signals ----------

class InputSignal:
    @staticmethod
    def ramp(T: np.ndarray) -> np.ndarray:
        return T.copy()

    @staticmethod
    def sine(T: np.ndarray, freq_hz: float = 0.5, phase: float = 0.0) -> np.ndarray:
        return np.sin(2 * np.pi * freq_hz * T + phase)

    @staticmethod
    def square(T: np.ndarray, freq_hz: float = 0.5) -> np.ndarray:
        try:
            from scipy.signal import square
        except Exception as e:  # pragma: no cover (optional dep)
            raise RuntimeError("scipy is required for square input.") from e
        return square(2 * np.pi * freq_hz * T)


# ---------- Engines ----------

class AugmentationEngine:
    """Implements the ramp‑via‑augmentation trick for SISO SS models.

    x_a = [x; z],  z = ∫ y dt
    A_A = [[A, 0], [C, 0]];  B_B = [[B], [D]];  C_C = [0...01];  D_D = [0]
    """

    @staticmethod
    def augment_for_ramp(A, B, C, D):
        A = np.asarray(A, float); B = np.asarray(B, float)
        C = np.asarray(C, float); D = np.asarray(D, float)
        n = A.shape[0]
        A_A = np.block([[A, np.zeros((n, 1))], [C, np.zeros((1, 1))]])
        B_B = np.vstack([B, D])
        C_C = np.hstack([np.zeros((1, n)), np.ones((1, 1))])
        D_D = np.zeros((1, 1))
        return A_A, B_B, C_C, D_D

    def unit_ramp_response(self, model: SSModel, tfinal: float, dt: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        sys_orig = model.system()
        A_A, B_B, C_C, D_D = self.augment_for_ramp(model.A, model.B, model.C, model.D)
        sys_aug = mk_ss(A_A, B_B, C_C, D_D)
        T = time_grid(tfinal, dt)
        T1, z = step_response(sys_aug, T)
        z = np.squeeze(z)
        U_ramp = InputSignal.ramp(T)
        T2, y_ramp, _ = forced_response(sys_orig, U=U_ramp, T=T)
        y_ramp = np.squeeze(y_ramp)
        return T1, z, y_ramp


class ResponseEngine:
    """High‑level façade for all response computations."""

    def ramp_ss(self, model: SSModel, *, tfinal: float = 10.0, dt: float = 0.01):
        return AugmentationEngine().unit_ramp_response(model, tfinal, dt)

    def lsim_tf(self, model: TFModel, *, u: Literal["ramp", "sine", "square"] = "ramp",
                 tfinal: float = 10.0, dt: float = 0.01):
        G = model.system()
        T = time_grid(tfinal, dt)
        if u == "ramp":
            U = InputSignal.ramp(T)
        elif u == "sine":
            U = InputSignal.sine(T)
        elif u == "square":
            U = InputSignal.square(T)
        else:
            raise ValueError(f"Unknown input '{u}'")
        T_out, y, _ = forced_response(G, U=U, T=T)
        return np.asarray(T_out), np.squeeze(y), U