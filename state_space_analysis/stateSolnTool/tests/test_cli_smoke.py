
# tests/test_cli_smoke.py
from __future__ import annotations
from pathlib import Path
import sys
import subprocess

def run_cmd(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[2]  # .../state_space_analysis
    # Adjust to project root by going one more up if package sits inside larger repo
    repo_root = repo_root.parent  # go to .../ (modernControl)
    p = subprocess.Popen(
        [sys.executable, "-m", "state_space_analysis.stateSolnTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_example_symbolic_pretty():
    code, out = run_cmd(["--example","ogata_9_1","--pretty","--verify"])
    assert code == 0
    assert "Solution for" in out
    assert "Verification" in out
