from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import numpy as np

class ServoMode(str, Enum):
    K  = "K"   # plant already has an integrator
    KI = "KI"  # add integrator via augmented design

@dataclass
class ControllerPayload:
    """Controller JSON produced by `gain_matrix.py` (mode=K or KI)."""
    mode: ServoMode
    A: np.ndarray
    B: np.ndarray
    C: Optional[np.ndarray] = None
    K: Optional[np.ndarray] = None
    kI: Optional[float] = None
    state_names: Optional[List[str]] = None
    output_names: Optional[List[str]] = None

@dataclass
class ServoIOModel:
    """Resulting I/O model for step-to-reference."""
    mode: ServoMode
    Acl: np.ndarray  # closed-loop (or augmented) A matrix
    Bcl: np.ndarray  # input vector for reference step
    C: np.ndarray
    D: np.ndarray
    r: float
    k_r: Optional[float] = None
    kI: Optional[float] = None
    state_names: List[str] = field(default_factory=list)
    output_names: List[str] = field(default_factory=list)

    def to_jsonable(self) -> dict:
        def tj(x):
            arr = np.array(x, dtype=float)
            arr = np.real_if_close(arr, tol=1e8)
            if np.iscomplexobj(arr):
                arr = np.real(arr)
            if arr.ndim == 0:
                return float(arr)
            return arr.tolist()
        payload = {
            "kind": "io",
            "source": "stateSpaceDesign.servoTool",
            "mode": self.mode.value,
            "Acl": tj(self.Acl),
            "Bcl": tj(self.Bcl),
            "C":   tj(self.C),
            "D":   tj(self.D),
            "r":   float(self.r),
            "state_names": list(self.state_names),
            "output_names": list(self.output_names),
        }
        if self.k_r is not None:
            payload["k_r"] = float(self.k_r)
        if self.kI is not None:
            payload["kI"] = float(self.kI)
        return payload
