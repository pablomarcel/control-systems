from __future__ import annotations
from pathlib import Path
import sys, subprocess, json

def run_cmd(args: list[str]) -> tuple[int, str]:
    # Assume repo root is two levels up from this test file: .../modernControl
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen(
        [sys.executable, "-m", "state_space_analysis.stateTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_obs_smoke():
    code, out = run_cmd(["--A","0 1; -2 -3","--B","0;1","--C","3 1","--mode","obs"])
    assert code == 0
    data = json.loads(out)
    assert data["results"]["obs"]["n"] == 2

def test_cli_tf_splane_smoke():
    code, out = run_cmd(["--tf","(s+3)/(s^2+3*s+2)","--mode","obssplane"])
    assert code == 0
    data = json.loads(out)
    assert "no_cancellation" in data["results"]["obssplane"]
