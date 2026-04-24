import sys, subprocess
from pathlib import Path

def _run_cmd(args, cwd):
    p = subprocess.Popen([sys.executable, "-m", "state_space_analysis.stateRepTool.cli", *args],
                         cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_numeric_export(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    out_name = "cli_all_numeric.json"
    code, out = _run_cmd(["--example","ogata_9_1","--canonical","all","--numeric","--digits","8",
                          "--no-verify","--export-json", out_name], cwd=repo_root)
    assert code == 0
    pkg_out = repo_root / "state_space_analysis" / "stateRepTool" / "out" / out_name
    assert pkg_out.exists()
    assert "CONTROLLABLE" in out and "DIAGONAL" in out
