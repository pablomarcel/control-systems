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
        # Expect the first positional arg after self to be the model
        model = kwargs.get('model', args[0] if len(args) > 0 else None)
        if model is None:
            return fn(self, *args, **kwargs)
        rS = controllability_rank(model.A, model.B)
        if rS < model.A.shape[0]:
            print(f"WARN: rank(S)={rS} < n={model.A.shape[0]} — system not fully controllable.")
        return fn(self, *args, **kwargs)
    return wrapper
