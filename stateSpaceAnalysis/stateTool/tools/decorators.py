from __future__ import annotations
import functools
import time
from typing import Callable, Any

def traced(fn: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.time()
        out = fn(*args, **kwargs)
        dt = (time.time() - t0) * 1e3
        return out
    return wrapper
