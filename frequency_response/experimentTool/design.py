from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Tuple
import numpy as np

@dataclass(slots=True)
class ModelSpec:
    """Structured model definition for identification tasks.

    G(s) = K Π (1 + s/ωz) / [ s^λ Π (1 + s/ωp) Π (1 + 2ζ s/ωn + (s/ωn)^2) ]
    with an optional transport lag T (handled outside via FRD or Padé).
    """
    K: float = 1.0
    lam: int = 0
    zeros: List[float] | None = None
    poles1: List[float] | None = None
    wns: List[float] | None = None
    zetas: List[float] | None = None
    delay: float = 0.0

    def clean(self) -> None:
        self.zeros  = [] if self.zeros  is None else [float(x) for x in self.zeros]
        self.poles1 = [] if self.poles1 is None else [float(x) for x in self.poles1]
        self.wns    = [] if self.wns    is None else [float(x) for x in self.wns]
        self.zetas  = [] if self.zetas  is None else [float(x) for x in self.zetas]
        if len(self.wns) != len(self.zetas):
            raise ValueError("wns and zetas must have the same length")
        self.lam   = int(self.lam)
        self.K     = float(self.K)
        self.delay = float(self.delay)

    def as_dict(self) -> dict:
        self.clean()
        return asdict(self)

def ogata_7_25() -> ModelSpec:
    """Ogata Example 7-25 canonical preset."""
    return ModelSpec(K=10.0, lam=1, zeros=[2.0], poles1=[1.0], wns=[8.0], zetas=[0.5], delay=0.2)
