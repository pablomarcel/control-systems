
from __future__ import annotations

import csv
from pathlib import Path
import plotly.graph_objects as go
import numpy as np

from rootLocus.systemResponseTool.io import Exporter

def test_exporter_save_csv_and_html(tmp_path: Path):
    out_dir = tmp_path / "out"
    exp = Exporter(out_dir)

    # CSV (relative target under out_dir)
    T = np.linspace(0, 0.2, 5)
    series = [("y", np.sin(T))]
    exp.save_csv("demo.csv", T, series)
    p_csv = out_dir / "demo.csv"
    assert p_csv.exists()
    # sanity read
    with p_csv.open() as f:
        rows = list(csv.reader(f))
    assert rows[0][0] == "t"

    # HTML (absolute-like nested path)
    fig = go.Figure()
    fig.update_layout(title="demo")
    nested = out_dir / "plots" / "demo.html"
    exp.save_html(fig, str(nested))
    assert nested.exists()
