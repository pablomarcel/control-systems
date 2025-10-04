from __future__ import annotations
import sys, subprocess
from pathlib import Path

def run_cmd(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen(
        [sys.executable, "-m", "stateSpaceAnalysis.converterTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_tf_smoke():
    code, out = run_cmd(["--num","1,0","--den","1,14,56,160","--no-plot"])
    assert code == 0
    assert "TF → SS" in out

def test_cli_ss_smoke():
    code, out = run_cmd([
        "--A","0 1 0; 0 0 1; -5 -25 -5",
        "--B","0; 25; -120",
        "--C","1 0 0",
        "--D","0",
        "--no-plot"
    ])
    assert code == 0
    assert "SS → TF" in out
