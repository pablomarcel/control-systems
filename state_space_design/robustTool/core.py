from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
import control as ct
from .utils import parse_vec, log_calls

@dataclass
class Plant:
    num: str
    den: str
    def tf(self) -> ct.TransferFunction:
        return ct.tf(parse_vec(self.num), parse_vec(self.den))

@dataclass
class Controller:
    pid: Optional[str] = None
    K_num: Optional[str] = None
    K_den: Optional[str] = None

    def tf(self) -> ct.TransferFunction:
        if self.K_num and self.K_den:
            return ct.tf(parse_vec(self.K_num), parse_vec(self.K_den))
        if self.pid:
            vals = [float(v) for v in self.pid.replace(" ", "").split(",")]
            if len(vals) not in (3,4):
                raise ValueError("pid must be 'kp,ki,kd[,nd]'")
            kp, ki, kd = vals[0], vals[1], vals[2]
            nd = vals[3] if len(vals)==4 else 0.0
            s = ct.tf([1,0],[1])
            Ti = (ki/s) if ki else 0
            Td = kd*s if (kd and nd<=0) else (kd*(nd*s)/(1+(1/nd)*s) if kd else 0)
            return kp + Ti + Td
        return ct.tf([1],[1])

@dataclass
class Weights:
    Wm_num: Optional[str] = None; Wm_den: Optional[str] = None
    Ws_num: Optional[str] = None; Ws_den: Optional[str] = None
    Wa_num: Optional[str] = None; Wa_den: Optional[str] = None

    def get(self) -> Tuple[ct.TransferFunction, ct.TransferFunction, Optional[ct.TransferFunction]]:
        I = ct.tf([1],[1])
        Wm = ct.tf(parse_vec(self.Wm_num), parse_vec(self.Wm_den)) if (self.Wm_num and self.Wm_den) else I
        Ws = ct.tf(parse_vec(self.Ws_num), parse_vec(self.Ws_den)) if (self.Ws_num and self.Ws_den) else I
        Wa = ct.tf(parse_vec(self.Wa_num), parse_vec(self.Wa_den)) if (self.Wa_num and self.Wa_den) else None
        return Wm, Ws, Wa

class LoopBuilder:
    @staticmethod
    def loops(G: ct.TransferFunction, K: ct.TransferFunction):
        I = ct.tf([1],[1])
        L = ct.series(K, G)
        S = ct.feedback(I, L)  # 1/(1+L)
        T = ct.feedback(L, I)  # L/(1+L)
        return L, S, T

class FrequencyTools:
    @staticmethod
    def evalfr_grid(sys, omega: np.ndarray) -> np.ndarray:
        ny, nu = sys.noutputs, sys.ninputs
        H = np.empty((ny, nu, len(omega)), dtype=complex)
        for k, w in enumerate(omega):
            H[:,:,k] = ct.evalfr(sys, 1j*w)
        return H

    @staticmethod
    def sigma_max_over_w(sys, w: np.ndarray) -> np.ndarray:
        H = FrequencyTools.evalfr_grid(sys, w)
        ny, nu, n = H.shape
        sig = np.empty(n)
        for k in range(n):
            Mk = H[:,:,k]
            if ny==1 and nu==1:
                sig[k] = abs(Mk.item())
            else:
                sig[k] = float(np.linalg.svd(Mk, compute_uv=False)[0])
        return sig

    @staticmethod
    def hinf_sweep(sys, wmin: float, wmax: float, npts: int = 400):
        w = np.logspace(np.log10(wmin), np.log10(wmax), npts)
        sig = FrequencyTools.sigma_max_over_w(sys, w)
        i = int(np.argmax(sig))
        return float(sig[i]), float(w[i]), w, sig

    @staticmethod
    def bode_mag_phase(sys, w: np.ndarray):
        H = FrequencyTools.evalfr_grid(sys, w)
        if H.shape[:2] != (1,1):
            raise ValueError("bode_mag_phase expects SISO.")
        Gjw = H.reshape(-1)
        mag = 20*np.log10(np.maximum(np.abs(Gjw), 1e-16))
        phs = np.angle(Gjw, deg=True)
        return mag, phs
