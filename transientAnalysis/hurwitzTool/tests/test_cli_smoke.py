# transientAnalysis/hurwitzTool/tests/test_cli_smoke.py
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _find_repo_root() -> Path:
    """
    Walk up from this file to locate the project root by presence of
    'pyproject.toml' or 'pytest.ini'. Falls back to 3 levels up.
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists() or (parent / "pytest.ini").exists():
            return parent
    # Fallback: .../modernControl (tests are at .../modernControl/transientAnalysis/hurwitzTool/tests)
    return here.parents[3]


def run_cmd(args: list[str]) -> tuple[int, str]:
    repo_root = _find_repo_root()
    env = dict(os.environ)
    # Ensure the repo root is importable so `-m transientAnalysis.hurwitzTool.cli` resolves.
    env["PYTHONPATH"] = os.pathsep.join([str(repo_root), env.get("PYTHONPATH", "")]).rstrip(os.pathsep)

    p = subprocess.Popen(
        [sys.executable, "-m", "transientAnalysis.hurwitzTool.cli", *args],
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out


def test_cli_numeric_smoke():
    code, out = run_cmd(["--coeffs", "1, 5, 6, 7"])
    assert code == 0
    assert "Hurwitz stable?" in out


def test_cli_symbolic_smoke():
    code, out = run_cmd(["--coeffs", "1, 5, 6, K", "--symbols", "K", "--solve-for", "K", "--intervals-pretty"])
    assert code == 0
    assert "Variables:" in out
