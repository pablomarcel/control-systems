"""
Public APIs and dataclasses that are CLI- and test-friendly.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional, List
import numpy as np

from .design import PlantFactory
from .core import MIMOSystem
from .io import save_current_fig

PlantName = Literal["two_tank", "two_zone_thermal"]

@dataclass
class DescribeRequest:
    plant: PlantName

@dataclass
class StepRequest:
    plant: PlantName
    tfinal: float = 100.0
    dt: float = 0.1
    save: bool = False
    out_prefix: Optional[str] = None

@dataclass
class SigmaRequest:
    plant: PlantName
    w_min: float = 1e-3
    w_max: float = 10**1.5
    n_pts: int = 400
    save: bool = False
    out_name: Optional[str] = None

def get_plant(plant: PlantName) -> MIMOSystem:
    if plant == "two_tank":
        return PlantFactory.two_tank()
    elif plant == "two_zone_thermal":
        return PlantFactory.two_zone_thermal()
    else:  # pragma: no cover
        raise ValueError(f"Unknown plant {plant}")

# -------------
# API functions
# -------------
def describe(req: DescribeRequest) -> dict:
    sys = get_plant(req.plant)
    return {
        "A": sys.A.tolist(),
        "B": sys.B.tolist(),
        "C": sys.C.tolist(),
        "D": sys.D.tolist(),
        "poles": [complex(p).real if abs(getattr(p, "imag", 0))<1e-14 else complex(p) for p in sys.poles()],
        "ninputs": sys.ninputs,
        "noutputs": sys.noutputs,
    }

def steps(req: StepRequest) -> List[str]:
    sys = get_plant(req.plant)
    paths: List[str] = []
    for u in range(sys.ninputs):
        sys.plot_steps_for_each_input(tfinal=req.tfinal, dt=req.dt, title_prefix=req.plant.replace("_"," ").title())
        if req.save:
            name = f"{req.out_prefix or req.plant}_step_u{u+1}.png"
            paths.append(save_current_fig(name))
    return paths

def sigma(req: SigmaRequest) -> str | None:
    sys = get_plant(req.plant)
    w = np.logspace(np.log10(req.w_min), np.log10(req.w_max), req.n_pts)
    sys.plot_sigma(title=f"{req.plant.replace('_',' ').title()}: σ(G(jω))")
    if req.save:
        name = req.out_name or f"{req.plant}_sigma.png"
        return save_current_fig(name)
    return None
