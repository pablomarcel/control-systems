import json, pathlib
from state_space_design.servoTool.apis import run, RunRequest

def test_apis_mpl_plot_and_csv(tmp_path):
    ctrl = {
        "mode": "K",
        "A": [[0,1],[0,-2]],
        "B": [[0],[1]],
        "K": [2,3],
        "state_names": ["x1","x2"],
        "output_names": ["y1"]
    }
    p = tmp_path / "ctrl.json"
    p.write_text(json.dumps(ctrl), encoding="utf-8")

    req = RunRequest(
        data_path=str(p),
        mode_C="1 0",
        r=1.0,
        export_json="apis_k_io.json",
        t="0:0.1:1",
        save_csv="apis_k_step.csv",
        backend="mpl",
        no_show=True,
    )
    resp = run(req)
    assert resp.io_json_path.endswith("apis_k_io.json")
    assert resp.csv_path.endswith("apis_k_step.csv")
