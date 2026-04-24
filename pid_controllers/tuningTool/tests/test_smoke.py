
# tests/test_smoke.py
from __future__ import annotations
import sys, subprocess, os
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    p = start.resolve()
    while True:
        if (p / "pid_controllers").is_dir():
            return p
        if p.parent == p:
            raise RuntimeError("Could not locate repo root containing 'pid_controllers'")
        p = p.parent

# Compute repo root dynamically, regardless of nesting depth
REPO_ROOT = find_repo_root(Path(__file__))

def write_minimal_json(path: Path) -> None:
    path.write_text("""
{
  "methods": {
    "ZN_step": {
      "name": "Ziegler-Nichols (First method)",
      "inputs": ["L", "T"],
      "controllers": {
        "P":   { "formula": { "Kp": "T/L",     "Ti": "inf", "Td": "0" } },
        "PI":  { "formula": { "Kp": "0.9*T/L", "Ti": "3*L", "Td": "0" }, "derived": { "Ki": "Kp/Ti", "Kd": "0" } },
        "PID": { "formula": { "Kp": "1.2*T/L", "Ti": "2*L", "Td": "0.5*L" }, "derived": { "Ki": "Kp/Ti", "Kd": "Kp*Td" } }
      }
    },
    "ZN_ultimate": {
      "name": "Ziegler-Nichols (Second method)",
      "inputs": ["Kcr", "Pcr"],
      "controllers": {
        "P":   { "formula": { "Kp": "0.5*Kcr",  "Ti": "inf",      "Td": "0" } },
        "PI":  { "formula": { "Kp": "0.45*Kcr", "Ti": "Pcr/1.2",  "Td": "0" }, "derived": { "Ki": "Kp/Ti", "Kd": "0" } },
        "PID": { "formula": { "Kp": "0.6*Kcr",  "Ti": "Pcr/2",    "Td": "Pcr/8" }, "derived": { "Ki": "Kp/Ti", "Kd": "Kp*Td" } }
      }
    }
  }
}
""", encoding="utf-8")

def test_cli_lists_and_compute(tmp_path: Path):
    # Ensure pid_controllers is a package (for imports in subprocess)
    pkg_init = REPO_ROOT / "pid_controllers" / "__init__.py"
    if not pkg_init.exists():
        pkg_init.write_text("", encoding="utf-8")

    json_path = tmp_path / "tuning_rules.json"
    write_minimal_json(json_path)

    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT) + (os.pathsep + env["PYTHONPATH"] if "PYTHONPATH" in env else "")

    # List methods
    proc1 = subprocess.run(
        [sys.executable, "-m", "pid_controllers.tuningTool.cli", "--file", str(json_path), "--list", "methods"],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env
    )
    assert proc1.returncode == 0, proc1.stderr
    out1 = proc1.stdout
    assert "ZN_step" in out1 and "ZN_ultimate" in out1

    # Compute a known case
    proc2 = subprocess.run(
        [sys.executable, "-m", "pid_controllers.tuningTool.cli",
         "--file", str(json_path), "--method", "ZN_step", "--controller", "PID", "--L", "0.8", "--T", "3.0"],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env
    )
    assert proc2.returncode == 0, proc2.stderr
    out2 = proc2.stdout
    assert "Kp=" in out2 and "Ki=" in out2 and "Kd=" in out2
