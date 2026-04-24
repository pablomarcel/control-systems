from __future__ import annotations
import warnings
import numpy as np
import control as ct

from typing import Tuple

def rlocus_map(L: ct.TransferFunction) -> Tuple[np.ndarray, np.ndarray]:
    """Return (branches, kvect) with branches shaped (n_branches, n_gains).
    Prefer control.root_locus_map (new API); fall back to root_locus(plot=False).
    """
    n_poles = len(ct.poles(L))
    try:
        resp = ct.root_locus_map(L)
        if hasattr(resp, "poles"):
            arr = np.asarray(resp.poles)
        elif hasattr(resp, "roots"):
            arr = np.asarray(resp.roots)
        elif isinstance(resp, tuple) and len(resp) >= 1:
            arr = np.asarray(resp[0])
        else:
            raise RuntimeError("root_locus_map(): cannot find poles/roots in response.")
        if hasattr(resp, "kvect"):
            kv = np.asarray(resp.kvect)
        elif hasattr(resp, "gains"):
            kv = np.asarray(resp.gains)
        elif isinstance(resp, tuple) and len(resp) >= 2:
            kv = np.asarray(resp[1])
        else:
            kv = np.array([])
        if arr.ndim != 2:
            raise RuntimeError("root_locus_map(): poles/roots array must be 2-D.")
        if arr.shape[1] == n_poles:
            branches = arr.T
        elif arr.shape[0] == n_poles:
            branches = arr
        else:
            branches = arr.T if arr.shape[0] >= arr.shape[1] else arr
        return branches, kv
    except Exception:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=r"root_locus\(\) return value.*", category=FutureWarning)
            roots, kv = ct.root_locus(L, plot=False)
        arr = np.asarray(roots); kv = np.asarray(kv)
        if arr.ndim != 2:
            raise RuntimeError("root_locus(plot=False) returned unexpected shape.")
        if arr.shape[1] == n_poles:
            branches = arr.T
        elif arr.shape[0] == n_poles:
            branches = arr
        else:
            branches = arr.T if arr.shape[0] >= arr.shape[1] else arr
        return branches, kv
