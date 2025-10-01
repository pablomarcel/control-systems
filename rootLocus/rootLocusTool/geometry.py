from __future__ import annotations
from typing import List, Optional, Tuple
import numpy as np
import math

def asymptotes_centroid(poles: np.ndarray, zeros: np.ndarray) -> tuple[Optional[float], List[float]]:
    n, m = len(poles), len(zeros)
    if n <= m:
        return None, []
    sigma_a = float(np.real_if_close((np.sum(poles) - np.sum(zeros)) / (n - m)))
    angs = [(2 * k + 1) * math.pi / (n - m) for k in range(n - m)]
    return sigma_a, angs

def compute_bounds(R: np.ndarray, poles: np.ndarray, zeros: np.ndarray, margin: float = 0.1) -> tuple[tuple[float,float], tuple[float,float]]:
    xs = [R.real.min(), R.real.max()]
    ys = [R.imag.min(), R.imag.max()]
    if len(poles):
        xs += [poles.real.min(), poles.real.max()]
        ys += [poles.imag.min(), poles.imag.max()]
    if len(zeros):
        xs += [zeros.real.min(), zeros.real.max()]
        ys += [zeros.imag.min(), zeros.imag.max()]
    xmin, xmax = float(min(xs)), float(max(xs))
    ymin, ymax = float(min(ys)), float(max(ys))
    dx = xmax - xmin; dy = ymax - ymin
    if dx <= 0: dx = 1.0
    if dy <= 0: dy = 1.0
    xmin -= margin * dx; xmax += margin * dx
    ymin -= margin * dy; ymax += margin * dy
    rng = max(xmax - xmin, ymax - ymin)
    cx = 0.5 * (xmin + xmax); cy = 0.5 * (ymin + ymax)
    xmin, xmax = cx - 0.5 * rng, cx + 0.5 * rng
    ymin, ymax = cy - 0.5 * rng, cy + 0.5 * rng
    return (xmin, xmax), (ymin, ymax)
