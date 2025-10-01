# rootLocus/systemResponseTool/io.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import csv
import numpy as np
import plotly.graph_objects as go

from .utils import make_logger

log = make_logger(__name__)

@dataclass(slots=True)
class Exporter:
    out_dir: Path

    def save_csv(self, fname: str, T: np.ndarray, series: List[Tuple[str, np.ndarray]]):
        p = self.out_dir / fname
        with p.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t"] + [name for name, _ in series])
            for i in range(len(T)):
                row = [f"{T[i]:.12g}"] + [f"{y[i]:.12g}" for _, y in series]
                w.writerow(row)
        log.info("[saved] CSV -> %s", p)

    def save_html(self, fig: go.Figure, fname: str):
        p = self.out_dir / fname
        fig.write_html(str(p), include_plotlyjs="cdn")
        log.info("[saved] HTML -> %s", p)
