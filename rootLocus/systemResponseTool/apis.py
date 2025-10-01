# rootLocus/systemResponseTool/apis.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import numpy as np

from .app import SystemResponseApp
from .core import ICMode

@dataclass(slots=True)
class RunRequest:
    sys_args: List[str]
    responses: List[str]               # ["step", "ramp", "impulse", "arb", "ic1", "ic2"]
    tfinal: float
    dt: float
    title: str = ""
    out_prefix: Optional[str] = None
    # arb
    arb_kind: str = "ramp"
    arb_amp: float = 1.0
    arb_freq: float = 0.5
    arb_duty: float = 0.5
    arb_expr: str = "sin(2*pi*0.5*t)+0.3*sin(2*pi*2*t)"
    arb_file: str = ""
    show_input: bool = False
    # ic
    ic_compare: bool = True

@dataclass(slots=True)
class SystemResponseService:
    in_dir: Path
    out_dir: Path
    show_plots: bool = True

    def __post_init__(self):
        self.app = SystemResponseApp(self.in_dir, self.out_dir, self.show_plots)

    def run(self, req: RunRequest):
        specs = self.app.parse_systems(req.sys_args)
        T = np.linspace(0.0, req.tfinal, int(req.tfinal / req.dt) + 1)

        for r in req.responses:
            if r == "step":
                self.app.run_step(specs, T, req.title, req.out_prefix)
            elif r == "impulse":
                self.app.run_impulse(specs, T, req.title, req.out_prefix)
            elif r == "ramp":
                self.app.run_ramp(specs, T, req.title, req.out_prefix, req.show_input)
            elif r == "arb":
                self.app.run_arb(
                    specs, T, kind=req.arb_kind, amp=req.arb_amp, freq=req.arb_freq,
                    duty=req.arb_duty, expr=req.arb_expr, file_path=req.arb_file,
                    show_input=req.show_input, title=req.title, out_prefix=req.out_prefix
                )
            elif r in ("ic1", "ic2"):
                self.app.run_ic(
                    specs, T, which=(ICMode.IC1 if r == "ic1" else ICMode.IC2),
                    compare=req.ic_compare, title=req.title, out_prefix=req.out_prefix
                )
            else:
                raise ValueError(f"Unknown response '{r}'")
