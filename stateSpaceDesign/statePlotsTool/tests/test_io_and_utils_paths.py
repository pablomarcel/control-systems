
from pathlib import Path
import json
from stateSpaceDesign.statePlotsTool.io import try_parse_controller, try_parse_io
from stateSpaceDesign.statePlotsTool.utils import resolve_out_path, ensure_dir

def test_io_try_parsers(tmp_path):
    ctrl = {"mode":"K","A":[[0]],"B":[[1]],"K":[[0]]}
    assert try_parse_controller(ctrl).mode == "K"
    bad = {"mode":"X","A":[[0]]}
    assert try_parse_controller(bad) is None
    io = {"Acl":[[0]],"Bcl":[[1]],"C":[[1]],"D":[[0]]}
    assert try_parse_io(io).Acl.shape == (1,1)

def test_utils_paths(tmp_path):
    out = resolve_out_path("file.csv", "def.csv", out_dir=tmp_path)
    assert Path(out).parent == tmp_path
    ensure_dir(tmp_path / "sub")
