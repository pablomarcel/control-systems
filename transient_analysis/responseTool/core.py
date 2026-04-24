# transient_analysis/responseTool/core.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional, Tuple, Dict, Any, List
import numpy as np
import control as ct

from .utils import (
    mk_ss,
    mk_tf,
    step_response,        # version-safe wrapper (SISO)
    forced_response,      # version-safe wrapper (SISO)
    time_grid,
    _unpack_step_result,  # used when calling control.* directly (MIMO)
    _unpack_forced_result
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


@dataclass(slots=True)
class SecondOrderModel:
    """Standard 2nd order: G(s) = K / (s^2 + 2*zeta*wn*s + wn^2)."""
    wn: float
    zeta: float
    K: float | None = None
    def system(self) -> ct.TransferFunction:
        K = self.K if self.K is not None else (self.wn ** 2)
        return mk_tf(
            np.array([K], float),
            np.array([1.0, 2.0 * self.zeta * self.wn, self.wn ** 2], float)
        )


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
    """Ramp via augmentation trick for SISO SS.

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
        T1, z = step_response(sys_aug, T)  # wrapper
        z = np.squeeze(z)
        U_ramp = InputSignal.ramp(T)
        T2, y_ramp, _ = forced_response(sys_orig, U=U_ramp, T=T)  # wrapper
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
        T_out, y, _ = forced_response(G, U=U, T=T)  # wrapper
        return np.asarray(T_out), np.squeeze(y), U


# ---------- Engines (MIMO step responses for SS) ----------

class MIMOStepEngine:
    """MIMO step responses and utilities for state-space models (non-deprecated API usage)."""

    @staticmethod
    def _normalize_y(T: np.ndarray, Y) -> np.ndarray:
        T = np.asarray(T).ravel()
        N = T.size
        Y = np.asarray(Y)
        Y = np.squeeze(Y)
        if Y.ndim == 0:
            return np.full((1, N), float(Y))
        if Y.ndim == 1:
            if Y.shape[0] != N:
                raise ValueError(f"normalize_y: 1D Y length {Y.shape[0]} != |T| {N}")
            return Y.reshape(1, -1)
        if Y.ndim == 2:
            if Y.shape[1] == N:
                return Y
            if Y.shape[0] == N:
                return Y.T
        if Y.ndim == 3 and Y.shape[-1] == N:
            mid = Y.shape[1]
            return Y[:, 0, :] if mid >= 1 else Y[:, 0, :]
        raise ValueError(f"normalize_y: cannot align shapes. |T|={N}, Y.shape={Y.shape}")

    @staticmethod
    def step_from_input(
        model: SSModel, *, input_index: int, tfinal: float, dt: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        sys = model.system()
        T = time_grid(tfinal, dt)
        # modern control API supports keywords T= and input=
        res = ct.step_response(sys, T=T, input=input_index)
        T_out, Y = _unpack_step_result(res)
        Y = MIMOStepEngine._normalize_y(T_out, Y)
        return np.asarray(T_out), Y

    @staticmethod
    def forced_step_states(
        model: SSModel, *, input_index: int, tfinal: float, dt: float
    ) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
        sys = model.system()
        T = time_grid(tfinal, dt)
        nin = int(np.asarray(model.B).shape[1])
        U = np.zeros((nin, T.size), dtype=float)
        U[input_index, :] = 1.0
        res = ct.forced_response(sys, T=T, U=U)
        T_out, Y, X = _unpack_forced_result(res)
        if Y is not None:
            Y = MIMOStepEngine._normalize_y(T_out, Y)
        if X is not None:
            X = MIMOStepEngine._normalize_y(T_out, X)
        return np.asarray(T_out), Y, X

    @staticmethod
    def ss2tf_matrix(model: SSModel):
        try:
            return ct.ss2tf(model.system())
        except Exception:
            return None

    @staticmethod
    def step_metrics(tf_matrix) -> Dict[str, Optional[Dict[str, Any]]]:
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


# ---------- Engines (Second-order analytics & simulation) ----------

class SecondOrderEngine:
    """Analytics + simulation for standard second-order systems."""

    @staticmethod
    def infer_from_coeffs(K: float, a2: float, a1: float, a0: float) -> Tuple[float, float, float]:
        if a2 <= 0 or a0 <= 0:
            raise ValueError("Require a2>0 and a0>0 for a proper 2nd-order form.")
        wn = np.sqrt(a0 / a2)
        zeta = a1 / (2.0 * np.sqrt(a0 * a2))
        K_eq = K * (wn ** 2) / a0  # match DC gain
        return float(wn), float(zeta), float(K_eq)

    @staticmethod
    def analytic_metrics(wn: float, zeta: float) -> Dict[str, float]:
        wd = wn * np.sqrt(max(0.0, 1.0 - zeta ** 2))
        if 0 < zeta < 1:
            Mp = np.exp(-zeta * np.pi / np.sqrt(1 - zeta ** 2)) * 100.0
            Tp = np.pi / wd
            Tr = (np.pi - np.arccos(zeta)) / wd
        else:
            Mp, Tp, Tr = 0.0, np.nan, np.nan
        Ts = (4.0 / (zeta * wn)) if zeta > 0 else np.nan
        return dict(Mp=float(Mp), Tp=float(Tp), Ts=float(Ts), Tr=float(Tr), wd=float(wd))

    @staticmethod
    def classify(zeta: float) -> str:
        if zeta < 0:
            return "unstable (negative damping)"
        if np.isclose(zeta, 1.0):
            return "critically damped"
        if zeta < 1.0:
            return "underdamped"
        if zeta > 1.0:
            return "overdamped"
        return "undamped"

    @staticmethod
    def auto_time(wn: float, zeta: float, tfinal: float | None = None, dt: float = 1e-3) -> np.ndarray:
        if tfinal is None:
            tfinal = (6.0 / (zeta * wn)) if zeta > 0 else (8.0 / wn)
        N = max(1000, int(tfinal / dt))
        return np.linspace(0.0, tfinal, N)

    @staticmethod
    def step(model: SecondOrderModel, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        G = model.system()
        # keyword API is current and supported
        T, y = ct.step_response(G, T=t)
        return np.asarray(T), np.squeeze(np.asarray(y))

    @staticmethod
    def measure_step(T: np.ndarray, y: np.ndarray, tol: float = 0.02) -> Dict[str, float]:
        y = np.asarray(y).ravel()
        T = np.asarray(T).ravel()
        y_final = y[-1]
        y_peak = float(np.max(y))
        Mp = max(0.0, (y_peak - y_final) / max(1e-12, y_final) * 100.0)
        Tp = float(T[int(np.argmax(y))])
        lower, upper = (1 - tol) * y_final, (1 + tol) * y_final
        Ts = np.nan
        for k in range(len(T) - 1, -1, -1):
            if not (lower <= y[k] <= upper):
                Ts = float(T[min(k + 1, len(T) - 1)])
                break
        y10, y90 = 0.1 * y_final, 0.9 * y_final
        try:
            t10 = float(T[np.where(y >= y10)[0][0]])
            t90 = float(T[np.where(y >= y90)[0][0]])
            Tr = t90 - t10
        except Exception:
            Tr = float('nan')
        return dict(Mp=float(Mp), Tp=float(Tp), Ts=float(Ts), Tr=float(Tr), y_final=float(y_final), y_peak=y_peak)

    @staticmethod
    def sweep_zeta(wn: float, zetas: List[float], t: np.ndarray) -> Dict[str, Any]:
        out: Dict[str, Any] = {"T": np.asarray(t).tolist(), "curves": []}
        for z in zetas:
            model = SecondOrderModel(wn=float(wn), zeta=float(z), K=None)
            T, y = SecondOrderEngine.step(model, t)
            out["curves"].append({"zeta": float(z), "y": y.tolist()})
        return out


# ---------- Engines (Second-order 2D/3D surfaces) ----------

class SecondOrderSurfaceEngine:
    """Engines for standard second-order system surfaces and overlays.

    Standard form:
        G(s) = wn^2 / (s^2 + 2*zeta*wn*s + wn^2)
    """

    @staticmethod
    def std2_tf(wn: float, zeta: float):
        num = [wn ** 2]
        den = [1.0, 2.0 * zeta * wn, wn ** 2]
        return mk_tf(np.array(num, float), np.array(den, float))

    @staticmethod
    def step_response_1d(sys, T: np.ndarray) -> np.ndarray:
        T_out, y = step_response(sys, T)  # wrapper (version-safe), returns (T, y)
        y = np.asarray(y)
        if y.ndim == 2:
            y = y[0, :]
        return np.asarray(y).ravel()

    @staticmethod
    def metrics_from_step(y: np.ndarray, T: np.ndarray, tol: float = 0.02) -> dict:
        i_peak = int(np.argmax(y))
        ypk = float(y[i_peak])
        tpk = float(T[i_peak])
        yss = float(y[-1])
        band = tol * abs(yss)
        idx = np.where(np.abs(y - yss) > band)[0]
        ts2 = float(T[idx[-1]]) if idx.size else 0.0
        return dict(peak=ypk, t_peak=tpk, y_ss=yss, Ts_2pct=ts2)

    # ---- simulations ----

    def overlays(self, wn: float, zetas: list[float], *, tfinal: float, dt: float) -> tuple[np.ndarray, dict]:
        """Return (T, curves) where curves[zeta] = y(T)."""
        T = time_grid(tfinal, dt)
        curves: dict[float, np.ndarray] = {}
        for z in zetas:
            sys = self.std2_tf(wn, z)
            y = self.step_response_1d(sys, T)
            curves[float(z)] = y
        return T, curves

    def mesh(self, wn: float, zeta_grid: np.ndarray, *, tfinal: float, dt: float) -> tuple[np.ndarray, np.ndarray]:
        """Return (T, Z) where Z has shape (len(zeta_grid), len(T))."""
        T = time_grid(tfinal, dt)
        Z_rows = []
        for z in zeta_grid:
            sys = self.std2_tf(wn, float(z))
            y = self.step_response_1d(sys, T)
            Z_rows.append(y)
        Z = np.vstack(Z_rows)  # (Nz, Nt)
        return T, Z
