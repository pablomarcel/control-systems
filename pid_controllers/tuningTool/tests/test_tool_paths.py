
from __future__ import annotations
from pathlib import Path
from pid_controllers.tuningTool.tools.tool_paths import IN_DIR, OUT_DIR, ensure_outdir

def test_paths_and_ensure_outdir():
    assert IN_DIR.name == "in"
    ensure_outdir()
    assert OUT_DIR.exists()
