
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
from .apis import ZeroPoleAPI, DesignRequest

@dataclass(slots=True)
class AppConfig:
    # Plant description
    plant_form: str = "coeff"
    num: Optional[str] = None
    den: Optional[str] = None
    num_poly: Optional[str] = None
    den_poly: Optional[str] = None
    gain: Optional[float] = None
    zeros: Optional[str] = None
    poles: Optional[str] = None

    # Architecture & grids
    arch: str = "fig8-31"
    a_vals: Optional[str] = None; b_vals: Optional[str] = None; c_vals: Optional[str] = None
    a_range: Optional[Tuple[float,float]] = None; a_n: Optional[int] = None
    b_range: Optional[Tuple[float,float]] = None; b_n: Optional[int] = None
    c_range: Optional[Tuple[float,float]] = None; c_n: Optional[int] = None

    # Specs & behavior
    os_min: float = 0.0; os_max: float = 100.0; ts_max: float = 10.0; settle_tol: float = 0.02
    best_effort: bool = False
    export_json: bool = False; export_csv: bool = False
    plots: List[str] = None
    no_progress: bool = False
    debug: bool = False
    rank_dist_peak_weight: float = 0.0
    save_prefix: str = "zp_design"
    plot_prefix: str = "zp_design"

class ZeroPoleApp:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg

    def run(self):
        req = DesignRequest(
            # Plant
            plant_form=self.cfg.plant_form,
            num=self.cfg.num, den=self.cfg.den,
            num_poly=self.cfg.num_poly, den_poly=self.cfg.den_poly,
            gain=self.cfg.gain, zeros=self.cfg.zeros, poles=self.cfg.poles,
            # Arch & grids
            arch=self.cfg.arch,
            a_vals=self.cfg.a_vals, b_vals=self.cfg.b_vals, c_vals=self.cfg.c_vals,
            a_range=self.cfg.a_range, a_n=self.cfg.a_n,
            b_range=self.cfg.b_range, b_n=self.cfg.b_n,
            c_range=self.cfg.c_range, c_n=self.cfg.c_n,
            # Specs & behavior
            os_min=self.cfg.os_min, os_max=self.cfg.os_max,
            ts_max=self.cfg.ts_max, settle_tol=self.cfg.settle_tol,
            rank_dist_peak_weight=self.cfg.rank_dist_peak_weight,
            export_json=self.cfg.export_json, export_csv=self.cfg.export_csv,
            plots=self.cfg.plots or [], best_effort=self.cfg.best_effort,
            no_progress=self.cfg.no_progress, debug=self.cfg.debug,
            save_prefix=self.cfg.save_prefix, plot_prefix=self.cfg.plot_prefix,
        )
        return ZeroPoleAPI.run(req)
