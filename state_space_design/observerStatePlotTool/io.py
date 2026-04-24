from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import json
import numpy as np
from .utils import ensure_out_path

@dataclass
class JSONLoader:
    """Load observer/controller JSON payloads."""
    def load(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

@dataclass
class CSVWriter:
    header: Optional[List[str]] = None
    def write(self, path: str, t: np.ndarray, series: List[np.ndarray], labels: List[str]) -> str:
        out = ensure_out_path(path, "observer_series.csv")
        M = np.column_stack([t] + series)
        hdr = "t," + ",".join(labels)
        np.savetxt(out, M, delimiter=",", header=hdr, comments="")
        return out
