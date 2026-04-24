# root_locus_analysis/compensatorTool/tests/test_cli_lag_smoke.py
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
from typing import Tuple, List

# This file lives at modernControl/root_locus_analysis/compensatorTool/tests
THIS_FILE = Path(__file__).resolve()
ROOTLOCUS_DIR = THIS_FILE.parents[2]   # .../modernControl/root_locus_analysis
PROJECT_ROOT = THIS_FILE.parents[3]    # .../modernControl

def run_cli(args: List[str]) -> Tuple[int, str, List[str], dict]:
    """
    Run the CLI in a subprocess with a controlled PYTHONPATH and encoding.
    Returns (returncode, stdout+stderr, argv, env_used).
    """
    env = os.environ.copy()

    # IMPORTANT: Add the parent of the package (modernControl) to PYTHONPATH
    # so 'root_locus_analysis' is importable as a package.
    python_path = str(PROJECT_ROOT)
    if "PYTHONPATH" in env and env["PYTHONPATH"]:
        python_path += os.pathsep + env["PYTHONPATH"]
    env["PYTHONPATH"] = python_path

    # Force UTF-8 to avoid any stdout encoding issues with en dashes in help text.
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("LC_ALL", "C.UTF-8")
    env.setdefault("LANG", "C.UTF-8")

    argv = [sys.executable, "-m", "root_locus_analysis.compensatorTool.cli", *args]
    p = subprocess.Popen(
        argv,
        cwd=PROJECT_ROOT,   # run from project root (…/modernControl)
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    out = p.communicate()[0]
    return p.returncode, out, argv, env


def _on_fail_dump(tag: str, code: int, out: str, argv: List[str], env: dict) -> str:
    return (
        f"--- DEBUG ({tag}) -----------------------------------------------------\n"
        f"Return code: {code}\n"
        f"Command: {' '.join(argv)}\n"
        f"CWD (intended): {PROJECT_ROOT}\n"
        f"PYTHONPATH used: {env.get('PYTHONPATH','')}\n"
        f"PYTHONIOENCODING: {env.get('PYTHONIOENCODING','')}\n"
        f"LANG/LC_ALL: {env.get('LANG','')} / {env.get('LC_ALL','')}\n"
        f"{'-'*72}\n"
        f"Captured output (stdout+stderr):\n{out.rstrip()}\n"
        f"{'-'*72}\n"
    )


def test_cli_lag_help():
    code, out, argv, env = run_cli(["lag", "--help"])
    if code != 0:
        print(_on_fail_dump("lag--help", code, out, argv, env))
    assert code == 0, _on_fail_dump("lag--help", code, out, argv, env)
    # A couple of flexible needles so small wording tweaks won’t break the test.
    assert ("Lag-only compensator design" in out) or ("Lag-only" in out) or ("Lag" in out), \
        _on_fail_dump("lag--help-missing-text", code, out, argv, env)


def test_cli_lag_basic_target():
    # Example in the spirit of the standalone script: size β from target Kv.
    code, out, argv, env = run_cli([
        "lag",
        "--num", "1.06", "--den", "1,3,2,0",
        "--zeta", "0.491", "--wn", "0.673",
        "--err", "kv", "--target", "5.12",
    ])
    if code != 0:
        print(_on_fail_dump("lag basic", code, out, argv, env))
    assert code == 0, _on_fail_dump("lag basic", code, out, argv, env)

    # Check some banner/lines the lag app prints.
    assert ("Lag Compensator Design" in out) or ("Lag" in out), \
        _on_fail_dump("lag-missing-banner", code, out, argv, env)
    assert "Kc from |L(s*)|=1" in out or "Kc from |L(s*)| = 1" in out, \
        _on_fail_dump("lag-missing-kc-line", code, out, argv, env)
