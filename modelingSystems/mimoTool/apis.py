
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Literal, List, Optional, Dict, Any
import numpy as np

PlantName = Literal["two_tank", "two_zone_thermal"]

@dataclass(frozen=True)
class RunConfig:
    plants: List[PlantName]
    # time-domain
    tfinal: float = 200.0
    dt: float = 0.25
    # frequency-domain
    wmin: float = 1e-3
    wmax: float = 10**1.5
    npts: int = 400
    # plotting
    plot_steps: bool = True
    plot_sigma: bool = True
    show: bool = True
    # outputs
    save_png: Optional[str] = None   # e.g., "out/{plant}_{kind}.png"
    save_json: Optional[str] = None  # e.g., "out/{plant}_summary.json"
    title_prefix: str = "Step"

    def wgrid(self) -> np.ndarray:
        return np.logspace(np.log10(self.wmin), np.log10(self.wmax), int(self.npts))

@dataclass
class PlantSummary:
    name: PlantName
    poles: list

@dataclass
class RunResult:
    summaries: List[PlantSummary]

    def to_jsonable(self) -> Dict[str, Any]:
        return {"summaries": [asdict(s) for s in self.summaries]}
