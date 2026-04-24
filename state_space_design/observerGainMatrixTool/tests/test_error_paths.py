import os, sys, subprocess, json, pathlib

def _env():
    env = os.environ.copy()
    env["PYTHONPATH"] = env.get("PYTHONPATH","") + (":" if env.get("PYTHONPATH") else "") + "/mnt/data"
    return env

def test_cli_not_observable():
    # C with zero row makes it unobservable
    cmd = [
        sys.executable, "-m", "state_space_design.observerGainMatrixTool.cli",
        "--A", "0 1; -2 -3",
        "--C", "0 0",
        "--poles", "-5", "-6"
    ]
    proc = subprocess.run(cmd, env=_env(), capture_output=True, text=True)
    assert proc.returncode != 0
    assert "observable" in (proc.stderr.lower())

def test_cli_missing_B_for_K():
    cmd = [
        sys.executable, "-m", "state_space_design.observerGainMatrixTool.cli",
        "--A", "0 1; -2 -3",
        "--C", "1 0",
        "--poles", "-5", "-6",
        "--K_poles=-3,-4"
    ]
    proc = subprocess.run(cmd, env=_env(), capture_output=True, text=True)
    assert proc.returncode != 0
    assert "B is required" in proc.stderr
