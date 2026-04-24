from __future__ import annotations
from pathlib import Path
import sys, subprocess

def run_cmd(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen(
        [sys.executable, "-m", "frequency_response.bodeTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_basic_bode_smoke():
    code, out = run_cmd(["--num","1","--den","1, 0.8, 1","--bode"])
    assert code == 0
    assert "Frequency-Response Summary" in out
    assert "Gain margin" in out
    assert "Phase margin" in out
