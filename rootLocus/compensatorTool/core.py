# modernControl/rootLocus/compensatorTool/core.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import math
import numpy as np
import control as ct

from .utils import LOG, tf_arrays, polyval, angle, wrap_pi

# ---------- model primitives ----------

@dataclass(slots=True)
class LeadStage:
    """A single lead stage with zero at -z and pole at -p (p>z>0). T1=1/z, gamma=p/z."""
    T1: float
    gamma: float
    z: float
    p: float

# ---------- angle helpers ----------

def angle_deficiency(G: "ct.TransferFunction", sstar: complex) -> float:
    """φ = π − Arg(G(s*)) wrapped to (0,π]."""
    n, d = tf_arrays(G)
    L = polyval(n, sstar) / polyval(d, sstar)
    return abs(wrap_pi(math.pi - angle(L)))


def bisector_raw_intersections(sstar: complex, phi: float) -> Tuple[float, float]:
    x, y = sstar.real, sstar.imag
    if abs(y) < 1e-14:
        raise ValueError("s* must be off the real axis.")
    u_left = np.array([-1.0, 0.0])
    u_PO = np.array([-x, -y]); u_PO = u_PO / np.linalg.norm(u_PO)
    b = u_left / np.linalg.norm(u_left) + u_PO
    beta = math.atan2(b[1], b[0])
    xs = []
    for sgn in (+1, -1):
        th = beta + sgn * (phi / 2.0)
        xs.append(x - y / math.tan(th))
    xs.sort()
    return xs[1], xs[0]  # (zero, pole)


def solve_p_for_angle(sstar: complex, phi: float, z: float) -> float | None:
    def f(p):
        return wrap_pi(angle((sstar + z) / (sstar + p)) - phi)
    p_lo = z * (1.0 + 1e-9)
    p_hi = max(10 * z, 10 * (abs(sstar.real) + abs(sstar.imag) + 1.0))
    f_lo = f(p_lo + 1e-12)
    ok = False
    for _ in range(60):
        f_hi = f(p_hi)
        if f_lo * f_hi < 0:
            ok = True
            break
        p_hi *= 1.6
        if p_hi > 1e16:
            break
    if not ok:
        return None
    for _ in range(160):
        pm = 0.5 * (p_lo + p_hi); fm = f(pm)
        if f_lo * fm <= 0:
            p_hi = pm
        else:
            p_lo, f_lo = pm, fm
        if abs(p_hi - p_lo) < 1e-12:
            break
    return float(0.5 * (p_lo + p_hi))


def repair_lead_by_scan(sstar: complex, phi: float) -> Tuple[float, float]:
    best = None
    a = sstar
    for z in np.logspace(-4, 4, 1000):
        p = solve_p_for_angle(a, phi, z)
        if p is None or not (p > z > 0):
            continue
        mag = abs((a + z) / (a + p))
        gamma = p / z
        score = abs(math.log(mag)) + 0.01 * abs(math.log(gamma / 4.0))
        if (best is None) or (score < best[0]):
            best = (score, z, p)
    if best is None:
        raise RuntimeError("Could not generate a valid lead (z,p) from angle constraint.")
    _, z, p = best
    return float(z), float(p)


def lead_from_bisector_validated(sstar: complex, phi: float) -> Tuple[float, float]:
    try:
        xz, xp = bisector_raw_intersections(sstar, phi)
    except Exception:
        xz, xp = (None, None)
    z = xz if (xz is not None and xz > 0) else None
    p = xp if (xp is not None and xp > 0) else None
    if (z is None) or (p is None) or not (p > z):
        z, p = repair_lead_by_scan(sstar, phi)
    return z, p

# ---------- lag helpers ----------

def lag_angle_mag(sstar: complex, beta: float, T2: float) -> tuple[float, float]:
    z = 1.0 / T2
    p = 1.0 / (beta * T2)
    r = (sstar + z) / (sstar + p)
    return (math.degrees(wrap_pi(angle(r))), abs(r))


def choose_T2(sstar: complex, beta: float,
              thetamax_deg: float = 5.0,
              mag_lo: float = 0.98, mag_hi: float = 1.02,
              T2max: float = 1000.0) -> float:
    grid = np.logspace(-2, math.log10(max(T2max, 1e-2)), 800)
    best = grid[-1]
    for T in grid[::-1]:
        ang, mag = lag_angle_mag(sstar, beta, T)
        if (-thetamax_deg <= ang <= 0.0) and (mag_lo <= mag <= mag_hi):
            best = T; break
    return float(best)

# ---------- composition ----------

def cascade_leads(leads: List[LeadStage]) -> Tuple[np.ndarray, np.ndarray]:
    num = np.array([1.0]); den = np.array([1.0])
    for L in leads:
        num = np.convolve(num, np.array([1.0, 1.0 / L.T1]))
        den = np.convolve(den, np.array([1.0, L.gamma / L.T1]))
    return num, den


def add_lag(num: np.ndarray, den: np.ndarray, T2: float, beta: float) -> Tuple[np.ndarray, np.ndarray]:
    num = np.convolve(num, np.array([1.0, 1.0 / T2]))
    den = np.convolve(den, np.array([1.0, 1.0 / (beta * T2)]))
    return num, den


def Gc_from_chain(Kc: float, leads: List[LeadStage], T2: float, beta: float) -> "ct.TransferFunction":
    num, den = cascade_leads(leads)
    num, den = add_lag(num, den, T2, beta)
    num = Kc * num
    return ct.tf(num, den)