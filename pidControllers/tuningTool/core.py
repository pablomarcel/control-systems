# core.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import math
from .tools.tool_expr import safe_eval
from .utils import TuningInputs

@dataclass(frozen=True, slots=True)
class TuningResult:
    method: str
    controller: str
    inputs: Dict[str, float]
    Kp: float
    Ti: float
    Td: float
    Ki: float
    Kd: float
    controller_zeros_location: float | None = None
    controller_zeros_multiplicity: int | None = None

class TuningEngine:
    """Pure compute engine: evaluate formulas and return TuningResult."""

    def compute(self, rules: Dict[str, Any], method: str, controller: str, inputs: TuningInputs) -> TuningResult:
        try:
            mblk = rules["methods"][method]
        except KeyError:
            raise KeyError(f"Unknown method '{method}'. Available: {list(rules.get('methods', {}).keys())}")
        try:
            cblk = mblk["controllers"][controller]
        except KeyError:
            raise KeyError(f"Unknown controller '{controller}'. Available: {list(mblk.get('controllers', {}).keys())}")

        f = cblk["formula"]
        ctx = inputs.to_ctx()

        # Evaluate primary terms
        Kp = float(safe_eval(f["Kp"], ctx))
        Ti = float(safe_eval(f["Ti"], ctx))
        Td = float(safe_eval(f["Td"], ctx))

        # Derived terms
        derived = cblk.get("derived", {})
        if derived:
            try:
                Ki = float(safe_eval(derived.get("Ki", "Kp/Ti"), {**ctx, "Kp": Kp, "Ti": Ti, "Td": Td}))
            except Exception:
                Ki = (Kp / Ti) if (math.isfinite(Ti) and Ti != 0.0) else 0.0
            try:
                Kd = float(safe_eval(derived.get("Kd", "Kp*Td"), {**ctx, "Kp": Kp, "Ti": Ti, "Td": Td}))
            except Exception:
                Kd = Kp * Td
        else:
            # Fallback if no 'derived' block
            if math.isfinite(Ti) and Ti != 0.0:
                Ki = Kp / Ti
            else:
                Ki = 0.0
            Kd = Kp * Td

        # Optional zeros
        cz_loc = None
        cz_mult = None
        iz = cblk.get("implied_zero_info")
        if iz and "location" in iz:
            try:
                cz_loc = float(safe_eval(iz["location"], ctx))
            except Exception:
                cz_loc = None
            cz_mult = int(iz.get("multiplicity")) if iz and "multiplicity" in iz else None

        used_inputs = {k: v for k, v in ctx.items() if k in ("L", "T", "Kcr", "Pcr") and v is not None}
        return TuningResult(
            method=method, controller=controller, inputs=used_inputs,
            Kp=Kp, Ti=Ti, Td=Td, Ki=Ki, Kd=Kd,
            controller_zeros_location=cz_loc, controller_zeros_multiplicity=cz_mult
        )
