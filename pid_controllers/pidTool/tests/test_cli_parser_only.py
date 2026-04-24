
import subprocess, sys, pathlib

def test_cli_parser_run_help():
    repo_root = pathlib.Path(__file__).resolve().parents[3]
    proc = subprocess.run([sys.executable, "-m", "pid_controllers.pidTool.cli", "run", "--help"],
                          cwd=repo_root, capture_output=True, text=True)
    assert proc.returncode == 0
    # Be robust to phrasing differences; look for 'usage' header and a few known flags
    out = proc.stdout
    assert "usage:" in out and "cli.py run" in out
    assert "--plant-form" in out and "--structure" in out and "--objective" in out
