# modernControl/root_locus_analysis/compensatorTool/tools/tool_logging.py
from __future__ import annotations
import time
from functools import wraps
from typing import Callable, Any


def track(label: str):
    """Lightweight timing decorator for tracing critical methods in tests/logs."""
    def deco(fn: Callable[..., Any]):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            try:
                return fn(*args, **kwargs)
            finally:
                dt = (time.perf_counter() - t0) * 1000
                print(f"[track] {label}: {dt:.2f} ms")
        return wrapper
    return deco