
from __future__ import annotations
import json, os, tempfile
from modeling_control_systems.mimoTool.io import write_json
from modeling_control_systems.mimoTool.utils import ensure_out_path

def test_write_json_complex(tmp_path):
    p = write_json({"z": 1+2j}, str(tmp_path/"z.json"), "out", "x.json")
    data = json.loads((tmp_path/"z.json").read_text())
    assert "z" in data and set(data["z"].keys()) == {"re","im"}

def test_ensure_out_path_dir_and_default(tmp_path):
    # default
    path = ensure_out_path(None, str(tmp_path), "a.json")
    assert os.path.basename(path) == "a.json" and os.path.dirname(path) == str(tmp_path)
    # directory provided -> becomes file within
    d = tmp_path/"nested"
    path2 = ensure_out_path(str(d), str(tmp_path), "b.json")
    assert os.path.basename(path2) == "b.json" and os.path.dirname(path2) == str(d)
    # file with extension passed -> return as-is
    f = tmp_path/"c.json"
    path3 = ensure_out_path(str(f), str(tmp_path), "x.json")
    assert path3 == str(f)
