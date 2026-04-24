# transient_analysis/routhTool/tools/logging_tools.py
from __future__ import annotations
import functools
import time
from typing import Callable, Any

def trace(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Lightweight decorator to trace execution time in debug logs."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        out = fn(*args, **kwargs)
        dt = (time.perf_counter() - t0) * 1e3
        # You can replace print with proper logging if you like.
        # print(f"[TRACE] {fn.__module__}.{fn.__name__} took {dt:.2f} ms")
        return out
    return wrapper