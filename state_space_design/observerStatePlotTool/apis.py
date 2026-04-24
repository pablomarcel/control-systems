from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class SimulateOptions:
    enabled: bool = False
    t: str = "0:0.01:4"
    x0: Optional[str] = None
    e0: Optional[str] = None

from dataclasses import field

@dataclass
class PlotRequest:
    data_path: str
    what: str = "auto"   # comma list of x,e,err,y,u or "auto"
    backend: str = "both"  # mpl|plotly|both|none
    subplots: bool = False
    save_png: Optional[str] = None
    save_html: Optional[str] = None
    save_csv: Optional[str] = None
    no_show: bool = False
    simulate: SimulateOptions = field(default_factory=SimulateOptions)

@dataclass
class PlotResponse:
    csv_path: Optional[str]
    png_path: Optional[str]
    html_path: Optional[str]
