
from __future__ import annotations
import os, tempfile, json
from frequencyResponse.bodeTool.app import BodeApp
from frequencyResponse.bodeTool.apis import BodeConfig

def test_app_run_and_render_json(tmp_path):
    cfg = BodeConfig(num="1", den="1, 0.8, 1", bode=True, save_json=str(tmp_path/"report.json"))
    app = BodeApp(level="INFO")
    result = app.run(cfg)
    assert "s^2" in result.pretty_tf
    # Render only JSON (no plots saved unless path set)
    app.render(cfg, result)
    assert (tmp_path/"report.json").exists()
    data = json.loads((tmp_path/"report.json").read_text())
    assert "margins" in data and "closedloop" in data and "L" in data
