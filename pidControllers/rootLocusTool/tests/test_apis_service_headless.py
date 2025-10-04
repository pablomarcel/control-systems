from __future__ import annotations
from pathlib import Path
import json
from pidControllers.rootLocusTool.design import RootLocusConfig
from pidControllers.rootLocusTool.apis import RootLocusService, RootLocusRequest

def test_service_headless_json(tmp_path):
    cfg = RootLocusConfig(example="ogata_8_1", omega=(0.2,2.0,20), zeta_values=[0.6,0.7])
    req = RootLocusRequest(cfg=cfg, save=None, export_json_path=str(tmp_path / "smoke.json"))
    out = RootLocusService().run(req)
    assert out["json_path"]
    data = json.loads(Path(out["json_path"]).read_text())
    assert "summary" in data and "a_used" in data
