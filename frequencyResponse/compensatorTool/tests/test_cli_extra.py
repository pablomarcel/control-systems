
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

def test_cli_plotly_multi_and_no_show(tmp_path):
    code, out = run_cmd([
        "--ogata_7_28",
        "--backend","plotly",
        "--plots","bode,nyquist,nichols",
        "--ogata_axes",
        "--nichols_templates",
        "--nyquist_M","1.2","1.05","0.9",
        "--nyquist_marks","0.2","0.4","1","2",
        "--save", str(tmp_path/"og728_{kind}.html"),
        "--no_show"
    ])
    assert code == 0

def test_cli_mpl_time_show_unstable(tmp_path):
    code, out = run_cmd([
        "--ogata_7_28",
        "--backend","mpl",
        "--plots","step,ramp",
        "--ogata_axes",
        "--show_unstable",
        "--save", str(tmp_path/"og728_{kind}.png"),
        "--no_show"
    ])
    assert code == 0
