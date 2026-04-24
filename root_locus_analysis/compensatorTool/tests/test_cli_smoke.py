# modernControl/root_locus_analysis/compensatorTool/tests/test_cli_smoke.py
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
from typing import Tuple, List

# Tests live at modernControl/root_locus_analysis/compensatorTool/tests
# We want PROJECT_ROOT = modernControl (one level above 'root_locus_analysis')
THIS_FILE = Path(__file__).resolve()
ROOTLocus_DIR = THIS_FILE.parents[2]         # .../modernControl/root_locus_analysis
PROJECT_ROOT = THIS_FILE.parents[3]          # .../modernControl


def run_cli(args: List[str]) -> Tuple[int, str, List[str], dict]:
    """
    Run the CLI in a subprocess with a controlled PYTHONPATH and encoding.
    Returns (returncode, stdout+stderr, argv, env_used).
    """
    env = os.environ.copy()

    # Ensure the *parent* directory of the package (modernControl) is on PYTHONPATH.
    # Putting root_locus_analysis itself on the path prevents importing 'root_locus_analysis' as a package.
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
        cwd=PROJECT_ROOT,                 # run from repo root
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    out = p.communicate()[0]
    return p.returncode, out, argv, env


def _on_fail_dump(context: str, code: int, out: str, argv: List[str], env: dict) -> str:
    """Create a verbose failure message."""
    lines = [
        "",
        f"--- DEBUG ({context}) -----------------------------------------------------",
        f"Return code: {code}",
        f"Command: {' '.join(argv)}",
        f"CWD (intended): {PROJECT_ROOT}",
        f"PYTHONPATH used: {env.get('PYTHONPATH', '')}",
        f"PYTHONIOENCODING: {env.get('PYTHONIOENCODING', '')}",
        f"LANG/LC_ALL: {env.get('LANG', '')} / {env.get('LC_ALL', '')}",
        "-" * 72,
        "Captured output (stdout+stderr):",
        out.rstrip("\n"),
        "-" * 72,
        "",
    ]
    return "\n".join(lines)


def test_cli_help_smoke():
    """Smoke: `python -m root_locus_analysis.compensatorTool.cli --help` returns 0 and shows banner."""
    code, out, argv, env = run_cli(["--help"])
    if code != 0:
        print(_on_fail_dump("help", code, out, argv, env))
    assert code == 0, _on_fail_dump("help", code, out, argv, env)

    needle = "Lag–Lead designer"
    if needle not in out:
        print(_on_fail_dump("help-missing-text", code, out, argv, env))
    assert needle in out, _on_fail_dump("help-missing-text", code, out, argv, env)


def test_cli_indep_cancel_kv_target():
    """End-to-end: valid 'design' invocation returns 0 and prints expected banner/metrics."""
    code, out, argv, env = run_cli([
        "design",
        "--num", "4", "--den", "0.5,1,0",
        "--zeta", "0.5", "--wn", "5",
        "--case", "indep",
        "--lead-method", "cancel", "--cancel-at", "-0.5",
        "--err", "kv", "--target", "80",
    ])
    if code != 0:
        print(_on_fail_dump("design", code, out, argv, env))
    assert code == 0, _on_fail_dump("design", code, out, argv, env)

    banner = "Lag–Lead Compensator Design"
    if banner not in out:
        print(_on_fail_dump("design-missing-banner", code, out, argv, env))
    assert banner in out, _on_fail_dump("design-missing-banner", code, out, argv, env)

    # Either the compact constants line or the explicit BEFORE block must appear.
    has_constants = ("Kv=" in out) or ("BEFORE (plant):" in out)
    if not has_constants:
        print(_on_fail_dump("design-missing-constants", code, out, argv, env))
    assert has_constants, _on_fail_dump("design-missing-constants", code, out, argv, env)
