
from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class CompareOptions:
    tfinal: float = 8.0
    dt: float = 1e-3
    symbolic: bool = False
    backend: str = "mpl"     # "mpl" | "plotly"
    show: bool = True
    save: str | None = None  # may contain {kind}
