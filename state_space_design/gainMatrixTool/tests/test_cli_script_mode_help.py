import subprocess, sys, pathlib

def pkg_dir():
    return pathlib.Path(__file__).resolve().parents[1]

def test_cli_script_mode_help():
    cp = subprocess.run([sys.executable, "cli.py", "--help"], cwd=pkg_dir(), capture_output=True, text=True)
    assert cp.returncode == 0
    assert "Gain-matrix design" in cp.stdout
