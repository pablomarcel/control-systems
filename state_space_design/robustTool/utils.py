from __future__ import annotations

import functools
import logging
import re
import time
from typing import Any, Callable, Iterable, Optional

__all__ = ["parse_vec", "log_calls"]


def parse_vec(s: Optional[str]) -> list[float]:
    """
    Convert a string like "1, 2  3" into a list of floats [1.0, 2.0, 3.0].
    - Accepts commas and/or whitespace as separators.
    - Returns [] for None or empty strings.
    - Ignores empty tokens safely.
    """
    if not s:
        return []
    # Normalize commas -> spaces, then split on any whitespace
    s_norm = s.strip().replace(",", " ")
    tokens = re.split(r"\s+", s_norm)
    out: list[float] = []
    for t in tokens:
        if not t:
            continue
        # Allow leading/trailing plus (e.g., "+1.0")
        out.append(float(t))
    return out


def log_calls(
    logger: Optional[logging.Logger] = None,
    *,
    ok_level: int = logging.DEBUG,
    fail_level: int = logging.DEBUG,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator that logs function entry/exit and elapsed time.

    • On entry: logs arguments at DEBUG.
    • On success: logs elapsed time at `ok_level` (default DEBUG).
    • On failure: logs elapsed time + exception *at DEBUG with traceback*
      (default `fail_level` = DEBUG) and re-raises.
      This avoids noisy ERROR logs in test output while keeping full trace.

    Parameters
    ----------
    logger : logging.Logger | None
        If provided, use this logger; otherwise use module logger.
    ok_level : int
        Logging level for successful return (default: DEBUG).
    fail_level : int
        Logging level for failure path (default: DEBUG).

    Returns
    -------
    Callable
        Wrapped function with logging.
    """
    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        name = fn.__qualname__

        @functools.wraps(fn)
        def wrapper(*a: Any, **k: Any) -> Any:
            log = logger or logging.getLogger(__name__)
            t0 = time.perf_counter()
            log.debug("→ %s args=%s kwargs=%s", name, a, k)
            try:
                out = fn(*a, **k)
                dt_ms = (time.perf_counter() - t0) * 1000.0
                log.log(ok_level, "← %s ok in %.2f ms", name, dt_ms)
                return out
            except Exception as e:
                dt_ms = (time.perf_counter() - t0) * 1000.0
                # Use DEBUG (with traceback) so tests capture it without noisy ERROR lines.
                log.log(fail_level, "← %s FAIL in %.2f ms: %s", name, dt_ms, e, exc_info=True)
                raise

        return wrapper

    return deco
