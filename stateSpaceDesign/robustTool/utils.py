from __future__ import annotations
from typing import Iterable, Callable, Any
import functools, time, logging

def parse_vec(s: str) -> list[float]:
    s = (s or "").strip().replace(",", " ")
    return [float(t) for t in s.split() if t]

def log_calls(logger: Callable[..., Any] | None = None):
    """Decorator: log function enter/exit with elapsed ms."""
    def deco(fn):
        name = fn.__qualname__
        @functools.wraps(fn)
        def wrapper(*a, **k):
            log = logger or logging.getLogger(__name__)
            t0 = time.perf_counter()
            log.debug(f"→ {name} args={a} kwargs={k}")
            try:
                out = fn(*a, **k)
                dt = (time.perf_counter() - t0)*1000
                log.debug(f"← {name} ok in {dt:.2f} ms")
                return out
            except Exception as e:
                dt = (time.perf_counter() - t0)*1000
                log.exception(f"← {name} FAIL in {dt:.2f} ms: {e}")
                raise
        return wrapper
    return deco
