from __future__ import annotations
import logging
import numpy as np
from typing import Tuple

def setup_logger(level: str = "INFO") -> None:
    lvl = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=lvl, format="%(levelname)s: %(message)s")
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("control").setLevel(logging.WARNING)

def parse_vector(s: str | None) -> np.ndarray | None:
    if s is None:
        return None
    toks = [t for t in s.replace(",", " ").replace(";", " ")
                 .replace("[", "").replace("]", "").split() if t.strip()]
    return np.array([float(x) for x in toks], dtype=float)

def parse_matrix(s: str | None) -> np.ndarray | None:
    if s is None:
        return None
    s = s.strip().replace("[", "").replace("]", "")
    rows = [r for r in s.split(";") if r.strip()]
    mat = []
    for r in rows:
        toks = [t for t in r.replace(",", " ").split() if t.strip()]
        mat.append([float(x) for x in toks])
    return np.array(mat, dtype=float)

def coeffs_from_tf(G) -> Tuple[np.ndarray, np.ndarray]:
    """Return (num, den) as 1‑D arrays for SISO regardless of control version."""
    import control as ct
    try:
        num, den = ct.tfdata(G, squeeze=True)  # newer API
    except TypeError:
        num, den = ct.tfdata(G)
        def _flat(a):
            while isinstance(a, (list, tuple)) and len(a) > 0:
                a = a[0]
            return a
        num, den = _flat(num), _flat(den)
    return np.asarray(num, float).ravel(), np.asarray(den, float).ravel()

def normalize_tf(num, den):
    den = np.asarray(den, float).ravel()
    num = np.asarray(num, float).ravel()
    k = 0
    while k < len(den) and abs(den[k]) == 0:
        k += 1
    den = den[k:]
    if den.size == 0:
        raise ValueError("Denominator is all zeros.")
    lead = den[0]
    den = den / lead
    num = num / lead
    if len(num) < len(den):
        num = np.pad(num, (len(den) - len(num), 0))
    return num, den

def clip_small(a, tol=1e-12):
    a = np.asarray(a, float).copy()
    a[np.abs(a) < tol] = 0.0
    return a

def coerce_outputs_to_m_by_N(Y, N_time) -> np.ndarray:
    import numpy as np
    Y = np.asarray(Y)
    logging.debug(f"raw Y.shape={Y.shape}")
    Y = np.squeeze(Y)
    logging.debug(f"squeezed Y.shape={Y.shape}")
    if Y.ndim == 1:
        Y = Y.reshape(1, -1)
    elif Y.ndim == 2:
        if Y.shape[1] == N_time:
            pass
        elif Y.shape[0] == N_time:
            Y = Y.T
        else:
            logging.warning("Unexpected 2‑D shape for Y; proceeding as (m,N) as‑is.")
    elif Y.ndim == 3:
        if Y.shape[-1] == N_time:
            if Y.shape[1] == 1:
                Y = Y[:, 0, :]
            elif Y.shape[0] == 1:
                Y = Y[0, :, :]
            else:
                if Y.shape[1] == 1:
                    Y = np.squeeze(Y, axis=1)
                else:
                    Y = Y.reshape(Y.shape[0], -1)
        else:
            Y = np.squeeze(Y)
            if Y.ndim == 2 and Y.shape[0] == N_time:
                Y = Y.T
    else:
        Y = Y.reshape(Y.shape[0], -1)
    return Y
