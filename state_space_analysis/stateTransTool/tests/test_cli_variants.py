
from __future__ import annotations
from pathlib import Path
import subprocess, sys

def run_cmd(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen(
        [sys.executable, "-m", "state_space_analysis.stateTransTool.cli", *args],
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
    assert "state-transition matrix" in out.lower()

def test_cli_inverse_pretty():
    code, out = run_cmd(["--example","ogata_9_1","--inverse","--pretty"])
    assert code == 0
    assert "Φ" in out or "Phi" in out

def test_cli_missing_inputs_errors():
    code, out = run_cmd([])
    # argparse won't error; the app will error when inputs missing
    assert code != 0
    assert "Provide `tf` OR both `num` and `den`" in out
