import os, json
from pathlib import Path

os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH","") + (":" if os.environ.get("PYTHONPATH") else "") + "/mnt/data"
from stateSpaceDesign.observerGainMatrixTool.io import OutputManager

def test_output_manager_writes(tmp_path):
    out = OutputManager(out_dir=tmp_path)
    p1 = out.write_text("hello", "a.txt")
    p2 = out.write_json({"x": 1}, "b.json")
    assert p1.exists() and p2.exists()
    assert json.loads(p2.read_text())["x"] == 1
