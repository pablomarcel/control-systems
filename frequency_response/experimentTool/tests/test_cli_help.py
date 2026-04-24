from __future__ import annotations
from pathlib import Path
import sys, subprocess

def run_cmd(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen(
        [sys.executable, "-m", "frequency_response.experimentTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_help():
    code, out = run_cmd(["--help"])
    assert code == 0
    assert "Experimental identification" in out

def test_subcommand_helps():
    for sub in ["run", "make-csv", "fit"]:
        code, out = run_cmd([sub, "--help"])
        assert code == 0
        assert "Options:" in out
