from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional

# ------------------------------- Config DTOs -------------------------------

Mode = Literal["msd-step", "tf-from-ss", "mimo-demo", "ode-no-deriv", "ode-with-deriv", "kv-vs-maxwell"]

@dataclass(slots=True)
class CommonSim:
    tfinal: float = 10.0
    dt: float = 1e-3
    u0: float = 1.0
    save: bool = True
    verbose: int = 0

@dataclass(slots=True)
class MSDConfig(CommonSim):
    m: float = 1.0
    b: float = 1.0
    k: float = 10.0
    y0: float = 0.0
    ydot0: float = 0.0

@dataclass(slots=True)
class TFfromSSConfig:
    A: Optional[str] = None
    B: Optional[str] = None
    C: Optional[str] = None
    D: Optional[str] = None
    m: float = 1.0
    b: float = 1.0
    k: float = 10.0

@dataclass(slots=True)
class ODENoDerivConfig(CommonSim):
    a: Optional[str] = None          # "[a1,...,an]"
    b0: float = 1.0
    msd: bool = False
    m: float = 1.0
    b: float = 1.0
    k: float = 10.0
    y0: float = 0.0
    ydot0: float = 0.0

@dataclass(slots=True)
class ODEWithDerivConfig(CommonSim):
    a: Optional[str] = None          # "[a1,...,an]"
    b: Optional[str] = None          # "[b0,...,bn]"

@dataclass(slots=True)
class RunConfig:
    mode: Mode
    # One of the below depending on mode
    msd: Optional[MSDConfig] = None
    tfss: Optional[TFfromSSConfig] = None
    ode_nd: Optional[ODENoDerivConfig] = None
    ode_d: Optional[ODEWithDerivConfig] = None
    kvmax: Optional[CommonSim] = None

# ------------------------------- Results DTO ------------------------------

@dataclass(slots=True)
class RunResult:
    ok: bool
    message: str = ""
    pretty_tf: Optional[str] = None
    saved_images: list[str] = None
    hints: list[str] = None
