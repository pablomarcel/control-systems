# ---------------------------------
# File: transient_analysis/icTool/tools/analytic.py
# ---------------------------------
from __future__ import annotations
import numpy as np

def analytic_solution(T: np.ndarray, m: float, b: float, k: float, x0: float, v0: float):
    """
    Closed-form for x(t) of m x¨ + b x˙ + k x = 0 with x(0)=x0, x˙(0)=v0.
    Returns None if underdamped (complex conjugate poles) to keep it simple.
    """
    a1, a0 = b / m, k / m
    disc = a1*a1 - 4.0*a0
    if disc < 0.0:  # underdamped
        return None
    r1 = (-a1 + np.sqrt(disc)) * 0.5
    r2 = (-a1 - np.sqrt(disc)) * 0.5
    if abs(r1 - r2) < 1e-12:  # repeated
        r = r1
        C1 = x0
        C2 = v0 - r * x0
        return (C1 + C2 * T) * np.exp(r * T)
    # distinct real
    C2 = (v0 - r1 * x0) / (r2 - r1)
    C1 = x0 - C2
    return C1 * np.exp(r1 * T) + C2 * np.exp(r2 * T)
