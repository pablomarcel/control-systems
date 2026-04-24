import subprocess, sys, pathlib

def repo_root():
    return pathlib.Path(__file__).resolve().parents[3]

def test_cli_missing_B_for_Ki_gives_error():
    root = repo_root()
    cmd = [sys.executable, "-m", "state_space_design.gainMatrixTool.cli", "run",
           "--mode","K", "--A","0 1; -2 -3", "--poles","-2","-5"]
    cp = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    assert cp.returncode != 0

def test_cli_missing_C_for_L_gives_error():
    root = repo_root()
    cmd = [sys.executable, "-m", "state_space_design.gainMatrixTool.cli", "run",
           "--mode","L", "--A","0 1; -2 -3", "--poles","-2","-5"]
    cp = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    assert cp.returncode != 0
