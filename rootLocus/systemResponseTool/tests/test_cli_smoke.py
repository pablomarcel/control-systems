# rootLocus/systemResponseTool/tests/test_cli_smoke.py
from __future__ import annotations
import sys
from pathlib import Path
import subprocess

def run_cmd(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[3]  # .../modernControl
    tool_pkg = repo_root / "rootLocus" / "systemResponseTool"
    python = sys.executable
    cmd = [python, "-m", "rootLocus.systemResponseTool.cli", "run", *args]
    p = subprocess.Popen(cmd, cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_step_smoke():
    code, out = run_cmd([
        "--sys", "tf; name=G; num=10; den=1,1,10; fb=none",
        "--responses", "step",
        "--tfinal", "1.0",
        "--dt", "0.05",
        "--out-prefix", "systemResponseTool/out/smoke_step"
    ])
    assert code == 0
    assert "STEP response" in out or "INFO" in out

def test_cli_ic1_smoke():
    code, out = run_cmd([
        "--sys", "ss; name=P; A=[0,1; -1,-1]; B=[0;1]; C=[1,0]; D=[0]; x0=[1; 0]",
        "--responses", "ic1",
        "--tfinal", "0.5",
        "--dt", "0.05",
        "--out-prefix", "systemResponseTool/out/smoke_ic1"
    ])
    assert code == 0
