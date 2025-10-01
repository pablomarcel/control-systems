# rootLocus/systemResponseTool/tests/test_cli_smoke.py
from __future__ import annotations

import os
import sys
from pathlib import Path
import subprocess
from typing import List, Tuple


def run_cmd(args: List[str]) -> Tuple[int, str]:
    """
    Run the CLI in a subprocess with a controlled environment, capturing stdout+stderr.
    We set PYTEST_CURRENT_TEST so the CLI disables plot popups.
    """
    repo_root = Path(__file__).resolve().parents[3]  # .../modernControl
    python = sys.executable
    cmd = [python, "-m", "rootLocus.systemResponseTool.cli", "run", *args]

    env = os.environ.copy()
    env["PYTEST_CURRENT_TEST"] = env.get("PYTEST_CURRENT_TEST", "1")

    p = subprocess.Popen(
        cmd,
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out


def _paths_for_prefix(prefix: str, stems: list[str]) -> list[Path]:
    """
    Build absolute Paths for expected outputs based on a repo-root
    relative prefix string and a set of filename stems.
    """
    repo_root = Path(__file__).resolve().parents[3]
    out: list[Path] = []
    for stem in stems:
        out.append(repo_root / f"{prefix}_{stem}.csv")
        out.append(repo_root / f"{prefix}_{stem}.html")
    return out


def _assert_files_exist(paths: list[Path], fail_context: str):
    """
    Assert that all paths exist; include a concise failure message.
    """
    missing = [str(p) for p in paths if not p.exists()]
    assert not missing, f"Missing expected output files: {missing}\n{fail_context}"


def test_cli_step_smoke():
    # Write under repo-root/systemResponseTool/out/...
    out_prefix = "systemResponseTool/out/smoke_step"

    code, out = run_cmd([
        "--sys", "tf; name=G; num=10; den=1,1,10; fb=none",
        "--responses", "step",
        "--tfinal", "1.0",
        "--dt", "0.05",
        "--out-prefix", out_prefix,
        "--log", "WARNING",  # keep subprocess chatter low
    ])

    assert code == 0, f"CLI exited with {code}\nSubprocess output:\n{out}"

    expected = _paths_for_prefix(out_prefix, stems=["step"])
    _assert_files_exist(expected, fail_context=f"Subprocess output:\n{out}")


def test_cli_ic1_smoke():
    out_prefix = "systemResponseTool/out/smoke_ic1"

    code, out = run_cmd([
        "--sys", "ss; name=P; A=[0,1; -1,-1]; B=[0;1]; C=[1,0]; D=[0]; x0=[1; 0]",
        "--responses", "ic1",
        "--tfinal", "0.5",
        "--dt", "0.05",
        "--out-prefix", out_prefix,
        "--log", "WARNING",
    ])

    assert code == 0, f"CLI exited with {code}\nSubprocess output:\n{out}"

    # Default is ic_compare=True → we expect the "_ic1_compare" files
    expected = _paths_for_prefix(out_prefix, stems=["ic1_compare"])
    _assert_files_exist(expected, fail_context=f"Subprocess output:\n{out}")
