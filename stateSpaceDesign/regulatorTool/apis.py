#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apis.py — public API (service layer) for programmatic use and the CLI.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
import numpy as np
import control as ct
import logging

from .core import Plant, RegulatorParams, SimulationSpec, RegulatorDesignResult, Signals
from .design import PlantFactory, RegulatorDesigner
from .io import out_path, save_json

@dataclass
class RegulatorRunRequest:
    num: np.ndarray
    den: np.ndarray
    K_poles: Optional[np.ndarray] = None
    obs_poles: Optional[np.ndarray] = None
    ts: Optional[float] = None
    undershoot: Optional[Tuple[float, float]] = None
    obs_speed_factor: float = 5.0
    x0: Optional[np.ndarray] = None
    e0: Optional[np.ndarray] = None
    t_final: float = 8.0
    dt: float = 0.01
    rl_axes: Tuple[float, float, float, float] = (-14.0, 2.0, -8.0, 8.0)
    rl_k: str = "auto"
    pretty: bool = False
    plots: str = "both"        # "none" | "mpl" | "plotly" | "both"
    save_prefix: Optional[str] = None
    export_json: Optional[str] = None
    ply_width: int = 0
    verbose: bool = False

class RegulatorService:
    def __init__(self, req: RegulatorRunRequest):
        self.req = req
        self.plant = PlantFactory.from_tf(req.num, req.den)
        self.designer = RegulatorDesigner(self.plant, RegulatorParams(
            K_poles=req.K_poles, obs_poles=req.obs_poles,
            ts=req.ts, undershoot=req.undershoot, obs_speed_factor=req.obs_speed_factor
        ))

    def run(self) -> Dict[str, Any]:
        logging.info("== Regulator with Minimum-Order Observer (Ogata §10-6) ==")

        design = self.designer.run()
        sim = self.designer.simulate_initial(design, SimulationSpec(
            x0=self.req.x0, e0=self.req.e0, t_final=self.req.t_final, dt=self.req.dt))

        # Export JSON if requested
        if self.req.export_json:
            path = self.req.export_json
            if not (path.endswith(".json") or path.endswith(".JSON")):
                path = out_path(f"{path}.json")
            payload = {
                "A": self.plant.A.tolist(), "B": self.plant.B.tolist(), "C": self.plant.C.tolist(),
                "K": design.K.tolist(), "Ke": design.Ke.tolist(),
                "Ahat": design.Ahat.tolist(), "Bhat": design.Bhat.tolist(), "Fhat": design.Fhat.tolist(),
                "Atil": design.Atil.tolist(), "Btil": design.Btil.tolist(), "Ctil": design.Ctil.tolist(), "Dtil": design.Dtil.tolist(),
                "Gc_num": np.asarray(design.Gc.num[0][0], float).tolist(),
                "Gc_den": np.asarray(design.Gc.den[0][0], float).tolist(),
                "L_num": np.asarray(design.L.num[0][0], float).tolist(),
                "L_den": np.asarray(design.L.den[0][0], float).tolist()
            }
            save_json(payload, path)
            logging.info("Saved JSON → %s", path)

        # Optional plots are handled in app/cli layer to avoid heavy deps here.

        return {
            "plant": self.plant,
            "design": design,
            "sim": sim
        }
