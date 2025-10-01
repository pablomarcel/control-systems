# rootLocus/systemResponseTool/tools/decorators.py
from __future__ import annotations
import time
from functools import wraps
from ..utils import make_logger

log = make_logger(__name__)

def timed(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            dt = time.perf_counter() - t0
            log.debug("Timing %s: %.3f s", fn.__name__, dt)
    return wrapper
