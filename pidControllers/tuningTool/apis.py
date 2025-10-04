
# apis.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .design import TuningService
from .utils import TuningInputs, fmt_num
from .core import TuningResult

@dataclass(slots=True)
class PrintAPI:
    """Presentation helpers for console/UI output."""
    def render_text(self, res: TuningResult, precision: int = 6) -> str:
        lines: list[str] = []
        lines.append(f"Ziegler–Nichols → {res.method} • {res.controller}")
        if res.inputs:
            ins = ", ".join(f"{k}={fmt_num(v, precision)}" for k, v in res.inputs.items())
            lines.append(f"Inputs: {ins}")
        lines.append("Ideal form: Gc(s) = Kp * (1 + 1/(Ti s) + Td s)")
        lines.append("Gains: " + ", ".join([
            f"Kp={fmt_num(res.Kp, precision)}",
            f"Ti={fmt_num(res.Ti, precision)}",
            f"Td={fmt_num(res.Td, precision)}",
            f"Ki={fmt_num(res.Ki, precision)}",
            f"Kd={fmt_num(res.Kd, precision)}",
        ]))
        if res.controller_zeros_location is not None:
            lines.append(
                f"Implied controller zeros: s = {fmt_num(res.controller_zeros_location, precision)}"
                + (f"  (mult={res.controller_zeros_multiplicity})" if res.controller_zeros_multiplicity else "")
            )
        return "\n".join(lines)

@dataclass(slots=True)
class ExportAPI:
    def to_json(self, res: TuningResult) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "method": res.method,
            "controller": res.controller,
            "inputs": res.inputs,
            "Kp": res.Kp, "Ti": res.Ti, "Td": res.Td, "Ki": res.Ki, "Kd": res.Kd,
        }
        if res.controller_zeros_location is not None:
            d["controller_zeros"] = {
                "location": res.controller_zeros_location,
                "multiplicity": res.controller_zeros_multiplicity,
            }
        return d
