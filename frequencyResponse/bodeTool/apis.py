from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple

@dataclass(frozen=True)
class Margins:
    gm: float
    pm: float
    wgc: float
    wpc: float
    gm_db: float

@dataclass(frozen=True)
class ClosedLoopFR:
    wb: float
    Mr_db: float
    wr: float

@dataclass(frozen=True)
class AnalysisResult:
    pretty_tf: str
    margins: Margins
    closedloop: ClosedLoopFR
    P: int
    hints: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class BodeConfig:
    # G(s)
    num: str | None = None
    den: str | None = None
    gain: float | None = None
    zeros: str | None = None
    poles: str | None = None
    fnum: str | None = None
    fden: str | None = None
    K: float = 1.0

    # H(s)
    hnum: str | None = None
    hden: str | None = None
    hgain: float | None = None
    hzeros: str | None = None
    hpoles: str | None = None
    hfnum: str | None = None
    hfden: str | None = None
    hK: float = 1.0

    # frequency grid
    wmin: float | None = None
    wmax: float | None = None
    npts: int = 2000

    # outputs/plots
    bode: bool = False
    nyquist: bool = False
    nichols: bool = False
    step: bool = False
    plotly: bool = False
    save_png: str | None = None
    save_html: str | None = None
    save_json: str | None = None
    title: str = "Bode of L(s)"
    verbose: int = 0
