from __future__ import annotations
from pathlib import Path
import sys
import subprocess

# Run the CLI as a module from the repo root

def run_cmd(args: list[str]) -> tuple[int, str]:
    # test file is at .../transient_analysis/responseTool/tests/test_cli_smoke.py
    repo_root = Path(__file__).resolve().parents[3]  # adjust depth if needed
    p = subprocess.Popen(
        [sys.executable, "-m", "transient_analysis.responseTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out


def test_cli_ramp_ss_smoke(tmp_path):
    code, out = run_cmd(["--root", str(tmp_path), "ramp-ss", "--A", "0 1; -1 -1", "--B", "0; 1", "--C", "1 0", "--D", "0", "--tfinal", "0.5", "--dt", "0.05"])
    assert code == 0


def test_cli_lsim_tf_smoke(tmp_path):
    code, out = run_cmd(["--root", str(tmp_path), "lsim-tf", "--num", "2 1", "--den", "1 1 1", "--input", "ramp", "--tfinal", "0.5", "--dt", "0.05"])
    assert code == 0