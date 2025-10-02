from __future__ import annotations
import logging, sys
from typing import Tuple
import numpy as np

def build_logger(level=logging.INFO) -> logging.Logger:
    log = logging.getLogger("bodeTool")
    log.setLevel(level)
    if not log.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(level)
        h.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        log.addHandler(h)
    return log

def tf_arrays(G) -> tuple[np.ndarray, np.ndarray]:
    import control as ct
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

def pretty_poly(c: np.ndarray) -> str:
    s = ""
    N = len(c)
    for k, ck in enumerate(c):
        p = N-1-k
        if abs(ck) < 1e-14:
            continue
        sign = " + " if ck>=0 and s!="" else (" - " if ck<0 and s!="" else ("-" if ck<0 else ""))
        mag = abs(ck)
        if p==0: term = f"{mag:.6g}"
        elif p==1: term = ("" if abs(mag-1)<1e-12 else f"{mag:.6g}")+"s"
        else: term = ("" if abs(mag-1)<1e-12 else f"{mag:.6g}")+f"s^{p}"
        s += sign+term
    return s or "0"

def pretty_tf(G) -> str:
    n, d = tf_arrays(G)
    return f"({pretty_poly(n)}) / ({pretty_poly(d)})"
