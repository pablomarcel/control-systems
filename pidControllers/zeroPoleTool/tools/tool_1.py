"""Reserved for future helpers (e.g., UML exporters, decorators)."""
from __future__ import annotations

def trace(label: str):
    def deco(fn):
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        wrapper.__doc__ = fn.__doc__
        return wrapper
    return deco
