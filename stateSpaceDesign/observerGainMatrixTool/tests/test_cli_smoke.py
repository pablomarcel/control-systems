import subprocess, sys, json, os, pathlib

def test_cli_help_runs():
    # Ensure module import path includes /mnt/data
    env = os.environ.copy()
    env["PYTHONPATH"] = env.get("PYTHONPATH", "") + (":" if env.get("PYTHONPATH") else "") + "/mnt/data"
    cmd = [sys.executable, "-m", "stateSpaceDesign.observerGainMatrixTool.cli", "--help"]
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "Observer Gain Matrix Tool" in proc.stdout or "usage" in proc.stdout

def test_cli_basic_json():
    env = os.environ.copy()
    env["PYTHONPATH"] = env.get("PYTHONPATH", "") + (":" if env.get("PYTHONPATH") else "") + "/mnt/data"
    # A simple 2nd order example (observable pair)
    cmd = [
        sys.executable, "-m", "stateSpaceDesign.observerGainMatrixTool.cli",
        "--A", "0 1; -2 -3",
        "--C", "1 0",
        "--poles", "-5", "-6"
    ]
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert "Ke" in data and isinstance(data["Ke"], list)
    assert data["observer"]["method_used"] in ("place","ack")
