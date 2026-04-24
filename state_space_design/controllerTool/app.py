# -*- coding: utf-8 -*-
"""
High-level application flow: build plant, design controller/observer, assemble closed loops.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple
import logging
import numpy as np
import control as ct

from .core import PlantTF, controllable_companion_from_tf
from .design import place_controller_acker, reduced_order_observer_gain, choose_N_for_feedback
from .utils import array2str, tf_coeffs

@dataclass
class DesignInputs:
    num: np.ndarray
    den: np.ndarray
    K_poles: Optional[np.ndarray] = None
    obs_poles: Optional[np.ndarray] = None
    ts: Optional[float] = None
    undershoot: Optional[Tuple[float, float]] = None
    obs_speed_factor: float = 5.0

@dataclass
class BuildConfig:
    cfg: str = "both"  # "cfg1", "cfg2", "both"

@dataclass
class BuildResult:
    plant_ss: object
    K: np.ndarray
    Ke: np.ndarray
    Gc: ct.TransferFunction
    T1: Optional[ct.TransferFunction]
    T2: Optional[ct.TransferFunction]

def _auto_poles(n: int, ts: Optional[float], undershoot: Optional[Tuple[float, float]], obs_speed_factor: float):
    if undershoot:
        lo, hi = undershoot
        Mp = 0.5 * (lo + hi)
        zeta = 0.6
        for _ in range(40):
            zeta = -np.log(Mp) / np.sqrt(np.pi**2 + (np.log(Mp))**2)
    else:
        zeta = 0.6
    wn = 4 / (zeta * ts) if ts else 2.0
    sigma = zeta * wn; wd = wn * np.sqrt(max(1 - zeta*zeta, 1e-6))
    Kp = np.array([-sigma + 1j*wd, -sigma - 1j*wd] + ([-2.5*sigma] if n >= 3 else [])[:max(n-2,0)], complex)
    if len(Kp) < n:
        Kp = np.hstack([Kp, -2.5*sigma*np.ones(n-len(Kp))])
    Op = np.array([-obs_speed_factor * sigma] * (n - 1), complex)
    return Kp, Op

class ControllerToolApp:
    """
    Main orchestrator. Pure-Python + python-control. No SciPy required.
    """
    def __init__(self, design_inputs: DesignInputs, build_cfg: BuildConfig):
        self.din = design_inputs
        self.bcfg = build_cfg

    def build(self) -> BuildResult:
        plant_ss = controllable_companion_from_tf(self.din.num, self.din.den)
        A, B, C, D = plant_ss.A, plant_ss.B, plant_ss.C, plant_ss.D
        n = A.shape[0]; r = n - 1

        if self.din.K_poles is None or self.din.obs_poles is None:
            Kp_auto, Op_auto = _auto_poles(n, self.din.ts, self.din.undershoot, self.din.obs_speed_factor)
        K_poles = self.din.K_poles if self.din.K_poles is not None else Kp_auto
        obs_poles = self.din.obs_poles if self.din.obs_poles is not None else Op_auto

        K_res = place_controller_acker(A, B, K_poles)
        K = K_res.K

        Aaa = float(A[0, 0]); Aab = A[0:1, 1:]; Aba = A[1:, 0:1]; Abb = A[1:, 1:]
        Ba  = B[0:1, :];      Bb  = B[1:, :]
        Ke_res = reduced_order_observer_gain(Abb, Aab, obs_poles)
        Ke = Ke_res.Ke

        Ahat = Abb - Ke @ Aab
        Bhat = Ahat @ Ke + Aba - Ke * Aaa
        Fhat = Bb - Ke @ Ba

        Ka = float(K[0, 0]); Kb = K[0:1, 1:]
        alpha = float(Ka + (Kb @ Ke).ravel()[0])

        Atil = Ahat - Fhat @ Kb
        Btil = Bhat - Fhat * alpha
        Ctil = -Kb
        Dtil = -np.array([[alpha]], float)

        Gc = -ct.ss2tf(ct.ss(Atil, Btil, Ctil, Dtil))
        G  = ct.tf(self.din.num.tolist(), self.din.den.tolist())

        want_cfg1 = self.bcfg.cfg in ("cfg1", "both")
        want_cfg2 = self.bcfg.cfg in ("cfg2", "both")
        T1 = None; T2 = None
        if want_cfg1:
            L1 = Gc * G
            T1 = ct.feedback(L1, 1)
            logging.info("Config 1 assembled.")
        if want_cfg2:
            from .utils import tf_coeffs
            N = choose_N_for_feedback(G, Gc)
            numG, denG = tf_coeffs(G)
            numC, denC = tf_coeffs(Gc)
            num_T2 = N * np.polymul(numG, denC)
            den_T2 = np.polyadd(np.polymul(denG, denC), np.polymul(numG, numC))
            T2 = ct.tf(num_T2.tolist(), den_T2.tolist())

        return BuildResult(plant_ss=plant_ss, K=K, Ke=Ke, Gc=Gc, T1=T1, T2=T2)
