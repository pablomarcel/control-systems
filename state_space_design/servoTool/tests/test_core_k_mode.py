import json, pathlib, numpy as np
from state_space_design.servoTool.apis import run, RunRequest
from state_space_design.servoTool.io import OUT_DIR

def test_k_mode_basic(tmp_path):
    # Simple controllable system with integrator in plant; K stabilizes it.
    ctrl = {
        "mode": "K",
        "A": [[0,1],[0,-2]],
        "B": [[0],[1]],
        "K": [2, 3],
        "state_names": ["x1","x2"],
        "output_names": ["y1"],
    }
    data = tmp_path / "K_controller.json"
    data.write_text(json.dumps(ctrl), encoding="utf-8")

    # Provide C via CLI (not in JSON)
    req = RunRequest(
        data_path=str(data),
        mode_C="1 0",
        r=1.0,
        export_json="k_mode_io.json",
        t="0:0.1:1",
        save_csv="k_mode_step.csv",
        backend="none",
    )
    resp = run(req)

    assert resp.model.mode.value == "K"
    assert resp.model.Acl.shape == (2,2)
    assert resp.model.Bcl.shape == (2,1)
    assert resp.model.C.shape == (1,2)
    assert resp.model.D.shape == (1,1)
    assert resp.model.k_r is not None
    # Files land under package OUT_DIR
    assert resp.io_json_path.endswith("k_mode_io.json")
    assert resp.csv_path.endswith("k_mode_step.csv")
