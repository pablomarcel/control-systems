import os, json, logging, pytest
from state_space_design.robustTool.io import ensure_out_dir, save_json, OUT_DIR
from state_space_design.robustTool.utils import log_calls

def test_ensure_out_dir_and_save_json():
    ensure_out_dir()
    p = save_json({"a":1}, "cov/test.json")
    assert p.startswith(OUT_DIR)
    data = json.load(open(p))
    assert data["a"] == 1

def test_log_calls_exception_path(caplog):
    caplog.set_level(logging.DEBUG)
    @log_calls()
    def will_fail(x):
        raise ValueError("boom")
    with pytest.raises(ValueError):
        will_fail(1)
    assert any("FAIL" in r.message for r in caplog.records)
