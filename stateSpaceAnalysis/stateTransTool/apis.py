from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
import sympy as sp

@dataclass
class StateTransRequest:
    # Input transfer function (choose exactly one path)
    tf: Optional[str] = None
    num: Optional[str] = None
    den: Optional[str] = None
    example: Optional[str] = None  # e.g., "ogata_9_1"
    # Options
    canonical: str = "controllable"  # controllable | observable | diagonal | jordan
    eval_time: Optional[float] = None
    inverse: bool = False
    numeric: bool = False
    digits: int = 8
    pretty: bool = False
    export_json: Optional[str] = None  # path to write JSON (Φ(t), and Φ^{-1}(t) if requested)
    log_level: str = "INFO"

@dataclass
class StateTransResult:
    A: sp.Matrix
    canonical: str
    Phi: sp.Matrix
    Phi_inv: Optional[sp.Matrix] = None
    Phi_eval: Optional[sp.Matrix] = None
    Phi_inv_eval: Optional[sp.Matrix] = None
    messages: List[str] = field(default_factory=list)

