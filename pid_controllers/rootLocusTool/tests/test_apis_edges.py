from __future__ import annotations
from pathlib import Path
import json
import types

from pid_controllers.rootLocusTool.design import RootLocusConfig, RootLocusDesigner
from pid_controllers.rootLocusTool.apis import RootLocusService, RootLocusRequest

def test_service_no_points_analyze_true(tmp_path, monkeypatch):
    cfg = RootLocusConfig(example="ogata_8_1", zeta_values=[0.6], omega=(0.2, 0.3, 3))
    # Force compute_scan to return no points
    monkeypatch.setattr(RootLocusDesigner, "compute_scan", lambda self, Gp: [])
    req = RootLocusRequest(cfg=cfg, analyze=True, export_json_path=str(tmp_path / "no_points.json"))
    out = RootLocusService().run(req)
    # s_row stays None and analyzed should be False (no s_row)
    assert out["s_row"] is None
    assert out["analyzed"] is False
    # json payload exists and contains summary with a_recommended None
    data = json.loads(Path(out["json_path"]).read_text())
    assert data["summary"].get("a_recommended") is None
