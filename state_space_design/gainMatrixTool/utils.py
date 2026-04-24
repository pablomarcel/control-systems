from __future__ import annotations
from dataclasses import dataclass
import functools, time, logging
import numpy as np

def timed(fn):
    """Decorator: log runtime if logging is configured."""
    @functools.wraps(fn)
    def wrap(*args, **kwargs):
        t0 = time.time()
        out = fn(*args, **kwargs)
        dt = (time.time() - t0)*1000.0
        logging.getLogger(__name__).debug("%s ran in %.2f ms", fn.__name__, dt)
        return out
    return wrap

def pretty_matrix(M: np.ndarray, digits: int = 6) -> str:
    return np.array2string(M, formatter={"float_kind": lambda v: f"{v:.{digits}f}"})

def to_jsonable(x):
    import numpy as _np
    arr = _np.array(x)
    arr = _np.real_if_close(arr, tol=1e8)
    if _np.iscomplexobj(arr):
        arr = _np.real(arr)
    if arr.ndim == 0:
        try:
            return float(arr)
        except Exception:
            return arr.item()
    return arr.tolist()
