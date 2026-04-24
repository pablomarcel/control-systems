
import json, sys, runpy

def test_main_module_entrypoint(tmp_path, monkeypatch):
    payload = {"C": [[1,0]], "K": [1,2], "simulation": {"t":[0,1], "x":[[1,0],[0,0]], "e":[[0.5,0.0],[0,0]]}}
    data = tmp_path / "ex.json"
    data.write_text(json.dumps(payload), encoding="utf-8")
    argv = [
        "python",
        "-m",
        "state_space_design.observerStatePlotTool",
        "--data", str(data),
        "--backend", "none",
        "--save_csv", str(tmp_path / "series.csv"),
        "--what", "x,e,err,y,u"
    ]
    monkeypatch.setattr(sys, "argv", argv)
    runpy.run_module("state_space_design.observerStatePlotTool", run_name="__main__")
    assert (tmp_path / "series.csv").exists()
