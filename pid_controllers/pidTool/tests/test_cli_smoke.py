from __future__ import annotations
import sys
import subprocess
from pathlib import Path

def run_cmd(args: list[str]) -> tuple[int, str]:
    # project root assumed to be repo root containing pid_controllers/
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen([sys.executable, "-m", "pid_controllers.pidTool.cli", *args],
                         cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_help_runs():
    code, out = run_cmd(["--help"])  # argparse will show top-level help and exit 0
    assert code == 0
    assert "PID design via" in out

def test_cli_run_smoke():
    # small grid to keep runtime tiny
    args = [
        "run",
        "--plant-form", "coeff", "--num", "1", "--den", "1 1 1",
        "--structure", "pd",
        "--pd-Kp-range", "0.5", "1.0", "--pd-Kp-n", "2",
        "--pd-Kd-range", "0.0", "0.2", "--pd-Kd-n", "2",
        "--max-overshoot", "80",
        "--objective", "itae",
        "--backend", "none",
        "--save-prefix", "test_run"
    ]
    code, out = run_cmd(args)
    assert code == 0
    assert "Best Candidate" in out or "No candidate" in out
