import os
from state_space_design.robustTool import io

def test_out_dir_is_package_relative():
    pkg_dir = os.path.dirname(io.__file__)
    assert io.OUT_DIR == os.path.join(pkg_dir, "out")
    assert os.path.isdir(io.ensure_out_dir())

def test_save_json_writes_under_out(tmp_path):
    p = io.save_json({"ok": 1}, "cov/smoke.json")
    assert p.startswith(io.OUT_DIR + os.sep)
    assert os.path.exists(p)
