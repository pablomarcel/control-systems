from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any

@dataclass(slots=True)
class RootLocusRequest:
    # Input (TF / ZPK / G*H / SS)
    poles: Optional[str] = None
    zeros: Optional[str] = None
    kgain: float = 1.0
    num: Optional[str] = None
    den: Optional[str] = None
    Gnum: Optional[str] = None
    Gden: Optional[str] = None
    Hnum: Optional[str] = None
    Hden: Optional[str] = None
    ssA: Optional[str] = None
    ssB: Optional[str] = None
    ssC: Optional[str] = None
    ssD: Optional[str] = None
    io: Optional[Tuple[int, int]] = None

    # K grid
    kpos: Optional[str] = None     # "lo,hi,N,lin|log" or None for auto
    kneg: Optional[str] = None     # "lo,hi" for negative K inclusion
    auto: bool = True

    # s-grid
    sgrid: bool = False
    zeta: Optional[str] = None
    wn: Optional[str] = None
    label_zeta: bool = True
    label_wn: bool = True

    # overlays
    cg: bool = False
    kgains: str = ""
    cg_absL: str = ""
    cg_res: int = 181

    # arrows & limits
    arrows: bool = False
    arrow_every: int = 80
    arrow_scale: float = 0.04
    xlim: Optional[Tuple[float, float]] = None
    ylim: Optional[Tuple[float, float]] = None

    # labels & outputs
    klabels: str = ""
    title: str = "Root–Locus Pro"

@dataclass(slots=True)
class RootLocusBatchSpec:
    cases: List[Dict[str, Any]]
    defaults: Dict[str, Any] = field(default_factory=dict)
    outdir: str = "."
    report: str = "root_locus_report.html"
