# utils.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import math

def fmt_num(x: float | int | str, digits: int = 6) -> str:
    try:
        if isinstance(x, (int, float)):
            if isinstance(x, float) and math.isinf(x):
                return "inf"
            return f"{x:.{digits}g}"
        return str(x)
    except Exception:
        return str(x)

@dataclass(frozen=True, slots=True)
class TuningInputs:
    # Context used by rule evaluation
    L: float | None = None
    T: float | None = None
    Kcr: float | None = None
    Pcr: float | None = None

    def to_ctx(self) -> Dict[str, Any]:
        ctx: Dict[str, Any] = {"inf": float("inf")}
        if self.L is not None: ctx["L"] = float(self.L)
        if self.T is not None: ctx["T"] = float(self.T)
        if self.Kcr is not None: ctx["Kcr"] = float(self.Kcr)
        if self.Pcr is not None: ctx["Pcr"] = float(self.Pcr)
        return ctx
