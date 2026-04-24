# -*- coding: utf-8 -*-
"""
Thin API for programmatic access, wrapping the app in a stable surface.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
from .app import ControllerToolApp, DesignInputs, BuildConfig, BuildResult

@dataclass
class RunRequest:
    num: str
    den: str
    K_poles: Optional[str] = None
    obs_poles: Optional[str] = None
    cfg: str = "both"
    ts: Optional[float] = None
    undershoot: Optional[Tuple[float, float]] = None
    obs_speed_factor: float = 5.0

@dataclass
class RunResponse:
    result: BuildResult

def run(req: RunRequest) -> RunResponse:
    from .utils import parse_real_vec, parse_complex_list
    din = DesignInputs(
        num=parse_real_vec(req.num),
        den=parse_real_vec(req.den),
        K_poles=(parse_complex_list(req.K_poles) if req.K_poles else None),
        obs_poles=(parse_complex_list(req.obs_poles) if req.obs_poles else None),
        ts=req.ts,
        undershoot=req.undershoot,
        obs_speed_factor=req.obs_speed_factor,
    )
    app = ControllerToolApp(din, BuildConfig(cfg=req.cfg))
    result = app.build()
    return RunResponse(result=result)
