
from __future__ import annotations
import sys, subprocess
from pathlib import Path

def test_cli_runs_as_script_from_package_dir():
    # .../pidControllers/zeroPoleTool/tests/test_cli_as_script.py
    pkg_dir = Path(__file__).resolve().parents[1]  # -> .../pidControllers/zeroPoleTool
    cmd = [sys.executable, "cli.py",
           "--plant-form","coeff","--num","1","--den","1,2,1",
           "--a-vals","2.0","--b-vals","2.0","--c-vals","1.0",
           "--no-progress"]
    p = subprocess.Popen(cmd, cwd=str(pkg_dir), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.communicate()[0]
    assert p.returncode == 0, out
    assert "Best candidate" in out or "No candidate" in out
