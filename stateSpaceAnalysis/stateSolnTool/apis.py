
# apis.py — dataclasses for requests / responses
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class SolveRequest:
    # Transfer function input
    tf: Optional[str] = None
    num: Optional[str] = None
    den: Optional[str] = None
    example: Optional[str] = None  # "ogata_9_1"
    # Options
    canonical: str = "controllable"  # controllable|observable|diagonal|jordan
    u: str = "1"
    x0: Optional[str] = None
    t0: float = 0.0
    eval_time: Optional[float] = None
    numeric: bool = False
    digits: int = 8
    pretty: bool = False
    export_json: Optional[str] = None
    verify: bool = False
    tol: float = 1e-9
    log_level: str = "INFO"

@dataclass
class SolveResponse:
    A: str
    B: str
    Phi: str
    x_hom: str
    x_part: str
    x: str
    verification: Optional[str] = None
