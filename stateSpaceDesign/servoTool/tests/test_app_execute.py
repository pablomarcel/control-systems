import json
from stateSpaceDesign.servoTool.app import ServoApp

def test_app_execute(tmp_path):
    ctrl = {"mode":"K","A":[[0,1],[0,-2]],"B":[[0],[1]],"K":[2,3]}
    data = tmp_path / "ctrl.json"
    data.write_text(json.dumps(ctrl), encoding="utf-8")
    app = ServoApp()
    resp = app.execute(data_path=str(data), mode_C="1 0", backend="none", export_json="app_k_io.json")
    assert resp.io_json_path.endswith("app_k_io.json")
