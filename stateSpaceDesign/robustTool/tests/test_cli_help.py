import subprocess, sys, os, pathlib

def test_cli_help_invokes():
    # call as a module: python -m stateSpaceDesign.robustTool.cli --help
    cmd = [sys.executable, "-m", "stateSpaceDesign.robustTool.cli", "--help"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "Robust control sweeps" in proc.stdout
