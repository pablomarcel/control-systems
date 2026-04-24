
from __future__ import annotations
import subprocess, sys, json
from pathlib import Path

def run_cli(args):
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen([sys.executable, "-m", "state_space_analysis.stateTool.cli", *args],
                         cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.communicate()[0]
    return p.returncode, out

def _extract_json(s: str) -> dict:
    # find first '{' and last '}' to strip logging noise
    i = s.find('{')
    j = s.rfind('}')
    if i == -1 or j == -1 or j < i:
        raise ValueError("No JSON object found in output:\n" + s)
    return json.loads(s[i:j+1])

def test_cli_help_runs():
    code, out = run_cli(["--help"])
    assert code == 0
    assert "State-Space Analysis" in out

def test_cli_state_and_json():
    code, out = run_cli(["--A","0 1; -2 -3","--B","0;1","--C","3 1","--D","0",
                         "--mode","all","--export-json","cli_out.json","--numeric","--digits","5","--log","INFO"])
    assert code == 0
    data = _extract_json(out)
    assert "state" in data["results"]
    p = Path("state_space_analysis/stateTool/out/cli_out.json")
    assert p.exists()

def test_cli_tf_path():
    code, out = run_cli(["--tf","(s+2.5)/((s+2.5)*(s-1))","--mode","obssplane","--log","DEBUG"])
    assert code == 0
    data = _extract_json(out)
    assert "obssplane" in data["results"]
