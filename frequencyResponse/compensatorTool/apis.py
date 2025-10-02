
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass(slots=True)
class PlantSpec:
    tf_expr: Optional[str] = None
    num: Optional[str] = None
    den: Optional[str] = None
    z: Optional[str] = None
    p: Optional[str] = None
    k: Optional[str] = None
    A: Optional[str] = None
    B: Optional[str] = None
    C: Optional[str] = None
    D: Optional[str] = None
    params: str = ''

@dataclass(slots=True)
class DesignOptions:
    Kv: Optional[float] = None
    pm_target: Optional[float] = None
    pm_allow: float = 5.0
    wc_hint: Optional[float] = None
    r_lead: float = 10.0
    r_lag: float = 10.0
    alpha: Optional[float] = None
    beta: Optional[float] = None
    wz_lead: Optional[float] = None
    wp_lead: Optional[float] = None
    wz_lag: Optional[float] = None
    wp_lag: Optional[float] = None
    Kc: float = 1.0
    ogata_7_28: bool = False

@dataclass(slots=True)
class PlotOptions:
    backend: str = 'mpl'
    plots: str = 'bode,nyquist,nichols,step,ramp'
    ogata_axes: bool = False
    nichols_templates: bool = False
    nichols_Mdb: Optional[list[float]] = None
    nichols_Ndeg: Optional[list[float]] = None
    nyquist_M: Optional[list[float]] = None
    nyquist_marks: Optional[list[float]] = None
    save: Optional[str] = None
    save_img: Optional[str] = None
    export_json: Optional[str] = None
    export_csv_prefix: Optional[str] = None
    no_show: bool = False
    verbose: bool = False

@dataclass(slots=True)
class FrequencyGrid:
    wmin: float = 1e-3
    wmax: float = 1e3
    wnum: int = 2000

@dataclass(slots=True)
class LagLeadDesignSpec:
    plant: PlantSpec
    design: DesignOptions
    plot: PlotOptions = field(default_factory=PlotOptions)
    grid: FrequencyGrid = field(default_factory=FrequencyGrid)

@dataclass(slots=True)
class LagLeadDesignResult:
    pack: Dict[str, Any]
    files: List[str]
