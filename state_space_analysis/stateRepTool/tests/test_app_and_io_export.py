from pathlib import Path
from state_space_analysis.stateRepTool.app import StateRepApp
from state_space_analysis.stateRepTool.apis import StateRepAPIRequest

def test_app_export_json(tmp_path):
    app = StateRepApp(out_dir=tmp_path)
    req = StateRepAPIRequest(example="ogata_9_1", which="all", numeric=True, digits=7, verify=False)
    results = app.run(req, export_json="ogata_9_1_all.json")
    assert "controllable" in results and "observable" in results and "diagonal" in results
    outp = tmp_path / "ogata_9_1_all.json"
    assert outp.exists() and outp.stat().st_size > 10
