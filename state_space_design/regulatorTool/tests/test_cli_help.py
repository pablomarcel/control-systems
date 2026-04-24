import subprocess, sys, json, os, shlex, pathlib

def test_cli_help_runs():
    cmd = [sys.executable, "-m", "state_space_design.regulatorTool.cli", "--help"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    assert out.returncode == 0
    assert "regulator" in out.stdout.lower()
