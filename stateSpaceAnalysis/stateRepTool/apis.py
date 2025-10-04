from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
import sympy as sp
from .core import TransferFunctionSpec, CanonicalFormCalculator

@dataclass
class StateRepAPIRequest:
    tf: str | None = None
    num: str | None = None
    den: str | None = None
    example: str | None = None
    which: str = "all"
    numeric: bool = False
    digits: int = 6
    pretty: bool = False
    verify: bool = True

@dataclass
class StateRepAPIResponse:
    results: Dict[str, dict]

class StateRepService:
    @staticmethod
    def _build_spec(req: StateRepAPIRequest) -> TransferFunctionSpec:
        if req.example == "ogata_9_1":
            return TransferFunctionSpec.from_tf_string("(s+3)/(s^2+3*s+2)")
        if req.tf:
            return TransferFunctionSpec.from_tf_string(req.tf)
        if req.num and req.den:
            return TransferFunctionSpec.from_num_den(req.num, req.den)
        raise ValueError("Provide example, tf, or (num, den).")

    @staticmethod
    def run(req: StateRepAPIRequest) -> StateRepAPIResponse:
        spec = StateRepService._build_spec(req)
        calc = CanonicalFormCalculator(
            tf=spec, numeric=req.numeric, digits=req.digits,
            pretty=req.pretty, verify=req.verify
        )
        reals = calc.compute(which=req.which)
        payload = {k: v.as_dict() for k, v in reals.items()}
        return StateRepAPIResponse(results=payload)
