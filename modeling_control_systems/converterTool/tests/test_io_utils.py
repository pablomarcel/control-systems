
from __future__ import annotations
from pathlib import Path
import numpy as np
from modeling_control_systems.converterTool.io import parse_vector, parse_matrix, ensure_out_path, write_json, read_json

def test_parse_vector_and_matrix():
    v = parse_vector("1, 2; 3")
    assert (v == np.array([1.0,2.0,3.0])).all()
    m = parse_matrix("1, 2; 3, 4")
    assert m.shape == (2,2)
    assert (m == np.array([[1.0,2.0],[3.0,4.0]])).all()

def test_ensure_out_and_json(tmp_path):
    # explicit file
    f = ensure_out_path(tmp_path / "x.json", "ignored", suffix=".json")
    p = write_json({"ok":1}, f)
    assert p.exists()
    assert read_json(p)["ok"] == 1
    # directory path
    dfile = ensure_out_path(tmp_path / "subdir", "yfile", suffix=".json")
    p2 = write_json({"z":2}, dfile)
    assert p2.exists()
