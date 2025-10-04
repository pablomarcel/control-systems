
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import os

def parse_list(s: str) -> List[float]:
    if isinstance(s, (list, tuple)):
        return [float(x) for x in s]
    return [float(x.strip()) for x in s.split(",") if str(x).strip()]

def ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

def substitute_kind(path: Optional[str], kind: str) -> Optional[str]:
    if not path:
        return None
    return path.replace("{kind}", kind)

def time_grid(tfinal: float, dt: float) -> np.ndarray:
    n = int(np.floor(tfinal / dt))
    return np.linspace(0.0, n * dt, n + 1)
