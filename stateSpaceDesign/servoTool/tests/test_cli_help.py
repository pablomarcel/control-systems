import subprocess, sys, os, json, tempfile, pathlib

def test_cli_help_runs():
    pkg_root = pathlib.Path(__file__).resolve().parents[1]
    cmd = [sys.executable, "-m", "stateSpaceDesign.servoTool.cli", "--help"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "Servo I/O model builder" in proc.stdout
