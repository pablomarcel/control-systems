import json
from pathlib import Path
import numpy as np
from transient_analysis.responseTool.app import ResponseToolApp

def test_second_order_single_params(tmp_path: Path):
    app = ResponseToolApp(root=tmp_path, show_plots=False)
    res = app.second_order_single(wn=5.0, zeta=0.4, tfinal=1.0, dt=1e-3, save_prefix="so")
    assert res.T.ndim == 1 and res.y.ndim == 1
    out_json = tmp_path / "out" / "so_single.json"
    assert out_json.exists()
    data = json.loads(out_json.read_text())
    assert "analytic" in data and "measured" in data

def test_second_order_sweep(tmp_path: Path):
    app = ResponseToolApp(root=tmp_path, show_plots=False)
    data = app.second_order_sweep(wn=5.0, zetas=[0.0, 0.2, 0.4], tfinal=0.5, dt=1e-3, save_prefix="sweep")
    assert "curves" in data and len(data["curves"]) == 3
    out_json = tmp_path / "out" / "sweep_sweep.json"
    assert out_json.exists()
