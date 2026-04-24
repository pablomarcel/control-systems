# -*- coding: utf-8 -*-
"""
Controller and observer design building blocks.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
import math
import numpy as np
import control as ct
from .utils import poly_from_roots, phi_of_A, tf_coeffs

@dataclass
class ControllerDesignResult:
    K: np.ndarray               # state feedback row vector (1 x n)
    K_poles: np.ndarray         # placed poles

@dataclass
class ObserverDesignResult:
    Ke: np.ndarray              # reduced-order observer gain (r x 1)
    obs_poles: np.ndarray

def place_controller_acker(A: np.ndarray, B: np.ndarray, K_poles: np.ndarray) -> ControllerDesignResult:
    K = np.atleast_2d(np.real_if_close(ct.acker(A, B, K_poles), 1e8).astype(float))
    return ControllerDesignResult(K=K, K_poles=np.asarray(K_poles, complex))

def reduced_order_observer_gain(Abb: np.ndarray, Aab: np.ndarray, poles: np.ndarray) -> ObserverDesignResult:
    r = Abb.shape[0]
    if r == 0:
        Ke = np.zeros((0, 1))
        return ObserverDesignResult(Ke=Ke, obs_poles=np.asarray(poles, complex))
    coeff = poly_from_roots(poles)
    S = np.vstack([Aab @ np.linalg.matrix_power(Abb, i) for i in range(r)])
    Ke = phi_of_A(Abb, coeff) @ np.linalg.inv(S) @ np.array([[0.0], [1.0]])[:r]
    Ke = np.real_if_close(Ke, 1e8).astype(float)
    return ObserverDesignResult(Ke=Ke, obs_poles=np.asarray(poles, complex))

def choose_N_for_feedback(G: ct.TransferFunction, Gc: ct.TransferFunction) -> float:
    """
    For cfg2 ensure unit step has DC gain 1:
        N = (g0d*c0d + g0n*c0n) / (g0n*c0d), with integrator special-case N=c0n/c0d.
    """
    numG, denG = tf_coeffs(G)
    numC, denC = tf_coeffs(Gc)
    g0n = float(np.polyval(numG, 0.0))
    g0d = float(np.polyval(denG, 0.0))
    c0n = float(np.polyval(numC, 0.0))
    c0d = float(np.polyval(denC, 0.0))

    if abs(g0d) < 1e-14:
        N = c0n / c0d
    else:
        denom = g0n * c0d
        if abs(denom) < 1e-14:
            raise ZeroDivisionError("choose_N_for_feedback: g0n*c0d is zero; cannot set DC gain.")
        N = (g0d * c0d + g0n * c0n) / denom
    return float(N)
