
from __future__ import annotations
from pathlib import Path
import json
from state_space_analysis.canonicalTool.utils import parse_list, ensure_dir, substitute_kind, time_grid
from state_space_analysis.canonicalTool.io import save_json, default_out_path

def test_utils_parse_and_timegrid_and_subst(tmp_path: Path):
    assert parse_list("1, 2, 3") == [1.0, 2.0, 3.0]
    assert parse_list([4,5]) == [4.0, 5.0]
    assert substitute_kind("x_{kind}.y", "step") == "x_step.y"
    T = time_grid(1.0, 0.1)
    assert abs(T[-1] - 1.0) < 1e-12
    out_file = tmp_path / "a" / "b" / "data.json"
    ensure_dir(str(out_file))
    save_json({"ok": True}, str(out_file))
    assert json.loads(out_file.read_text())["ok"] is True

def test_default_out_path_string():
    p = default_out_path("hello.txt")
    assert "state_space_analysis/canonicalTool/out" in p
