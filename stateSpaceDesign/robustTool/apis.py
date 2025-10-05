from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List

@dataclass
class RunRequest:
    # plant
    num: str
    den: str
    # controller (choose one)
    pid: Optional[str] = None            # "kp,ki,kd[,nd]"
    K_num: Optional[str] = None
    K_den: Optional[str] = None
    # weights
    Wm_num: Optional[str] = None
    Wm_den: Optional[str] = None
    Ws_num: Optional[str] = None
    Ws_den: Optional[str] = None
    Wa_num: Optional[str] = None
    Wa_den: Optional[str] = None
    # sweep/grid
    wmin: float = 1e-2
    wmax: float = 1e2
    npts: int = 400
    # step
    step: bool = False
    tfinal: float = 8.0
    dt: float = 0.01
    # plots
    plots: str = "mpl"  # {"mpl","plotly","both","none"}
    # io
    export_json: Optional[str] = None    # path in out/
    loglevel: str = "INFO"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SweepMetric:
    gamma: Optional[float] = None
    w_peak: Optional[float] = None
    ok: Optional[bool] = None
    error: Optional[str] = None

@dataclass
class RunResult:
    info: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, SweepMetric] = field(default_factory=dict)
    # Step results (may be None if step=False)
    step_time: Optional[List[float]] = None
    step_y: Optional[List[float]] = None
    step_u: Optional[List[float]] = None

    def to_jsonable(self) -> Dict[str, Any]:
        def sm_to_dict(sm: SweepMetric):
            return None if sm is None else {
                "gamma": sm.gamma,
                "w_peak": sm.w_peak,
                "ok": sm.ok,
                "error": sm.error,
            }
        return {
            "info": self.info,
            "metrics": {k: sm_to_dict(v) for k, v in self.metrics.items()},
            "step": None if self.step_time is None else {
                "time": self.step_time,
                "y": self.step_y,
                "u": self.step_u,
            }
        }
