from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Literal, Dict, Any
import numpy as np

PlotsMode = Literal["mpl", "plotly", "both", "none"]
PrefilterMode = Literal["ogata", "dcgain", "none"]

@dataclass
class LQRRunRequest:
    # system definition (exclusive OR between tf and abcd paths)
    A: Optional[str] = None
    B: Optional[str] = None
    C: Optional[str] = None
    D: Optional[str] = "0"
    num: Optional[str] = None
    den: Optional[str] = None
    # weights
    Q: str = "eye"
    R: str = "1"
    # simulations
    x0: Optional[str] = None
    step: bool = False
    step_amp: float = 1.0
    prefilter: PrefilterMode = "dcgain"
    tfinal: float = 8.0
    dt: float = 0.01
    # output
    plots: PlotsMode = "mpl"

    def to_jsonable(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass
class LQRRunResult:
    K: list
    P: list
    eig_cl: list
    prefilter_gain: float | None
    rank_ctrb: int
    note: str = ""

    def to_jsonable(self) -> Dict[str, Any]:
        return {
            "K": self.K,
            "P": self.P,
            "eig": self.eig_cl,
            "prefilter_gain": self.prefilter_gain,
            "rank_ctrb": self.rank_ctrb,
            "note": self.note,
        }
