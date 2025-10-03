
from __future__ import annotations
import sys, subprocess
from pathlib import Path

def run_cmd(args: list[str]) -> tuple[int, str]:
    # test file: .../modernControl/pidControllers/zeroPoleTool/tests/test_cli_smoke.py
    # repo root is three levels up from this file (parents[3] -> modernControl)
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen(
        [sys.executable, "-m", "pidControllers.zeroPoleTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_coeff_small_grid():
    code, out = run_cmd([
        "--plant-form","coeff","--num","1","--den","1,2,1",
        "--a-vals","2.0 2.5","--b-vals","2.0","--c-vals","1.0",
        "--os-min","0","--os-max","100","--ts-max","10",
        "--no-progress"
    ])
    assert code == 0, f"CLI failed with code={code}. Output:\n{out}"
    assert "Best candidate" in out or "No candidate" in out
