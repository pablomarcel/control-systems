from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class RunRequest:
    # mode is decided by which fields are present (TF, SS, or BOTH)
    num: Optional[str] = None
    den: Optional[str] = None
    A: Optional[str] = None
    B: Optional[str] = None
    C: Optional[str] = None
    D: Optional[str] = None
    iu: int = 0
    tfinal: float = 8.0
    dt: float = 1e-3
    sympy: bool = False
    no_plot: bool = False
    out_prefix: Optional[str] = None
    log: str = "INFO"
