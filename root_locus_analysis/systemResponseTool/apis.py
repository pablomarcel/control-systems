# root_locus_analysis/systemResponseTool/apis.py
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import numpy as np

from .app import SystemResponseApp
from .core import Responses, ICMode
from .utils import make_logger

log = make_logger(__name__)


# -------------------------- DTOs --------------------------

@dataclass(slots=True)
class RunRequest:
    # systems
    sys_args: List[str]
    # which responses to run
    responses: List[str]

    # time grid
    tfinal: float = 5.0
    dt: float = 0.005

    # presentation
    title: str = ""
    out_prefix: Optional[str] = None

    # arbitrary input options
    arb_kind: str = "ramp"          # ramp|sine|square|expr|file
    arb_amp: float = 1.0
    arb_freq: float = 0.5
    arb_duty: float = 0.5
    arb_expr: str = "sin(2*pi*0.5*t)+0.3*sin(2*pi*2*t)"
    arb_file: str = ""
    show_input: bool = False

    # initial-condition overlay
    ic_compare: bool = True


# ---------------------- Service layer ----------------------

def _time_grid(tfinal: float, dt: float) -> np.ndarray:
    n = int(np.floor(tfinal / dt)) + 1
    return np.linspace(0.0, tfinal, n)


@dataclass(slots=True)
class SystemResponseService:
    in_dir: Path
    out_dir: Path
    show_plots: bool = True

    # important: slotted fields that are set in __post_init__
    app: SystemResponseApp = field(init=False)

    def __post_init__(self):
        self.in_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.app = SystemResponseApp(self.in_dir, self.out_dir, self.show_plots)

    def run(self, req: RunRequest) -> None:
        """
        Execute all requested responses using the application layer.
        """
        # Parse systems once
        specs = self.app.parse_systems(req.sys_args)

        # Build uniform time grid
        T = _time_grid(req.tfinal, req.dt)

        # Normalize response tokens
        want = [r.strip().lower() for r in req.responses if r.strip()]

        for r in want:
            if r == Responses.STEP.value:
                self.app.run_step(
                    specs, T,
                    title=(req.title or "STEP response"),
                    out_prefix=req.out_prefix,
                )
            elif r == Responses.IMPULSE.value:
                self.app.run_impulse(
                    specs, T,
                    title=(req.title or "IMPULSE response"),
                    out_prefix=req.out_prefix,
                )
            elif r == Responses.RAMP.value:
                self.app.run_ramp(
                    specs, T,
                    title=(req.title or "RAMP response"),
                    out_prefix=req.out_prefix,
                    show_input=req.show_input,
                )
            elif r == Responses.ARB.value:
                self.app.run_arb(
                    specs, T,
                    kind=req.arb_kind,
                    amp=req.arb_amp,
                    freq=req.arb_freq,
                    duty=req.arb_duty,
                    expr=req.arb_expr,
                    file_path=req.arb_file,
                    show_input=req.show_input,
                    title=(req.title or None) or f"ARBITRARY response — {req.arb_kind}",
                    out_prefix=req.out_prefix,
                )
            elif r == Responses.IC1.value:
                self.app.run_ic(
                    specs, T,
                    which=ICMode.IC1,
                    compare=req.ic_compare,
                    title=(req.title or "IC Case 1 — states from x(0)"),
                    out_prefix=req.out_prefix,
                )
            elif r == Responses.IC2.value:
                self.app.run_ic(
                    specs, T,
                    which=ICMode.IC2,
                    compare=req.ic_compare,
                    title=(req.title or "IC Case 2 — outputs from x(0)"),
                    out_prefix=req.out_prefix,
                )
            else:
                log.error("Unknown response '%s'", r)
