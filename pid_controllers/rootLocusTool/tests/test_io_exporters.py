from __future__ import annotations
from pathlib import Path
from pid_controllers.rootLocusTool.io import export_json, export_csv
from pid_controllers.rootLocusTool.design import DesignPoint

def test_exporters(tmp_path):
    pjson = export_json(str(tmp_path / "a.json"), {"x": 1, "y": 2})
    assert Path(pjson).exists()
    rows = [DesignPoint(0.6, 1.0, 0.5, 1.2, 0.6, 2.0, 0.5, -0.3, 1.0)]
    pcsv = export_csv(str(tmp_path / "a.csv"), rows)
    assert Path(pcsv).exists()
