import os, sys, subprocess, json
from pathlib import Path

def _env():
    env = os.environ.copy()
    # Ensure repo root (containing state_space_design/) is on PYTHONPATH
    here = Path(__file__).resolve()
    root = here
    # Walk up until we find 'state_space_design' directory
    for p in here.parents:
        if (p / "state_space_design").exists():
            root = p
            break
    env["PYTHONPATH"] = (str(root) + (":" + env.get("PYTHONPATH","") if env.get("PYTHONPATH") else ""))
    return env

def test_cli_export_json(tmp_path):
    out_json = tmp_path / "cli_out.json"
    cmd = [
        sys.executable, "-m", "state_space_design.observerGainMatrixTool.cli",
        "--A", "0 1; -2 -3",
        "--B", "0;1",
        "--C", "1 0",
        "--poles", "-5", "-6",
        "--K_poles=-3,-4",
        "--compute_closed_loop",
        "--export_json", str(out_json.name),
        "--log", "INFO"
    ]
    proc = subprocess.run(cmd, cwd=tmp_path, env=_env(), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    data = json.loads((tmp_path / out_json.name).read_text())
    assert "Ke" in data and data["observer_controller_tf"] is not None

def test_cli_pretty_output():
    cmd = [
        sys.executable, "-m", "state_space_design.observerGainMatrixTool.cli",
        "--A", "0 1; -2 -3",
        "--C", "1 0",
        "--poles", "-5", "-6",
        "--pretty"
    ]
    proc = subprocess.run(cmd, env=_env(), capture_output=True, text=True)
    assert proc.returncode == 0
    assert "Full-Order Observer Design" in proc.stdout
