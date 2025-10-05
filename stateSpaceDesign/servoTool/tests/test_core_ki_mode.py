import json, pathlib, numpy as np
from stateSpaceDesign.servoTool.apis import run, RunRequest

def test_ki_mode_basic(tmp_path):
    ctrl = {
        "mode": "KI",
        "A": [[0,1],[0,-2]],
        "B": [[0],[1]],
        "C": [[1,0]],
        "K": [2, 3],
        "kI": 4.0,
        "state_names": ["x1","x2"],
        "output_names": ["y1"],
    }
    data = tmp_path / "KI_controller.json"
    data.write_text(json.dumps(ctrl), encoding="utf-8")

    req = RunRequest(
        data_path=str(data),
        r=1.0,
        export_json="ki_mode_io.json",
        t="0:0.1:1",
        save_csv="ki_mode_step.csv",
        backend="none",
    )
    resp = run(req)

    assert resp.model.mode.value == "KI"
    # Augmented size: (n+p) x (n+p) with p=1 here → 3x3
    assert resp.model.Acl.shape == (3,3)
    assert resp.model.Bcl.shape == (3,1)
    assert resp.model.C.shape == (1,3)
    assert resp.model.D.shape == (1,1)
    assert resp.model.kI == 4.0
    assert resp.io_json_path.endswith("ki_mode_io.json")
    assert resp.csv_path.endswith("ki_mode_step.csv")
