# SPDX-License-Identifier: MIT
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional, Sequence, List
import numpy as np
import control as ct

from .io import ControllerJSON, IOJSON

def parse_time(s: str) -> np.ndarray:
    s = s.strip()
    if ":" in s:
        t0, dt, tf = (float(v) for v in s.split(":"))
        n = int(round((tf - t0)/dt)) + 1
        return np.linspace(t0, tf, n)
    return np.array([float(v) for v in s.replace(",", " ").split()], float)

def parse_vec_real(s: str | None, n: int) -> np.ndarray:
    if s is None:
        v = np.zeros(n, float); v[0] = 1.0; return v
    toks = [t for t in s.replace(",", " ").split() if t]
    comp = np.array([complex(t.replace("i","j")) for t in toks], complex)
    if comp.size != n:
        raise ValueError(f"x0 has length {comp.size}, expected n={n}")
    comp = np.real_if_close(comp, tol=1e8)
    if np.iscomplexobj(comp) and np.max(np.abs(comp.imag)) > 1e-12:
        raise ValueError("x0 contains non-negligible imaginary parts.")
    return np.asarray(comp.real, float)

@dataclass(frozen=True)
class SimICResult:
    t: np.ndarray
    X: np.ndarray  # shape (n, N)
    labels: list[str]

@dataclass(frozen=True)
class SimStepResult:
    t: np.ndarray
    series: list[np.ndarray]  # each shape (N,)
    labels: list[str]
    kind: str  # 'y', 'states', or 'both'

class ScenarioDetector:
    @staticmethod
    def detect(payload: dict) -> str:
        if all(k in payload for k in ("Acl","Bcl","C","D")):
            return "step"
        return "ic"

class ClosedLoopBuilder:
    @staticmethod
    def Acl_from_controller(cj: ControllerJSON) -> tuple[np.ndarray, list[str]]:
        A = cj.A
        n = A.shape[0]
        if cj.mode == 'K':
            if cj.B is None or cj.K is None:
                raise ValueError("Controller JSON missing B or K for mode K")
            B = cj.B
            K = cj.K
            if K.ndim == 1: K = K.reshape(1,-1)
            m = B.shape[1] if B.ndim == 2 else 1
            K = K.reshape(m, n)
            Acl = A - B @ K
        else:
            if cj.C is None or cj.L is None:
                raise ValueError("Controller JSON missing C or L for mode L")
            C = cj.C
            L = cj.L.reshape(n, C.shape[0])
            Acl = A - L @ C
        return Acl, cj.state_names

class Simulator:
    @staticmethod
    def initial_condition(cj: ControllerJSON, t: np.ndarray, x0: np.ndarray) -> SimICResult:
        Acl, names = ClosedLoopBuilder.Acl_from_controller(cj)
        n = Acl.shape[0]
        C = np.eye(n); D = np.zeros((n,1)); B = np.zeros((n,1))
        sys = ct.ss(Acl, B, C, D)
        T, X = ct.initial_response(sys, T=t, X0=x0)  # X: (n, N)
        return SimICResult(T, X, names)

    @staticmethod
    def _fr_extract(res):
        if isinstance(res, (tuple, list)):
            if len(res) >= 3:
                return np.asarray(res[0]), np.asarray(res[1]), np.asarray(res[2])
            elif len(res) == 2:
                return np.asarray(res[0]), np.asarray(res[1]), None
        # object-like
        T = getattr(res, 'time', getattr(res, 'T', getattr(res, 't', None)))
        Y = getattr(res, 'outputs', getattr(res, 'y', getattr(res, 'yout', getattr(res, 'Y', None))))
        X = getattr(res, 'states', getattr(res, 'x', getattr(res, 'xout', getattr(res, 'X', None))))
        if T is None or Y is None:
            raise TypeError("forced_response returned an unsupported type/shape")
        return np.asarray(T), np.asarray(Y), (None if X is None else np.asarray(X))

    @staticmethod
    def _normalize_output(Y, p, N):
        Y = np.asarray(Y)
        if Y.ndim == 1:
            return Y.reshape(1, -1)
        if Y.shape == (N, p):
            return Y.T
        if Y.shape[0] == p and Y.shape[1] == N:
            return Y
        if Y.shape[0] == N:
            return Y.T
        return Y

    @staticmethod
    def _normalize_states(X, n, N):
        if X is None: return None
        X = np.asarray(X)
        if X.shape == (N, n): return X.T
        if X.shape[0] == n and X.shape[1] == N: return X
        if X.shape[0] == N: return X.T
        return X

    @staticmethod
    def _simulate_states_via_output(Acl, Bcl, T, U):
        n = Acl.shape[0]
        I = np.eye(n)
        m = Bcl.shape[1] if Bcl.ndim == 2 else 1
        Z = np.zeros((n, m))
        sys_x = ct.ss(Acl, Bcl, I, Z)
        res = ct.forced_response(sys_x, T=T, U=U)
        T2, Yx, _ = Simulator._fr_extract(res)
        X = Simulator._normalize_output(Yx, n, len(T2))
        return T2, X

    @staticmethod
    def step(ioj: IOJSON, t: np.ndarray, what: str = 'y') -> SimStepResult:
        Acl, Bcl, C, D, r = ioj.Acl, ioj.Bcl, ioj.C, ioj.D, ioj.r
        n = Acl.shape[0]
        m = Bcl.shape[1] if Bcl.ndim == 2 else 1
        p = C.shape[0] if C.ndim == 2 else 1
        sys_io = ct.ss(Acl, Bcl, C, D)

        U = (r * np.ones_like(t)) if m == 1 else (r * np.ones((m, len(t)), dtype=float))
        res_io = ct.forced_response(sys_io, T=t, U=U)
        T, Y_raw, X_raw = Simulator._fr_extract(res_io)
        N = len(T)
        Y = Simulator._normalize_output(Y_raw, p, N)

        need_states = what in ('states','both')
        Xn = Simulator._normalize_states(X_raw, n, N)
        if need_states and Xn is None:
            T2, X_from_y = Simulator._simulate_states_via_output(Acl, Bcl, T, U)
            T, Xn = T2, X_from_y
            N = len(T)

        labels, series = [], []
        if what in ('y','both'):
            for i in range(Y.shape[0]):
                lbl = ioj.output_names[i] if i < len(ioj.output_names) else f"y{i+1}"
                labels.append(lbl)
                series.append(Y[i,:])
        if what in ('states','both'):
            if Xn is not None:
                for i in range(Xn.shape[0]):
                    lbl = ioj.state_names[i] if i < len(ioj.state_names) else f"x{i+1}"
                    labels.append(lbl)
                    series.append(Xn[i,:])
        kind = 'both' if what=='both' else ('states' if what=='states' else 'y')
        return SimStepResult(T, series, labels, kind)
