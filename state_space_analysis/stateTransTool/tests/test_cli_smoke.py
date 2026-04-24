# state_space_analysis/stateTransTool/tests/test_cli_smoke.py
from __future__ import annotations
from pathlib import Path
import sys
import subprocess

def run_cmd(args: list[str]) -> tuple[int, str]:
    # project root is .../modernControl
    repo_root = Path(__file__).resolve().parents[3]  # tests → stateTransTool → state_space_analysis → modernControl
    p = subprocess.Popen(
        [sys.executable, "-m", "state_space_analysis.stateTransTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_example_pretty():
    code, out = run_cmd(["--example", "ogata_9_1", "--pretty"])
    assert code == 0
    assert "State-Transition Matrix" in out

def test_cli_eval_numeric_and_json(tmp_path):
    out_json = tmp_path / "phi.json"
    code, out = run_cmd(["--example", "ogata_9_1", "--eval", "1", "--numeric", "--export-json", str(out_json)])
    assert code == 0
    assert out_json.exists()
