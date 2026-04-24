from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
import numpy as np
import control as ct
import sympy as sp
from .utils import squeeze_poly

@dataclass(slots=True, frozen=True)
class PlantPolys:
    Kp: float
    A: np.ndarray
    B: np.ndarray

def tf_from_coeff(num, den) -> ct.TransferFunction:
    return ct.tf(num, den)

def tf_from_poly(num_expr: str, den_expr: str, s: sp.Symbol) -> ct.TransferFunction:
    num_poly = sp.Poly(sp.expand(sp.sympify(num_expr, locals={str(s): s})), s)
    den_poly = sp.Poly(sp.expand(sp.sympify(den_expr, locals={str(s): s})), s)
    return ct.tf([float(c) for c in num_poly.all_coeffs()],
                 [float(c) for c in den_poly.all_coeffs()])

def tf_from_zpk(zeros, poles, gain: float = 1.0) -> ct.TransferFunction:
    return ct.tf(ct.zpk(zeros, poles, gain))

def plant_polys(Gp: ct.TransferFunction) -> PlantPolys:
    """Factor Gp(s) = Kp * A(s)/B(s) with monic A,B."""
    num_l, den_l = ct.tfdata(Gp)
    num = squeeze_poly(num_l)
    den = squeeze_poly(den_l)
    if den[0] == 0:
        raise ValueError("Leading denominator coefficient is zero.")
    num = num / den[0]
    den = den / den[0]
    B = den / den[0]
    if np.allclose(num, 0):
        raise ValueError("Plant numerator is all zeros.")
    Kp = float(num[0])
    if len(num) > 1:
        A = num / Kp
    else:
        A = np.array([1.0], dtype=float)
    return PlantPolys(Kp=Kp, A=A, B=B)
