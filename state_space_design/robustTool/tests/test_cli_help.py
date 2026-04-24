import subprocess, sys, os, pathlib

def test_cli_help_invokes():
    # call as a module: python -m state_space_design.robustTool.cli --help
    cmd = [sys.executable, "-m", "state_space_design.robustTool.cli", "--help"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "Robust control sweeps" in proc.stdout
