import json
from pathlib import Path
from pidControllers.tuningTool.app import TuningApp
from pidControllers.tuningTool.utils import TuningInputs

def write_rules(tmp_path: Path):
    data = {
      "methods": {
        "M": {"name":"X","inputs":[], "controllers": {
          "P":{"formula":{"Kp":"1","Ti":"inf","Td":"0"},"derived":{"Ki":"0","Kd":"0"}}
        }}
      }
    }
    p = tmp_path / "rules.json"; p.write_text(json.dumps(data), encoding="utf-8"); return p

def test_app_save_json_and_run(tmp_path, monkeypatch):
    p = write_rules(tmp_path)
    app = TuningApp.create_default()
    # compute with no inputs, method M/P
    res = app.run_compute(method="M", controller="P", inputs=TuningInputs(), file=str(p))
    assert res.Kp == 1 and res.Ki == 0 and res.Ti == float("inf")
    # save_json path
    saved = app.save_json({"a": 1}, "tst.json")
    assert saved.name == "tst.json" and saved.exists() and json.loads(saved.read_text())["a"] == 1
