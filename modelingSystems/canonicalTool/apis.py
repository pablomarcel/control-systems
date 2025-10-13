
# apis.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(slots=True)
class RunRequest:
    """User-facing configuration for a conversion run."""
    num: list[float]
    den: list[float]
    tfinal: float = 8.0
    dt: float = 1e-3
    symbolic: bool = False
    plots: bool = True
    save_png: Optional[str] = None
    no_show: bool = False

@dataclass(slots=True)
class PlotConfig:
    title: str = "Step responses (all forms should coincide)"
