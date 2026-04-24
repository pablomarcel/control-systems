
from __future__ import annotations
import json, tempfile, os
from modeling_control_systems.mimoTool.apis import RunConfig
from modeling_control_systems.mimoTool.app import MIMOApp

def test_app_run_and_save_json(tmp_path):
    out_tpl = str(tmp_path / "{plant}_sum.json")
    cfg = RunConfig(plants=["two_tank","two_zone_thermal"], plot_steps=False, plot_sigma=False, show=False, save_json=out_tpl)
    app = MIMOApp()
    result = app.run(cfg)
    assert len(result.summaries) == 2
    # files written
    for p in cfg.plants:
        fp = tmp_path / f"{p}_sum.json"
        assert fp.exists()
        data = json.loads(fp.read_text())
        assert data["plant"] == p
