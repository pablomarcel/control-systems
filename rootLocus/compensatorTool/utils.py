# modernControl/rootLocus/compensatorTool/utils.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
import math
import numpy as np
import control as ct

# ---------- logging helper (used by many modules) ----------
import logging, sys

def build_logger(name: str = "compensatorTool", level=logging.INFO) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(level)
    if not log.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        log.addHandler(h)
    return log

LOG = build_logger()

# ---------- generic math / TF helpers ----------

def parse_list(s: str) -> np.ndarray:
    return np.array([float(x) for x in s.replace(";", ",").split(",") if x.strip()], dtype=float)


def tf_arrays(G: "ct.TransferFunction") -> Tuple[np.ndarray, np.ndarray]:
    try:
        num, den = ct.tfdata(G, squeeze=True)
    except TypeError:
        num, den = ct.tfdata(G)
        def _flat(a):
            while isinstance(a, (list, tuple)) and len(a) > 0:
                a = a[0]
            return a
        num, den = _flat(num), _flat(den)
    return np.asarray(num, float).ravel(), np.asarray(den, float).ravel()


def polyval(n: np.ndarray, s: complex) -> complex:
    return np.polyval(n, s)


def angle(z: complex) -> float:
    return math.atan2(z.imag, z.real)


def wrap_pi(th: float) -> float:
    return (th + math.pi) % (2 * math.pi) - math.pi


def pretty_poly(c: np.ndarray) -> str:
    s = ""; N = len(c)
    for k, ck in enumerate(c):
        pwr = N - 1 - k
        if abs(ck) < 1e-12:
            continue
        sign = " + " if ck >= 0 and s != "" else (" - " if ck < 0 and s != "" else ("-" if ck < 0 else ""))
        mag = abs(ck)
        if pwr == 0:
            term = f"{mag:.6g}"
        elif pwr == 1:
            term = ("" if abs(mag - 1) < 1e-12 else f"{mag:.6g}") + "s"
        else:
            term = ("" if abs(mag - 1) < 1e-12 else f"{mag:.6g}") + f"s^{pwr}"
        s += sign + term
    return s or "0"


def pretty_tf(sys: "ct.TransferFunction") -> str:
    n, d = tf_arrays(sys)
    return f"({pretty_poly(n)}) / ({pretty_poly(d)})"


def _count_s_power_desc(coeffs: np.ndarray, tol=1e-14) -> int:
    k = 0
    for c in coeffs[::-1]:
        if abs(c) <= tol:
            k += 1
        else:
            break
    return k


def error_constants(L: "ct.TransferFunction") -> dict:
    """Unity‑feedback open‑loop constants: Kp, Kv, Ka and type."""
    n, d = tf_arrays(L)
    kn = _count_s_power_desc(n)
    kd = _count_s_power_desc(d)
    k_common = min(kn, kd)
    if k_common:
        n = n[:-k_common] if k_common < len(n) else np.array([0.0])
        d = d[:-k_common]
    m = _count_s_power_desc(d)
    d0 = d[:-m] if m > 0 else d
    n0 = n
    d0c = d0[-1] if d0.size else 0.0
    n0c = n0[-1] if n0.size else 0.0

    def _fmt(v):
        return float(v) if np.isfinite(v) else v

    if m >= 1:
        Kp = np.inf
    else:
        Kp = n0c / d0c

    if m == 0:
        Kv = 0.0
    elif m == 1:
        Kv = n0c / d0c
    else:
        Kv = np.inf

    if m <= 1:
        Ka = 0.0
    elif m == 2:
        Ka = n0c / d0c
    else:
        Ka = np.inf

    return dict(Kp=_fmt(Kp), Kv=_fmt(Kv), Ka=_fmt(Ka), type=m)