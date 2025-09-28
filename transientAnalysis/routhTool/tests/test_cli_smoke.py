# transientAnalysis/routhTool/tests/test_cli_smoke.py
from __future__ import annotations
from pathlib import Path
import sys
import subprocess

def run_cli(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[3]  # .../modernControl
    pkg_dir = repo_root / "transientAnalysis" / "routhTool"
    cmd = [sys.executable, "-m", "transientAnalysis.routhTool.cli", *args]
    p = subprocess.Popen(
        cmd, cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_numeric_smoke():
    code, out = run_cli(["--coeffs", "1, 5, 6, 2"])
    assert code == 0
    assert "Routh array:" in out
    assert "#RHP roots by Routh" in out

def test_cli_symbolic_smoke():
    code, out = run_cli(["--coeffs", "1, 5, 6, K", "--symbol", "K", "--solve-for", "K"])
    assert code == 0
    assert "Stability region" in out