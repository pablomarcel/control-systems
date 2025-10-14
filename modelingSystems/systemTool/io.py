from __future__ import annotations
import ast
import numpy as np
from typing import Iterable

def parse_list(text: str) -> list[float]:
    return list(ast.literal_eval(text))

def parse_matrix(text: str) -> np.ndarray:
    arr = np.array(ast.literal_eval(text), dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    return arr

def ensure_1d(arr_like: Iterable[float]) -> np.ndarray:
    import numpy as np
    return np.asarray(list(arr_like), dtype=float).ravel()
