import subprocess, sys, pathlib, os

def test_cli_help_runs():
    # File is .../stateSpaceDesign/gainMatrixTool/tests/test_cli_help.py
    # repo_root should be .../modernControl
    repo_root = pathlib.Path(__file__).resolve().parents[3]

    cmd = [sys.executable, "-m", "stateSpaceDesign.gainMatrixTool.cli", "--help"]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)

    # Helpful diagnostics if it ever fails again
    if out.returncode != 0:
        print("STDOUT:\n", out.stdout)
        print("STDERR:\n", out.stderr)

    assert out.returncode == 0
    assert "Gain-matrix design" in out.stdout
