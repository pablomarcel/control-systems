# -*- coding: utf-8 -*-
"""
Core math/data classes for plant realization in controllable companion form (x1 = y).
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import control as ct
from .utils import array2str

@dataclass
class PlantTF:
    num: np.ndarray
    den: np.ndarray

    def tf(self) -> ct.TransferFunction:
        return ct.tf(self.num.tolist(), self.den.tolist())

@dataclass
class PlantSS:
    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: float

    def as_ct(self) -> ct.StateSpace:
        return ct.ss(self.A, self.B, self.C, self.D)

    def __str__(self) -> str:
        return f"A:\n{array2str(self.A)}\nB:\n{array2str(self.B)}\nC:\n{array2str(self.C)}\nD:{self.D}"

def controllable_companion_from_tf(num: np.ndarray, den: np.ndarray) -> PlantSS:
    """
    Realize SISO TF in controllable companion form with C=[1 0 ... 0], so x1 = y.
    Ensures deg(den) = n, deg(num) <= n-1.
    """
    den = np.asarray(den, float).ravel()
    num = np.asarray(num, float).ravel()
    if abs(den[0] - 1.0) > 1e-12:
        num = num / den[0]; den = den / den[0]

    n = len(den) - 1
    if len(num) > n:
        num = num[-n:]
    num = np.pad(num, (n - len(num), 0))

    a = den[1:]  # [a1..an]
    A = np.zeros((n, n), float)
    for i in range(n - 1):
        A[i, i + 1] = 1.0
    A[-1, :] = -a[::-1]

    # triangular mapping for B so TF = num/den
    b = np.zeros(n, float)
    b[0] = num[0]
    for k in range(1, n):
        b[k] = num[k] - sum(a[i - 1] * b[k - i] for i in range(1, k + 1))
    B = b.reshape(-1, 1)

    C = np.zeros((1, n)); C[0, 0] = 1.0
    D = 0.0
    return PlantSS(A, B, C, D)
