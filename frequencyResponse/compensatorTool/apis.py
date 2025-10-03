# apis.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


# ------------------------------- Plant ----------------------------------------
@dataclass(slots=True)
class PlantSpec:
    """
    Declarative specification for the plant model.

    All fields are optional; exactly one of the input representations should be provided:
      • tf_expr: safe rational expression in 's' (e.g., "1/(s*(s+1)*(s+2))")
      • num/den: coefficient vectors as strings (comma/space separated), e.g., "1" / "1, 1, 2"
      • z/p/k:   ZPK representation as strings (comma/space separated)
      • A/B/C/D: State-space matrices as semicolon/comma separated rows, e.g., "0,1; -2,-3"
      • params:  parameter dictionary as "K=4,T=0.2" for use in tf_expr parsing
    """
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
    params: str = ""


# ---------------------------- Lag–Lead (existing) -----------------------------
@dataclass(slots=True)
class DesignOptions:
    """
    Options controlling lag–lead design.

    If ogata_7_28 is True, a preset design is used (Ogata Example 7-28).
    Otherwise the designer can:
      • Auto-scale gain to meet Kv (type-1 systems) and/or
      • Auto-place lead/lag from pm_target, pm_allow, wc_hint, r_lead, r_lag
      • Or accept manual lead/lag parameters (alpha/beta or wz/wp pairs).
    """
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
    """
    Plotting, export, and UX options.

    Lists (nichols_Mdb, nichols_Ndeg, nyquist_M, nyquist_marks) are populated by the CLI
    from either space-separated or comma-separated inputs. If None, the default behavior
    for that feature applies (e.g., no extra contours).
    """
    backend: str = "mpl"  # "mpl" or "plotly"
    plots: str = "bode,nyquist,nichols,step,ramp"
    ogata_axes: bool = False
    nichols_templates: bool = False

    # Optional numeric lists
    nichols_Mdb: Optional[List[float]] = None
    nichols_Ndeg: Optional[List[float]] = None
    nyquist_M: Optional[List[float]] = None
    nyquist_marks: Optional[List[float]] = None

    # File outputs
    save: Optional[str] = None           # e.g., ".../out/run_{kind}.html|png"
    save_img: Optional[str] = None       # static images when using plotly+kaleido
    export_json: Optional[str] = None    # path to design pack JSON
    export_csv_prefix: Optional[str] = None  # prefix for CSV exports

    # Runtime behavior
    no_show: bool = False
    verbose: bool = False
    show_unstable: bool = False  # force-show unstable baseline in time-domain plots


@dataclass(slots=True)
class FrequencyGrid:
    """Frequency grid used for frequency response computations and plots."""
    wmin: float = 1e-3
    wmax: float = 1e3
    wnum: int = 2000


@dataclass(slots=True)
class LagLeadDesignSpec:
    """Complete specification for a lag–lead design and visualization run."""
    plant: PlantSpec
    design: DesignOptions
    plot: PlotOptions = field(default_factory=PlotOptions)
    grid: FrequencyGrid = field(default_factory=FrequencyGrid)


@dataclass(slots=True)
class LagLeadDesignResult:
    """
    Output of a lag–lead design and visualization run.

    pack:  JSON-serializable dictionary with margins, design parameters, CL poles/zeros, etc.
    files: paths to any artifacts written to disk (plots, JSON, CSV).
    """
    pack: Dict[str, Any]
    files: List[str]


# ------------------------------- Lead-only ------------------------------------
# These mirror the fields used by lead.py (manual α/T/Kc or automatic PM-based multi-stage).
@dataclass(slots=True)
class LeadDesignOptions:
    """
    Options for the lead-only designer.

    Either provide (alpha & T) for a manual single-stage, or set pm_target for
    automatic one/multi-stage design. Kv can optionally auto-scale plant gain
    (type-1 only) before the lead design.
    """
    Kv: Optional[float] = None
    pm_target: Optional[float] = None
    pm_add: float = 5.0
    stages: int = 1
    phi_split: Optional[str] = None  # e.g., "60,40" to split φ across 2 stages
    alpha: Optional[float] = None    # manual single-stage
    T: Optional[float] = None        # manual single-stage
    Kc: Optional[float] = None       # optional manual gain when alpha/T given


@dataclass(slots=True)
class LeadDesignSpec:
    """Complete specification for a lead-only design and visualization run."""
    plant: PlantSpec
    design: LeadDesignOptions
    plot: PlotOptions = field(default_factory=PlotOptions)
    grid: FrequencyGrid = field(default_factory=FrequencyGrid)


@dataclass(slots=True)
class LeadDesignResult:
    """
    Output of a lead-only design and visualization run.

    pack:  JSON-serializable dictionary with margins, design parameters, etc.
    files: paths to any artifacts written to disk (plots, JSON, CSV).
    """
    pack: Dict[str, Any]
    files: List[str]
