from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
import control as ct

@dataclass
class StateSpaceModel:
    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: np.ndarray

    def as_control(self) -> ct.StateSpace:
        return ct.ss(self.A, self.B, self.C, self.D)

    @property
    def n(self) -> int:
        return int(self.A.shape[0])

    @property
    def m(self) -> int:
        return int(self.B.shape[1])

    @property
    def p(self) -> int:
        return int(self.C.shape[0])


@dataclass
class LQRDesignResult:
    K: np.ndarray
    P: np.ndarray
    eig_cl: np.ndarray


@dataclass
class Trajectory:
    T: np.ndarray
    X: np.ndarray
    Y: np.ndarray
    U: np.ndarray


class Simulator:
    """Simulation utilities for initial and forced responses with robust result unpacking."""

    @staticmethod
    def _to_T_y_x(resp):
        # tuple API (legacy or return_x=True path)
        if isinstance(resp, tuple):
            if len(resp) == 3:
                T, y, x = resp
                return np.asarray(T), np.asarray(y), np.asarray(x)
            if len(resp) == 2:
                T, y = resp
                T = np.asarray(T); y = np.asarray(y)
                x = np.zeros((0, T.size))
                return T, y, x
        # ResponseData object (python-control >=0.10.0)
        T = np.asarray(getattr(resp, "time"))
        y = np.asarray(getattr(resp, "outputs"))
        x_attr = getattr(resp, "states", None)
        if x_attr is None or (isinstance(x_attr, (list, tuple)) and len(x_attr) == 0):
            x = np.zeros((0, T.size))
        else:
            x = np.asarray(x_attr)
        return T, y, x

    @staticmethod
    def initial(model: StateSpaceModel, K: np.ndarray, x0: np.ndarray, T: np.ndarray) -> Trajectory:
        Acl = model.A - model.B @ K
        sys = ct.ss(Acl, np.zeros((model.n, 1)), model.C, model.D)
        try:
            resp = ct.initial_response(sys, T=T, X0=x0.flatten(), return_x=True)
        except TypeError:
            resp = ct.initial_response(sys, T=T, X0=x0.flatten())
        T0, y, x = Simulator._to_T_y_x(resp)
        if x.size == 0:
            # reconstruct using expm when states not provided
            from scipy.linalg import expm
            x = np.zeros((model.n, T0.size))
            for k, tk in enumerate(T0):
                x[:, k] = (expm(Acl * tk) @ x0).flatten()
        u = -(K @ x).reshape(1, -1)
        return Trajectory(T0, x, y.reshape(model.p, -1), u)

    @staticmethod
    def forced_step(model: StateSpaceModel, K: np.ndarray, N: float, T: np.ndarray, amp: float = 1.0) -> Trajectory:
        Acl = model.A - model.B @ K
        sys = ct.ss(Acl, model.B * N, model.C, model.D)
        U = amp * np.ones_like(T)
        try:
            resp = ct.forced_response(sys, T=T, U=U, X0=np.zeros((model.n,)))
        except TypeError:
            resp = ct.forced_response(sys, T=T, U=U, X0=np.zeros((model.n,)))
        Ts, y, x = Simulator._to_T_y_x(resp)
        if x.size == 0:
            x = np.zeros((model.n, Ts.size))
        u = -(K @ x).reshape(1, -1) + N * U.reshape(1, -1)
        return Trajectory(Ts, x, y.reshape(model.p, -1), u)
