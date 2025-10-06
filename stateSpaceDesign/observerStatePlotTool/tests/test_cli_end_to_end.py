
import json, os, tempfile
from stateSpaceDesign.observerStatePlotTool.cli import main as cli_main

def test_cli_csv_only_end_to_end(tmp_path):
    data = tmp_path / "ex.json"
    payload = {
        "C": [[1,0]],
        "K": [1,2],
        "simulation": {"t":[0,1],"x":[[1,0],[0,0]],"e":[[0.5,0.0],[0,0]]}
    }
    data.write_text(json.dumps(payload), encoding="utf-8")
    csv_path = tmp_path / "series.csv"
    argv = [
        "--data", str(data),
        "--what", "x,e,err,y,u",
        "--backend", "none",
        "--save_csv", str(csv_path),
    ]
    cli_main(argv)
    assert csv_path.exists()
