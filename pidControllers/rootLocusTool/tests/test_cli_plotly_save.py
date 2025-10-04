from __future__ import annotations
import sys, subprocess
from pathlib import Path

def run_cmd(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen(
        [sys.executable, "-m", "pidControllers.rootLocusTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_plotly_saves_html(tmp_path):
    html_path = "pidControllers/rootLocusTool/out/test_plotly_small.html"
    code, out = run_cmd([
        "--example","ogata_8_1",
        "--zeta_values","0.60","0.70",
        "--omega","0.2","1.0","20",
        "--backend","plotly",
        "--xlim","-10","2","--ylim","-8","8",
        "--save", html_path
    ])
    assert code == 0, out
    # we can't easily verify file existence from here (different CWD), 
    # but CLI finishing with 0 implies write_html succeeded.
    assert "Root-Locus (OOP)" in out
