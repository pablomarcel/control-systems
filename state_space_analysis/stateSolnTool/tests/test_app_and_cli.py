
import sys, subprocess
from pathlib import Path
from state_space_analysis.stateSolnTool.app import StateSolnApp

def test_app_facade_runs():
    app = StateSolnApp(canonical="controllable")
    app.configure_logging("INFO")
    out = app.run(example="ogata_9_1", u="1", pretty=False, verify=True)
    assert out["x"]

def run_cli(args):
    repo_root = Path(__file__).resolve().parents[3]  # up to /mnt/data
    p = subprocess.Popen(
        [sys.executable, "-m", "state_space_analysis.stateSolnTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_numeric_eval():
    code, out = run_cli(["--example","ogata_9_1","--eval","1","--numeric","--verify"])
    assert code == 0
    assert "Verification" in out

def test_cli_error_missing_args():
    code, out = run_cli(["--num","1,2,3"])  # missing --den
    assert code != 0 or "Provide --tf OR both --num and --den." in out
