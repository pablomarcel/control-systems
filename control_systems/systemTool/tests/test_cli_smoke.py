import subprocess, sys, pathlib

PKG_DIR = pathlib.Path(__file__).resolve().parents[1]

def run_cli(*args):
    cmd = [sys.executable, str(PKG_DIR/'cli.py'), *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=True)

def test_help():
    r = run_cli("--help")
    assert "System modeling toolkit" in r.stdout

def test_msd_no_save():
    r = run_cli("msd-step", "--no-save")
    assert "ok - msd-step done" in r.stdout
