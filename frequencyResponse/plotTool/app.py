from __future__ import annotations
from dataclasses import dataclass, field, field
from .io import IOConfig
from .utils import build_logger

@dataclass(slots=True)
class PlotToolApp:
    io: IOConfig = field(default_factory=IOConfig)
    log_name: str = "plotTool"

    def logger(self, level=None):
        return build_logger(self.log_name, level=(level if level is not None else None))
