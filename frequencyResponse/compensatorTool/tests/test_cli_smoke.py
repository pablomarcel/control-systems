
from __future__ import annotations
import sys, subprocess
from pathlib import Path

def run_cmd(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[3]
    modpath = "frequencyResponse.compensatorTool.cli"
    p = subprocess.Popen(
        [sys.executable, "-m", modpath, *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_help_runs():
    code, out = run_cmd(["--help"])
    assert code == 0
    assert "Lag-Lead compensator" in out

def test_cli_ogata_json_only(tmp_path):
    jsonp = tmp_path / "og728.json"
    code, out = run_cmd(["--ogata_7_28", "--backend", "mpl", "--plots", "bode", "--export_json", str(jsonp), "--no_show"])
    assert code == 0
    assert jsonp.exists()
