from pathlib import Path
import sys, subprocess

def run_cmd(args):
    repo_root = Path(__file__).resolve().parents[3]  # .../modernControl
    p = subprocess.Popen(
        [sys.executable, "-m", "state_space_analysis.stateRepTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_example_all():
    code, out = run_cmd(["--example", "ogata_9_1", "--canonical", "all"])
    assert code == 0
    assert "CONTROLLABLE" in out
    assert "OBSERVABLE" in out
    assert "DIAGONAL" in out
