from __future__ import annotations
import logging
import numpy as np
import control as ct

def setup_logger(level: int = logging.INFO) -> logging.Logger:
    log = logging.getLogger("systemTool")
    if not log.handlers:
        h = logging.StreamHandler()
        fmt = logging.Formatter("%(levelname)s: %(message)s")
        h.setFormatter(fmt)
        log.addHandler(h)
    log.setLevel(level)
    return log

def get_dims(sys) -> tuple[int, int]:
    m = getattr(sys, "noutputs", None) or getattr(sys, "outputs", None) or sys.C.shape[0]
    r = getattr(sys, "ninputs", None) or getattr(sys, "inputs", None) or sys.B.shape[1]
    return int(m), int(r)

def normalize_rows(T, Y):
    T = np.asarray(T).ravel()
    Y = np.asarray(Y)
    Y = np.squeeze(Y)
    if Y.ndim == 1:
        if Y.size != T.size:
            raise ValueError("Length mismatch between T and Y.")
        return Y.reshape(1, -1)
    if Y.ndim == 2:
        if Y.shape[1] == T.size:
            return Y
        if Y.shape[0] == T.size:
            return Y.T
    if Y.ndim == 3 and Y.shape[-1] == T.size:
        return Y[:, 0, :]
    raise ValueError(f"Cannot align shapes: T={T.size}, Y={Y.shape}")

def forced_response_safe(sys, T, U, X0=None):
    """Call control.forced_response robustly across versions.
    - If X0 is None, omit it (some versions error if X0=None).
    - If provided, coerce X0 to float ndarray.
    Returns (t, y(nout,N), x(nx,N or None)).
    """
    kwargs = dict(T=np.asarray(T), U=np.asarray(U))
    if X0 is not None:
        kwargs["X0"] = np.asarray(X0, dtype=float)
    res = ct.forced_response(sys, **kwargs)

    # Newer API object
    if hasattr(res, "time") and hasattr(res, "outputs"):
        t = np.asarray(res.time).ravel()
        y = normalize_rows(t, res.outputs)
        x = None
        if hasattr(res, "states") and res.states is not None and np.size(res.states) > 0:
            x = normalize_rows(t, res.states)
        return t, y, x

    # Older tuple APIs
    if isinstance(res, tuple) and len(res) in (2, 3):
        t = np.asarray(res[0]).ravel()
        y = normalize_rows(t, res[1])
        x = None
        if len(res) == 3 and res[2] is not None and np.size(res[2]) > 0:
            x = normalize_rows(t, res[2])
        return t, y, x

    raise RuntimeError("Unexpected return from control.forced_response")
