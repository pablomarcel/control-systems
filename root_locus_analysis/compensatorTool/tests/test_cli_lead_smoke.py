# modernControl/root_locus_analysis/compensatorTool/tests/test_cli_lead_smoke.py
from __future__ import annotations
from pathlib import Path
import os, sys, subprocess
from typing import List, Tuple

THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[3]   # .../modernControl

def run_cli(args: List[str]) -> Tuple[int, str, List[str], dict]:
    env = os.environ.copy()
    # Ensure the *parent* of package root is on PYTHONPATH
    python_path = str(PROJECT_ROOT)
    if env.get("PYTHONPATH"):
        python_path += os.pathsep + env["PYTHONPATH"]
    env["PYTHONPATH"] = python_path
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("LC_ALL", "C.UTF-8")
    env.setdefault("LANG", "C.UTF-8")

    argv = [sys.executable, "-m", "root_locus_analysis.compensatorTool.cli", *args]
    p = subprocess.Popen(
        argv,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    out = p.communicate()[0]
    return p.returncode, out, argv, env

def _on_fail_dump(tag: str, code: int, out: str, argv: List[str], env: dict) -> str:
    return (
        f"\n--- DEBUG ({tag}) -----------------------------------------------------\n"
        f"Return code: {code}\n"
        f"Command: {' '.join(argv)}\n"
        f"CWD (intended): {PROJECT_ROOT}\n"
        f"PYTHONPATH used: {env.get('PYTHONPATH','')}\n"
        f"PYTHONIOENCODING: {env.get('PYTHONIOENCODING','')}\n"
        f"LANG/LC_ALL: {env.get('LANG','')} / {env.get('LC_ALL','')}\n"
        + "-"*72 + "\nCaptured output (stdout+stderr):\n"
        + out.rstrip("\n") + "\n" + "-"*72 + "\n"
    )

def test_cli_lead_help():
    code, out, argv, env = run_cli(["lead", "--help"])
    if code != 0:
        print(_on_fail_dump("lead--help", code, out, argv, env))
    assert code == 0
    assert "Lead-only compensator design" in out or "Lead-only" in out or "Lead Compensator Design" in out

def test_cli_lead_method1_basic():
    # Ogata Ex 6-6 spirit: G(s)=10/[s(s+1)], zeta=0.5, wn=3, method 1
    code, out, argv, env = run_cli([
        "lead",
        "--num", "10", "--den", "1,1,0",
        "--zeta", "0.5", "--wn", "3",
        "--method", "1",
    ])
    if code != 0:
        print(_on_fail_dump("lead-m1", code, out, argv, env))
    assert code == 0
    assert "Lead Compensator Design" in out
    assert "Method:                   Method 1" in out or "Method:   Method 1" in out
    assert "Kc from |L(s*)|=1" in out

def test_cli_lead_method2_cancel():
    # Same plant; cancel a pole at -1
    code, out, argv, env = run_cli([
        "lead",
        "--num", "10", "--den", "1,1,0",
        "--zeta", "0.5", "--wn", "3",
        "--method", "2",
        "--cancel-at", "-1",
    ])
    if code != 0:
        print(_on_fail_dump("lead-m2", code, out, argv, env))
    assert code == 0
    assert "Lead Compensator Design" in out
    assert "Method:                   Method 2" in out or "Method:   Method 2" in out
    assert "Kc from |L(s*)|=1" in out
