from __future__ import annotations
import os, math
from typing import Optional, Iterable, List

def ensure_out_path(path: Optional[str]) -> Optional[str]:
    """Return an absolute/ensured path under ./out if `path` is relative."""
    if path is None:
        return None
    if not os.path.isabs(path):
        os.makedirs("out", exist_ok=True)
        path = os.path.join("out", path)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    return path

def parse_poly(arg: Optional[str | Iterable[float]]) -> List[float] | None:
    if arg is None:
        return None
    if isinstance(arg, (list, tuple)):
        return [float(x) for x in arg]
    parts = [p for p in str(arg).replace(',', ' ').split() if p.strip()]
    return [float(p) for p in parts]

def complex_arg(z: complex) -> float:
    return math.atan2(z.imag, z.real)
