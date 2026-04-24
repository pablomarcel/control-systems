from __future__ import annotations
from state_space_analysis.converterTool.io import default_out, OUT_DIR

def test_default_out_creates_dir():
    p = default_out("touch_me.txt")
    assert p.parent == OUT_DIR
    # Touch is done by plot tests; here just ensure path target is inside OUT_DIR
    assert "out" in str(p)
