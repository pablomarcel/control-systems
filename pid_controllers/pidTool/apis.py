from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple

@dataclass(slots=True)
class RunRequest:
    plant_form: str
    num: str | None = None
    den: str | None = None
    num_poly: str | None = None
    den_poly: str | None = None
    gain: float | None = None
    zeros: str | None = None
    poles: str | None = None

    structure: str = "pid_dz"
    objective: str = "itae"
    weights: Tuple[float, float, float, float] = (1.0, 0.1, 1.0, 0.0)

    # Grids (string fields map to parser in design.make_grids)
    Kp_vals: str | None = None; Ki_vals: str | None = None; Kd_vals: str | None = None
    Kp_range: List[float] | None = None; Ki_range: List[float] | None = None; Kd_range: List[float] | None = None
    Kp_n: int | None = None; Ki_n: int | None = None; Kd_n: int | None = None

    pi_Kp_vals: str | None = None; pi_Ki_vals: str | None = None
    pi_Kp_range: List[float] | None = None; pi_Ki_range: List[float] | None = None
    pi_Kp_n: int | None = None; pi_Ki_n: int | None = None

    pd_Kp_vals: str | None = None; pd_Kd_vals: str | None = None
    pd_Kp_range: List[float] | None = None; pd_Kd_range: List[float] | None = None
    pd_Kp_n: int | None = None; pd_Kd_n: int | None = None

    K_vals: str | None = None; a_vals: str | None = None
    K_range: List[float] | None = None; a_range: List[float] | None = None
    K_n: int | None = None; a_n: int | None = None

    # Requirements
    max_overshoot: float | None = None
    max_settling: float | None = None
    max_rise: float | None = None
    max_ess: float | None = None
    settle_tol: float = 0.02

    # Simulation
    tfinal: float | None = None
    dt: float | None = None

    # Output
    backend: str = "plotly"
    plot_top: int = 5
    save_prefix: str = "design"
    export_json: bool = False
    export_csv: bool = False
