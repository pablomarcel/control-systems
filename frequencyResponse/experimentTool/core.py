from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
import math
import numpy as np
import control as ct

from .design import ModelSpec
from .utils import info, np2list

def poly_mul(a: List[float], b: List[float]) -> List[float]:
    return np.polymul(a, b).tolist()

def build_rational_tf(spec: ModelSpec) -> ct.TransferFunction:
    """Builds the *rational* part of G(s) (no transport lag)."""
    spec.clean()
    num = [spec.K]
    den = [1.0]
    for wz in spec.zeros:
        num = poly_mul(num, [1.0 / wz, 1.0])
    if spec.lam > 0:
        den = poly_mul(den, [1.0] + [0.0] * spec.lam)
    for wp in spec.poles1:
        den = poly_mul(den, [1.0 / wp, 1.0])
    for wn, zeta in zip(spec.wns, spec.zetas):
        den = poly_mul(den, [1.0 / (wn * wn), 2.0 * zeta / wn, 1.0])
    return ct.TransferFunction(num, den)

def complex_response(sys: ct.TransferFunction, w: np.ndarray) -> np.ndarray:
    """Stable across python-control versions; avoids deprecated freqresp()."""
    return np.array([np.asarray(ct.evalfr(sys, 1j*wi)).squeeze() for wi in w], dtype=complex)

@dataclass(slots=True)
class BodeData:
    w: np.ndarray
    mag_db: np.ndarray
    phase_deg: np.ndarray

def bode_arrays(sys: ct.TransferFunction, w: np.ndarray, delay: float,
                *, delay_method: str = "frd") -> BodeData:
    H = complex_response(sys, w)
    if delay_method == "frd" and delay > 0:
        H = H * np.exp(-1j * w * delay)
    mag_db = 20.0*np.log10(np.maximum(np.abs(H), 1e-20))
    phase_deg = np.degrees(np.unwrap(np.angle(H)))
    return BodeData(w=w, mag_db=mag_db, phase_deg=phase_deg)

def pretty_tf(num, den) -> str:
    return f"TF(num={np2list(num)}, den={np2list(den)})"
