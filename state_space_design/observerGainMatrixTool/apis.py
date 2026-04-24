from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class ObserverRequest:
    A: str
    C: str
    poles: List[complex]
    method: str = "auto"
    place_fallback: str = "none"
    jitter_eps: float = 1e-6
    # Optional controller / closed-loop
    B: Optional[str] = None
    K: Optional[str] = None
    K_poles_csv: Optional[str] = None
    K_poles_list: Optional[List[str]] = None
    compute_closed_loop: bool = False
    x0: Optional[str] = None
    e0: Optional[str] = None
    t_final: float = 0.0
    dt: float = 0.01
    pretty: bool = False
    equations: bool = False
    eq_style: str = "auto"
    latex_out: Optional[str] = None

@dataclass
class ObserverResponse:
    data: Dict[str, Any] = field(default_factory=dict)
    pretty_blocks: List[str] = field(default_factory=list)
