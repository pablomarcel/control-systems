
import subprocess, sys

PKG = "stateSpaceDesign.minOrdTfTool.cli"

def run_cmd(args, check=True):
    return subprocess.run([sys.executable, "-m", PKG] + args, capture_output=True, text=True, check=check)

def test_cli_pretty_and_debug(tmp_path):
    args = [
        "--A","0 1; -2 -3",
        "--B","0; 1",
        "--C","1 0",
        "--poles","-5",
        "--K","6 4",
        "--pretty",
        "--export_json", str(tmp_path/"dbg.json"),
        "--log","DEBUG"
    ]
    res = run_cmd(args, check=True)
    assert "Controller TF" in res.stdout
    assert "Saved JSON" in res.stdout
