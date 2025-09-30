# transientAnalysis/responseTool/tests/test_cli_step_ss.py
from __future__ import annotations
from pathlib import Path
import sys, subprocess

def run_cmd(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen([sys.executable, "-m", "transientAnalysis.responseTool.cli", *args],
                         cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_step_ss_smoke(tmp_path):
    code, out = run_cmd([
        "--root", str(tmp_path),
        "step-ss",
        "--A", "-1 -1; 6.5 0",
        "--B", "1 1; 1 0",
        "--C", "1 0; 0 1",
        "--D", "0 0; 0 0",
        "--input-index", "0",
        "--tfinal", "0.5", "--dt", "0.05"
    ])
    assert code == 0
