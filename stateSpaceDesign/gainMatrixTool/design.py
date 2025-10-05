from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List
import numpy as np
from .core import GainMatrixDesigner, parse_matrix, parse_poles_arg
from .utils import to_jsonable

@dataclass
class DesignService:
    """High-level service orchestrating single-case gain designs."""
    designer: GainMatrixDesigner

    def run_single(self, mode: str, A: str, B: str|None, C: str|None, poles, method: str, verify: bool, pretty: bool) -> Dict[str, Any]:
        A_m = parse_matrix(A)
        if mode == "K":
            B_m = parse_matrix(B)
            res = self.designer.design_K(A_m, B_m, parse_poles_arg(poles), method, verify, pretty)
        elif mode == "L":
            C_m = parse_matrix(C)
            res = self.designer.design_L(A_m, C_m, parse_poles_arg(poles), method, verify, pretty)
        elif mode == "KI":
            B_m = parse_matrix(B); C_m = parse_matrix(C)
            res = self.designer.design_KI(A_m, B_m, C_m, parse_poles_arg(poles), method, verify, pretty)
        else:
            raise SystemExit("Unknown mode")
        return res.payload
