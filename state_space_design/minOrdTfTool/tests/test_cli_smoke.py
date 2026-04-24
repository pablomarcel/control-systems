
import subprocess, sys, json, os, pathlib

PKG = "state_space_design.minOrdTfTool.cli"

def run_cli(args):
    cmd = [sys.executable, "-m", PKG] + args
    return subprocess.run(cmd, capture_output=True, text=True, check=True)

def test_cli_help_runs():
    out = subprocess.run([sys.executable, "-m", PKG, "--help"], capture_output=True, text=True)
    assert out.returncode == 0
    assert "Minimum-order observer-based controller" in out.stdout

def test_cli_basic_json(tmp_path):
    # Simple 2-state example
    A = "0 1; -2 -3"
    B = "0; 1"
    C = "1 0"
    poles = ["-5"]  # r = n-1 = 1
    K = "6 4"       # explicit K to avoid python-control dependency in tests

    json_path = tmp_path/"out.json"
    args = [
        "--A", A, "--B", B, "--C", C,
        "--poles", *poles,
        "--K", K,
        "--export_json", str(json_path),
    ]
    out = run_cli(args)
    assert json_path.exists(), out.stderr
    data = json.loads(json_path.read_text())
    assert "tf_num" in data and "tf_den" in data
    assert len(data["tf_den"]) >= 1
