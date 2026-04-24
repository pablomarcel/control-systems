import sys, subprocess, json, os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]  # .../modernControl
PKG_DIR = REPO_ROOT / "pid_controllers" / "tuningTool"

def write_rules(tmpdir: Path):
    data = {
      "methods": {
        "ZN_step": {"name":"ZN First","inputs":["L","T"],
          "controllers": {
            "P": {"formula":{"Kp":"T/L","Ti":"inf","Td":"0"},"derived":{"Ki":"0","Kd":"0"}},
            "PID":{"formula":{"Kp":"1.2*T/L","Ti":"2*L","Td":"0.5*L"},"derived":{"Ki":"Kp/Ti","Kd":"Kp*Td"}}
          }}
      }
    }
    p = tmpdir / "tuning_rules.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    (PKG_DIR / "in").mkdir(parents=True, exist_ok=True)
    # copy into package in/ for relative resolution test
    (PKG_DIR / "in" / "tuning_rules.json").write_text(p.read_text(), encoding="utf-8")
    return p

def test_cli_shim_runs_from_package(tmp_path):
    rules = write_rules(tmp_path)
    # Run from inside the package using the shim
    cmd = [sys.executable, "cli.py", "--file", "tuning_rules.json", "--method", "ZN_step", "--controller", "PID", "--L", "0.8", "--T", "3.0"]
    proc = subprocess.run(cmd, cwd=str(PKG_DIR), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "Gains:" in proc.stdout

def test_cli_list_methods_with_in_prefix(tmp_path):
    rules = write_rules(tmp_path)
    # Pass a path beginning with 'in/...'
    cmd = [sys.executable, "-m", "pid_controllers.tuningTool.cli", "--file", "in/tuning_rules.json", "--list", "methods"]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "ZN_step:" in proc.stdout or "ZN_step" in proc.stdout

def test_cli_unknowns_and_missing(tmp_path):
    rules = write_rules(tmp_path)
    # Unknown method
    proc = subprocess.run([sys.executable, "-m", "pid_controllers.tuningTool.cli", "--file", "tuning_rules.json", "--method", "BAD", "--controller", "PID"],
                          cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert proc.returncode == 2 and "Unknown method" in proc.stdout
    # Missing inputs
    proc2 = subprocess.run([sys.executable, "-m", "pid_controllers.tuningTool.cli", "--file", "tuning_rules.json", "--method", "ZN_step", "--controller", "PID"],
                           cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert proc2.returncode == 2 and "requires inputs" in proc2.stdout
