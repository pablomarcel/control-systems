
from __future__ import annotations
from pathlib import Path
import json

from transientAnalysis.routhTool.app import RouthApp
from transientAnalysis.routhTool.io import RouthPaths, ensure_dirs, write_text, dump_json

def test_paths_and_export(tmp_path):
    pkg_dir = tmp_path / "routhToolPkg"
    pkg_dir.mkdir()
    # Ensure dirs
    paths = RouthPaths.from_package_root(pkg_dir)
    ensure_dirs(paths)
    assert paths.in_dir.exists() and paths.out_dir.exists()

    # App export
    app = RouthApp.discover(pkg_dir)
    payload = app.run("1, 5, 6, 2", export_basename="demo")
    out_file = paths.out_dir / "demo.json"
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert data["degrees"] == [3,2,1,0]

def test_io_helpers(tmp_path):
    out_txt = tmp_path / "a" / "b" / "note.txt"
    write_text(out_txt, "hello")
    assert out_txt.exists() and out_txt.read_text() == "hello"

    out_json = tmp_path / "c" / "d" / "data.json"
    dump_json(out_json, {"x": 1})
    assert out_json.exists() and '"x": 1' in out_json.read_text()
