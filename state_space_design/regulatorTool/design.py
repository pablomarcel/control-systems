#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
design.py — classes that implement the regulator design with reduced-order observer.
"""

from __future__ import annotations
import logging, math
from typing import Tuple, Optional
import numpy as np
import control as ct
from .utils import parse_real_vec, parse_complex_list, array2str, mat_inline, poly_from_roots, phi_of_A, bode_data, rlocus_from_control
from .core import Plant, RegulatorParams, SimulationSpec, RegulatorDesignResult, Signals

class PlantFactory:
    """Create a controllable companion form realization with x1=y that matches the given TF."""
    @staticmethod
    def from_tf(num: np.ndarray, den: np.ndarray) -> Plant:
        den = np.asarray(den, float).ravel()
        num = np.asarray(num, float).ravel()
        if abs(den[0] - 1.0) > 1e-12:
            num = num / den[0]; den = den / den[0]

        n = len(den) - 1
        if len(num) > n:
            num = num[-n:]
        num = np.pad(num, (n - len(num), 0))  # degree n-1..0

        a = den[1:]  # [a1..an]
        A = np.zeros((n, n), float)
        for i in range(n - 1):
            A[i, i + 1] = 1.0
        A[-1, :] = -a[::-1]

        # triangular mapping for B so that TF = num/den
        b = np.zeros(n, float)
        b[0] = num[0]
        for k in range(1, n):
            b[k] = num[k] - sum(a[i - 1] * b[k - i] for i in range(1, k + 1))
        B = b.reshape(-1, 1)

        C = np.zeros((1, n)); C[0, 0] = 1.0
        D = 0.0
        return Plant(num=num, den=den, A=A, B=B, C=C, D=D)

class ReducedObserverDesigner:
    """Implements Ogata's minimum-order observer (p=1 → r=n-1)."""
    @staticmethod
    def min_order_acker(Abb: np.ndarray, Aab: np.ndarray, poles: np.ndarray) -> np.ndarray:
        r = Abb.shape[0]
        if r == 0:
            return np.zeros((0, 1))
        coeff = poly_from_roots(poles)
        S = np.vstack([Aab @ np.linalg.matrix_power(Abb, i) for i in range(r)])
        logging.info("rank(S) = %d (expected r = %d)", np.linalg.matrix_rank(S), r)
        e_r = np.zeros((r, 1)); e_r[-1, 0] = 1.0
        Ke = phi_of_A(Abb, coeff) @ np.linalg.inv(S) @ e_r
        return np.real_if_close(Ke, 1e8).astype(float)

class RegulatorDesigner:
    """Top-level orchestrator for regulator design + simulation + analysis."""
    def __init__(self, plant: Plant, params: RegulatorParams):
        self.plant = plant
        self.params = params

    # ---------- poles helper (manual or auto) ----------
    def _auto_poles(self, n: int) -> Tuple[np.ndarray, np.ndarray]:
        # compute zeta from undershoot band if provided; otherwise 0.6
        if self.params.undershoot is not None:
            lo, hi = self.params.undershoot
            Mp = 0.5 * (lo + hi)
            z = 0.6
            for _ in range(40):
                z = -math.log(Mp) / math.sqrt(math.pi**2 + (math.log(Mp))**2)
            zeta = z
        else:
            zeta = 0.6
        wn = 4 / (zeta * self.params.ts) if self.params.ts else 2.0
        sigma = zeta * wn; wd = wn * math.sqrt(max(1 - zeta*zeta, 1e-6))
        Kp = np.array([-sigma + 1j*wd, -sigma - 1j*wd, -2.5*sigma])[:n]
        Op = np.array([-self.params.obs_speed_factor * sigma] * (n - 1))
        return Kp, Op

    # ---------- main design ----------
    def run(self) -> RegulatorDesignResult:
        A, B, C, D = self.plant.A, self.plant.B, self.plant.C, self.plant.D
        n = A.shape[0]; r = n - 1

        # poles: manual or auto
        if self.params.K_poles is None or self.params.obs_poles is None:
            Kp_auto, Op_auto = self._auto_poles(n)
        K_poles = self.params.K_poles if self.params.K_poles is not None else Kp_auto
        obs_poles = self.params.obs_poles if self.params.obs_poles is not None else Op_auto

        # Design K (acker)
        K = np.atleast_2d(np.real_if_close(ct.acker(A, B, K_poles), 1e8).astype(float))

        # Ogata partitions & reduced-order observer
        Aaa = float(A[0, 0]); Aab = A[0:1, 1:]; Aba = A[1:, 0:1]; Abb = A[1:, 1:]
        Ba  = B[0:1, :];      Bb  = B[1:, :]
        Ke = ReducedObserverDesigner.min_order_acker(Abb, Aab, obs_poles)

        # Observer-controller TF blocks (10-108)
        Ahat = Abb - Ke @ Aab
        Bhat = Ahat @ Ke + Aba - Ke * Aaa
        Fhat = Bb - Ke @ Ba

        Ka = float(K[0, 0]); Kb = K[0:1, 1:]
        alpha = float(Ka + (Kb @ Ke).ravel()[0])

        Atil = Ahat - Fhat @ Kb
        Btil = Bhat - Fhat * alpha
        Ctil = -Kb
        Dtil = -np.array([[alpha]], float)

        # TFs (retain near-cancellations)
        Gc = -ct.ss2tf(ct.ss(Atil, Btil, Ctil, Dtil))
        G  = ct.tf(self.plant.num.tolist(), self.plant.den.tolist())
        L  = Gc * G
        T  = ct.feedback(L, 1)

        return RegulatorDesignResult(K=K, Ke=Ke, Ahat=Ahat, Bhat=Bhat, Fhat=Fhat,
                                     Atil=Atil, Btil=Btil, Ctil=Ctil, Dtil=Dtil,
                                     Gc=Gc, G=G, L=L, T=T)

    # ---------- simulation ----------
    def simulate_initial(self, design: RegulatorDesignResult, spec: SimulationSpec) -> Signals:
        A, B, C = self.plant.A, self.plant.B, self.plant.C
        n = A.shape[0]; r = n - 1

        x0 = np.zeros((n, 1)) if spec.x0 is None else spec.x0.reshape(n, 1)
        e0 = np.zeros((r, 1)) if spec.e0 is None else spec.e0.reshape(r, 1)

        K = design.K; Ke = design.Ke
        Ax = A - B @ K
        Bx = B @ K[:, 1:]
        Ae = self.plant.A[1:, 1:] - Ke @ self.plant.A[0:1, 1:]

        A_aug = np.block([[Ax, Bx],
                          [np.zeros((r, n)), Ae]])
        C_aug = np.eye(n + r)
        sys_aug = ct.ss(A_aug, np.zeros((n + r, 1)), C_aug, np.zeros((n + r, 1)))

        t = np.arange(0.0, float(spec.t_final) + spec.dt / 2, float(spec.dt))
        X0 = np.vstack([x0, e0]).reshape(-1)
        tt, Z = ct.initial_response(sys_aug, T=t, X0=X0)

        X = Z[:n, :]; E = Z[n:, :]
        U = np.empty_like(tt); Y = np.empty_like(tt)
        for k in range(tt.size):
            xk = X[:, k:k+1]; ek = E[:, k:k+1]
            U[k] = float((-K @ xk + K[:, 1:] @ ek).ravel()[0])
            Y[k] = float((C @ xk).ravel()[0])

        return Signals(t=tt, X=X, E=E, U=U, Y=Y)

    # ---------- frequency data ----------
    def bode_open_closed(self, design: RegulatorDesignResult) -> Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray], np.ndarray, np.ndarray]:
        w_ol = np.logspace(-3, 2, 1200)
        w_cl = np.logspace(-1, 2, 900)
        mag_ol, ph_ol = bode_data(design.L, w_ol)
        mag_cl, ph_cl = bode_data(design.T, w_cl)
        return (mag_ol, ph_ol), (mag_cl, ph_cl), w_ol, w_cl

    # ---------- root locus ----------
    def root_locus(self, design: RegulatorDesignResult, rl_k: str) -> Tuple[np.ndarray, np.ndarray]:
        if rl_k.strip().lower() == "auto":
            kvect = None
            logging.info("root_locus: using python-control auto k-grid")
        else:
            p = [float(v) for v in rl_k.replace(",", " ").split()]
            if len(p) != 3:
                raise SystemExit("--rl_k must be 'auto' or 'kmin,kmax,samples'")
            kmin, kmax, km = p[0], p[1], int(p[2])
            kvect = np.logspace(np.log10(kmin), np.log10(kmax), km)
            logging.info("root_locus: custom k-grid [%g, %g] with %d samples", kmin, kmax, km)
        return rlocus_from_control(design.L, kvect)
