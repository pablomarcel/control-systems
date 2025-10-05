from __future__ import annotations
from functools import wraps
from typing import Callable
import numpy as np
import control as ct

def controllability_rank(A, B) -> int:
    S = ct.ctrb(A, B)
    return int(np.linalg.matrix_rank(S))

def ensure_controllable(fn: Callable):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        rS = controllability_rank(self.model.A, self.model.B)
        if rS < self.model.A.shape[0]:
            # Only warn (allow stabilizable cases); tests can assert this path
            print(f"WARN: rank(S)={rS} < n={self.model.A.shape[0]} — system not fully controllable.")
        return fn(self, *args, **kwargs)
    return wrapper
