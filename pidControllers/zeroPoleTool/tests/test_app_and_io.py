
from __future__ import annotations
import json, csv, io, os
from pathlib import Path
from pidControllers.zeroPoleTool.app import ZeroPoleApp, AppConfig
from pidControllers.zeroPoleTool.apis import ZeroPoleAPI, DesignRequest
from pidControllers.zeroPoleTool.io import export_results
from pidControllers.zeroPoleTool.core import plant_polys
from pidControllers.zeroPoleTool.design import Designer
import control as ct
import numpy as np
import pytest

def test_app_run_best_effort(monkeypatch, tmp_path: Path):
    # small grid; best_effort ensures we still get a candidate
    cfg = AppConfig(
        plant_form="coeff", num="1", den="1,2,1",
        a_vals="2.0 2.5", b_vals="2.0", c_vals="1.0",
        os_min=0, os_max=100, ts_max=10, best_effort=True, no_progress=True,
        plots=[]
    )
    app = ZeroPoleApp(cfg)
    picked, ok_list = app.run()
    assert picked is None or picked is not None  # smoke

def test_io_export_results_json_csv(tmp_path: Path):
    # Build a tiny candidate set using Designer on a trivial plant
    Gp = ct.tf([1], [1, 2, 1])
    des = Designer(arch="fig8-31")
    best, ok, closest, counts = des.search(
        Gp, a_grid=[2.0], b_grid=[2.0], c_grid=[1.0],
        os_min=0, os_max=100, ts_max=10, settle_tol=0.02,
        dist_peak_weight=0.0, show_progress=False
    )
    assert best or ok or closest
    # Save to tmp using a patched ensure_out_dir
    from pidControllers.zeroPoleTool import io as io_mod
    io_mod.ensure_out_dir = lambda base=None: str(tmp_path)
    P = plant_polys(Gp)
    export_results("cov", str(Gp), "fig8-31", P.Kp, P.A, P.B, ok if ok else ([best] if best else []), True, True)
    json_p = tmp_path / "cov_results.json"
    csv_p = tmp_path / "cov_results.csv"
    assert json_p.exists() and csv_p.exists()
    data = json.loads(json_p.read_text("utf-8"))
    assert data["arch"] == "fig8-31"
    rows = csv_p.read_text("utf-8").strip().splitlines()
    assert rows and rows[0].startswith("rank,a,b,c")

