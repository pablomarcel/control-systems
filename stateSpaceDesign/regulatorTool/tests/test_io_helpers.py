
import os, json, tempfile
from stateSpaceDesign.regulatorTool.io import ensure_dir, out_path, save_json

def test_io_paths_and_save_json(tmp_path):
    d = tmp_path / "x"
    ensure_dir(str(d))
    assert d.exists()
    p = out_path("demo.json", out_dir=str(d))
    save_json({"a":1}, p)
    with open(p, "r") as f:
        data = json.load(f)
    assert data["a"] == 1
