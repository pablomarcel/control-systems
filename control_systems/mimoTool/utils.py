
from __future__ import annotations
import os
import numpy as np
from typing import Optional

def ensure_dir(path: str) -> str:
    """Ensure directory exists and return it."""
    os.makedirs(path, exist_ok=True)
    return path

def ensure_out_path(path: Optional[str], default_dir: str, default_name: str) -> str:
    """
    Return a writable file path.
      - None -> default_dir/default_name
      - Dir  -> dir/default_name
      - File -> ensure parent and return as-is
    """
    if path is None or path == "":
        ensure_dir(default_dir)
        return os.path.join(default_dir, default_name)
    base, ext = os.path.splitext(path)
    if ext == "":
        ensure_dir(path)
        return os.path.join(path, default_name)
    ensure_dir(os.path.dirname(path) or ".")
    return path

def get_poles(sys):
    """Return poles, compatible across python-control versions."""
    import numpy as _np
    import control as ct
    try:
        return _np.sort(ct.pole(sys))
    except AttributeError:
        try:
            return _np.sort(ct.poles(sys))
        except Exception:
            try:
                return _np.sort(_np.linalg.eigvals(sys.A))
            except Exception as exc:
                raise RuntimeError("Could not compute poles for this system.") from exc

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
    return Y.reshape(Y.shape[0], -1)
