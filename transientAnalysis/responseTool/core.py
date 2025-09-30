# transientAnalysis/responseTool/core.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional, Tuple, Dict, Any
import numpy as np
import control as ct

from .utils import (
    mk_ss,
    mk_tf,
    step_response,        # version-safe for SISO/augmentation paths
    forced_response,      # version-safe for SISO/TF lsim paths
    time_grid,
    _unpack_step_result,  # used for MIMO step engine (after calling control.* directly)
    _unpack_forced_result # used for MIMO step engine (after calling control.* directly)
)

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


# ---------- Engines (SISO ramp + TF lsim) ----------

class AugmentationEngine:
    """Implements the ramp-via-augmentation trick for SISO SS models.

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

    def unit_ramp_response(
        self, model: SSModel, tfinal: float, dt: float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        sys_orig = model.system()
        A_A, B_B, C_C, D_D = self.augment_for_ramp(model.A, model.B, model.C, model.D)
        sys_aug = mk_ss(A_A, B_B, C_C, D_D)
        T = time_grid(tfinal, dt)
        T1, z = step_response(sys_aug, T)          # safe wrapper
        z = np.squeeze(z)
        U_ramp = InputSignal.ramp(T)
        T2, y_ramp, _ = forced_response(sys_orig, U=U_ramp, T=T)  # safe wrapper
        y_ramp = np.squeeze(y_ramp)
        return T1, z, y_ramp


class ResponseEngine:
    """High-level façade for SISO ramp and TF arbitrary input."""

    def ramp_ss(self, model: SSModel, *, tfinal: float = 10.0, dt: float = 0.01):
        return AugmentationEngine().unit_ramp_response(model, tfinal, dt)

    def lsim_tf(
        self,
        model: TFModel,
        *,
        u: Literal["ramp", "sine", "square"] = "ramp",
        tfinal: float = 10.0,
        dt: float = 0.01,
    ):
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
        T_out, y, _ = forced_response(G, U=U, T=T)  # safe wrapper
        return np.asarray(T_out), np.squeeze(y), U


# ---------- Engines (MIMO step responses for SS) ----------

class MIMOStepEngine:
    """MIMO step responses and utilities for state-space models (non-deprecated API usage)."""

    @staticmethod
    def _normalize_y(T: np.ndarray, Y) -> np.ndarray:
        """
        Normalize outputs (or states) to shape (nout, N) given time T of length N.
        Handles shapes: (N,), (nout,N), (N,nout), (nout,1,N), (nout,nin,N).
        """
        T = np.asarray(T).ravel()
        N = T.size
        Y = np.asarray(Y)
        Y = np.squeeze(Y)  # drop singleton dims where safe

        if Y.ndim == 0:
            # scalar -> (1, N) replicated
            return np.full((1, N), float(Y))

        if Y.ndim == 1:
            # (N,) -> (1, N)
            if Y.shape[0] != N:
                raise ValueError(f"normalize_y: 1D Y length {Y.shape[0]} != |T| {N}")
            return Y.reshape(1, -1)

        if Y.ndim == 2:
            # Prefer (nout, N)
            if Y.shape[1] == N:
                return Y
            if Y.shape[0] == N:
                return Y.T

        if Y.ndim == 3:
            # Common: (nout, 1, N) or (nout, nin, N)
            if Y.shape[-1] == N:
                mid = Y.shape[1]
                if mid == 1:
                    return Y[:, 0, :]
                else:
                    # pick first input slice consistently
                    return Y[:, 0, :]

        raise ValueError(f"normalize_y: cannot align shapes. |T|={N}, Y.shape={Y.shape}")

    @staticmethod
    def step_from_input(
        model: SSModel, *, input_index: int, tfinal: float, dt: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Return (T, Y[nout, N]) for a unit step on the selected input channel."""
        sys = model.system()
        T = time_grid(tfinal, dt)
        # Non-deprecated current API: use keyword args
        res = ct.step_response(sys, T=T, input=input_index)
        T_out, Y = _unpack_step_result(res)
        Y = MIMOStepEngine._normalize_y(T_out, Y)
        return np.asarray(T_out), Y

    @staticmethod
    def forced_step_states(
        model: SSModel, *, input_index: int, tfinal: float, dt: float
    ) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
        """Return (T, Y[nout,N] or None, X[nx,N] or None) for a unit step on input_index."""
        sys = model.system()
        T = time_grid(tfinal, dt)
        nin = int(np.asarray(model.B).shape[1])
        U = np.zeros((nin, T.size), dtype=float)
        U[input_index, :] = 1.0
        # Non-deprecated current API
        res = ct.forced_response(sys, T=T, U=U)
        T_out, Y, X = _unpack_forced_result(res)
        if Y is not None:
            Y = MIMOStepEngine._normalize_y(T_out, Y)
        if X is not None:
            X = MIMOStepEngine._normalize_y(T_out, X)
        return np.asarray(T_out), Y, X

    @staticmethod
    def ss2tf_matrix(model: SSModel):
        """Matrix of transfer functions (nout x nin) or None if unavailable."""
        try:
            return ct.ss2tf(model.system())
        except Exception:
            return None

    @staticmethod
    def step_metrics(tf_matrix) -> Dict[str, Optional[Dict[str, Any]]]:
        """Basic step_info per SISO channel, if available."""
        out: Dict[str, Optional[Dict[str, Any]]] = {}
        if tf_matrix is None:
            return out
        try:
            nout, nin = tf_matrix.shape
        except Exception:
            return out
        for i in range(nout):
            for j in range(nin):
                key = f"Y{i+1}/U{j+1}"
                try:
                    info = ct.step_info(tf_matrix[i, j])
                    out[key] = {
                        "RiseTime": float(info.get("RiseTime")) if info.get("RiseTime") is not None else None,
                        "SettlingTime": float(info.get("SettlingTime")) if info.get("SettlingTime") is not None else None,
                        "Overshoot": float(info.get("Overshoot")) if info.get("Overshoot") is not None else None,
                    }
                except Exception:
                    out[key] = None
        return out
