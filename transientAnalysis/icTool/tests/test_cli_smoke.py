# ---------------------------------
# File: transientAnalysis/icTool/tests/test_cli_smoke.py
# ---------------------------------
from __future__ import annotations
from pathlib import Path
import sys
import subprocess


def run_cmd(args: list[str]) -> tuple[int, str]:
    # repo_root is two parents above icTool/tests when installed in project
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen(
        [sys.executable, "-m", "transientAnalysis.icTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out


def test_cli_compare1_smoke():
    code, out = run_cmd(["compare1", "--A", "0 1; -6 -5", "--x0", "2; 1", "--tfinal", "0.5", "--dt", "0.05"])
    assert code == 0
    assert "Compare1 OK" in out


def test_cli_compare2_smoke():
    code, out = run_cmd(["compare2", "--A", "0 1 0; 0 0 1; -10 -17 -8", "--C", "1 0 0", "--x0", "2; 1; 0.5", "--tfinal", "0.5", "--dt", "0.05"])
    assert code == 0
    assert "Compare2 OK" in out