# rootLocus/systemResponseTool/tests/test_cli_legacy_log.py
from __future__ import annotations

import os
import sys
import json
import subprocess
from pathlib import Path


def _print_header(title: str):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def run_cmd(args):
    # Start from this test file and walk up until we find the project root
    # (i.e., a directory that contains the 'rootLocus' package folder).
    here = Path(__file__).resolve()
    cur = here.parent
    project_root = None
    for _ in range(10):  # guard to avoid infinite loops
        if (cur / "rootLocus").is_dir():
            project_root = cur
            break
        cur = cur.parent
    if project_root is None:
        # Fallback to the previous heuristic (modernControl)
        project_root = here.parents[3]  # .../modernControl

    python = sys.executable
    cmd = [python, "-m", "rootLocus.systemResponseTool.cli", "run", *args]

    env = os.environ.copy()
    env["PYTEST_CURRENT_TEST"] = "1"
    env["SRT_TEST_NOISE"] = "1"
    # Extra safety: ensure the package is importable even if cwd somehow shifts
    env["PYTHONPATH"] = os.pathsep.join(
        [str(project_root)] + ([env["PYTHONPATH"]] if "PYTHONPATH" in env else [])
    )

    _print_header("LEGACY-LOG TEST: SUBPROCESS DEBUG")
    print(f"project_root: {project_root}")
    print(f"python      : {python}")
    print(f"cwd         : {project_root}")
    print(f"cmd         : {' '.join(cmd)}")
    print("env delta   : " + json.dumps(
        {
            "PYTEST_CURRENT_TEST": env.get("PYTEST_CURRENT_TEST"),
            "SRT_TEST_NOISE": env.get("SRT_TEST_NOISE"),
            "PYTHONPATH_has_root": str(str(project_root) in env["PYTHONPATH"]),
        },
        indent=2,
    ))

    p = subprocess.Popen(
        cmd,
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]

    _print_header("SUBPROCESS COMBINED STDOUT+STDERR")
    print(out)
    _print_header(f"PROCESS RETURN CODE = {p.returncode}")

    return p.returncode, out



def test_cli_accepts_legacy_log_flag():
    code, out = run_cmd([
        "--sys", "tf; name=G; num=1; den=1,1; fb=none",
        "--responses", "step",
        "--tfinal", "0.2",
        "--dt", "0.05",
        "--out-prefix", "rootLocus/systemResponseTool/out/cli_legacy",
        "--log", "DEBUG",  # legacy flag that should be accepted
    ])

    # Make the failure message maximally helpful
    if code != 0:
        _print_header("ASSERTION FAILED — DUMP LAST 80 LINES")
        lines = out.splitlines()[-80:]
        print("\n".join(lines))

    assert code == 0
