# apis.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ------------------------------- Plant ----------------------------------------
@dataclass(slots=True)
class PlantSpec:
    """
    Declarative specification for the plant model.

    Provide exactly one plant representation: a transfer-function expression,
    numerator and denominator coefficients, zero-pole-gain data, or state-space
    matrices.

    The params field can provide named constants for transfer-function parsing,
    using a string such as "K=4,T=0.2".
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


# ---------------------------- Lag-Lead (existing) -----------------------------
@dataclass(slots=True)
class DesignOptions:
    """
    Options controlling lag-lead compensator design.

    If ogata_7_28 is true, the Ogata Example 7-28 preset design is used.
    Otherwise, the designer can auto-scale gain to meet Kv for type-1 systems,
    auto-place lead and lag elements from the phase-margin target, or accept
    manual lead and lag parameters.
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
    Plotting, export, and runtime options.

    The numeric list fields can be populated by the CLI from space-separated or
    comma-separated inputs. If a list field is None, the default behavior for
    that feature applies.
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
    save: Optional[str] = None  # e.g., ".../out/run_{kind}.html|png"
    save_img: Optional[str] = None  # static images when using plotly+kaleido
    export_json: Optional[str] = None  # path to design pack JSON
    export_csv_prefix: Optional[str] = None  # prefix for CSV exports

    # Runtime behavior
    no_show: bool = False
    verbose: bool = False
    show_unstable: bool = False  # force-show unstable baseline in time-domain plots


@dataclass(slots=True)
class FrequencyGrid:
    """Frequency grid used for frequency-response computations and plots."""

    wmin: float = 1e-3
    wmax: float = 1e3
    wnum: int = 2000


@dataclass(slots=True)
class LagLeadDesignSpec:
    """Complete specification for a lag-lead design and visualization run."""

    plant: PlantSpec
    design: DesignOptions
    plot: PlotOptions = field(default_factory=PlotOptions)
    grid: FrequencyGrid = field(default_factory=FrequencyGrid)


@dataclass(slots=True)
class LagLeadDesignResult:
    """
    Output of a lag-lead design and visualization run.

    The pack field contains JSON-serializable design results. The files field
    contains paths to artifacts written to disk.
    """

    pack: Dict[str, Any]
    files: List[str]


# ------------------------------- Lead-only ------------------------------------
@dataclass(slots=True)
class LeadDesignOptions:
    """
    Options for the lead-only designer.

    A manual single-stage design can be requested with alpha and T. Automatic
    one-stage or multi-stage design can be requested with pm_target. Kv can
    optionally auto-scale plant gain for type-1 systems before lead design.
    """

    Kv: Optional[float] = None
    pm_target: Optional[float] = None
    pm_add: float = 5.0
    stages: int = 1
    phi_split: Optional[str] = None  # e.g., "60,40" to split phi across 2 stages
    alpha: Optional[float] = None  # manual single-stage
    T: Optional[float] = None  # manual single-stage
    Kc: Optional[float] = None  # optional manual gain when alpha/T given


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

    The pack field contains JSON-serializable design results. The files field
    contains paths to artifacts written to disk.
    """

    pack: Dict[str, Any]
    files: List[str]


# ------------------------------- Lag-only -------------------------------------
@dataclass(slots=True)
class LagDesignOptions:
    """
    Options for the lag-only designer.

    A manual single-stage design can be requested with beta and T. Automatic
    design can be requested with pm_target. Kv can optionally auto-scale plant
    gain for type-1 systems before lag design.
    """

    Kv: Optional[float] = None
    pm_target: Optional[float] = None
    pm_add: float = 8.0
    w_ratio_z: float = 10.0
    beta: Optional[float] = None  # manual single-stage, beta > 1
    T: Optional[float] = None  # manual single-stage, wz = 1/T
    Kc: Optional[float] = None  # optional manual gain, default 1.0 in engine


@dataclass(slots=True)
class LagDesignSpec:
    """Complete specification for a lag-only design and visualization run."""

    plant: PlantSpec
    design: LagDesignOptions
    plot: PlotOptions = field(default_factory=PlotOptions)
    grid: FrequencyGrid = field(default_factory=FrequencyGrid)


@dataclass(slots=True)
class LagDesignResult:
    """
    Output of a lag-only design and visualization run.

    The pack field contains JSON-serializable design results. The files field
    contains paths to artifacts written to disk.
    """

    pack: Dict[str, Any]
    files: List[str]
