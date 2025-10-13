
from __future__ import annotations
import logging
import numpy as np

def setup_logger(level: int | str = logging.INFO) -> None:
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("control").setLevel(logging.WARNING)

def clip_small(a, tol: float = 1e-12):
    arr = np.asarray(a, dtype=float).copy()
    arr[np.abs(arr) < tol] = 0.0
    return arr
