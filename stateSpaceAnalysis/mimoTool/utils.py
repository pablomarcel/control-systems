"""
Utility helpers for version-agnostic python-control usage, shape coercions,
decorators, and logging.
"""
from __future__ import annotations
import functools
import logging
import os
from typing import Callable, Any
import numpy as np
try:
    import control as ct  # type: ignore
except Exception:  # pragma: no cover - import failure will be caught in tests
    ct = None  # type: ignore

# -----------------------
# Logging configuration
# -----------------------
def get_logger(name: str = "mimoTool", level: str | None = None) -> logging.Logger:
    lvl = level or os.environ.get("MIMOTOOL_LOG", "INFO").upper()
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(levelname)s [%(name)s] %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, lvl, logging.INFO))
    return logger

log = get_logger()

# -----------------------
# Decorators
# -----------------------
def require_control_lib(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if ct is None:
            raise RuntimeError("python-control is required but not installed.")
        return fn(*args, **kwargs)
    return wrapper

# -----------------------
# Version-agnostic helpers
# -----------------------
@require_control_lib
def get_poles(sys) -> np.ndarray:
    """Return poles from a StateSpace/TransferFunction in sorted order.
    Compatible across python-control versions.
    """
    import numpy as _np
    try:
        p = ct.pole(sys)  # newer name
    except AttributeError:
        try:
            p = ct.poles(sys)  # older fallback
        except Exception:
            try:
                p = _np.linalg.eigvals(sys.A)  # type: ignore[attr-defined]
            except Exception as e:
                raise RuntimeError("Could not compute poles for this system.") from e
    return _np.sort(_np.asarray(p))

def coerce_outputs_m_by_N(Y, N_time: int):
    """
    Make output array shape (m, N_time) robust across python-control versions:
      (N,) -> (1,N)
      (m,N) ok
      (N,m) -> (m,N)
      (m,1,N) or (1,m,N) -> (m,N)
    """
    Y = np.asarray(Y)
    Y = np.squeeze(Y)
    if Y.ndim == 1:
        return Y.reshape(1, -1)
    if Y.ndim == 2:
        if Y.shape[1] == N_time:
            return Y
        if Y.shape[0] == N_time:
            return Y.T
        return Y
    if Y.ndim == 3 and Y.shape[-1] == N_time:
        if Y.shape[1] == 1:
            return Y[:, 0, :]
        if Y.shape[0] == 1:
            return Y[0, :, :]
        return Y.reshape(Y.shape[0], -1)
    # fallback
    return Y.reshape(Y.shape[0], -1)

def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path
