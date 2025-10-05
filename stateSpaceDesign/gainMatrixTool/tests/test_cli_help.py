import subprocess, sys, os, pathlib

def test_cli_help_runs():
    pkg_root = pathlib.Path(__file__).resolve().parents[2]
    cmd = [sys.executable, "-m", "stateSpaceDesign.gainMatrixTool.cli"]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=pkg_root)
    assert out.returncode == 0
    assert "Gain-matrix design" in out.stdout
