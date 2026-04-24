import json, os
from state_space_design.robustTool import cli

def test_cli_main_saves_json(tmp_path, monkeypatch):
    outname = "cli_result.json"
    argv = [
        "--num","10 20","--den","1 10 24 0",
        "--pid","1,2,0.1,10",
        "--Wm_num","0.2 1","--Wm_den","0.02 1",
        "--Ws_num","0.5 0","--Ws_den","1 0.05 0",
        "--plots","none",
        "--export-json", outname,
        "--npts","32",
    ]
    cli.main(argv)
    out_path = os.path.join(os.path.dirname(cli.__file__), "out", outname)
    assert os.path.exists(out_path)
    data = json.load(open(out_path))
    assert "info" in data and "metrics" in data
