
from __future__ import annotations
from pathlib import Path
import subprocess
import sys

def run_cmd(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen(
        [sys.executable, "-m", "stateSpaceAnalysis.canonicalTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_compare_smoke():
    code, out = run_cmd([
        "compare",
        "--num", "2,3",
        "--den", "1,1,10",
        "--tfinal", "1.0",
        "--dt", "0.01",
        "--no_show",
        "--backend", "mpl",
    ])
    assert code == 0
    assert "TF equality (vs CCF):" in out
