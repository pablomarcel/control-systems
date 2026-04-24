
from __future__ import annotations
from functools import wraps
from typing import Callable, Any

def track(src: str, dst: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        wrapper._trace_edge = (src, dst)
        return wrapper
    return deco

def export_trace_metadata(obj: Any) -> list[tuple[str, str]]:
    edges = []
    for name in dir(obj):
        try:
            attr = getattr(obj, name)
        except Exception:
            continue
        if callable(attr) and hasattr(attr, "_trace_edge"):
            edges.append(attr._trace_edge)  # type: ignore[attr-defined]
    return edges
