
from __future__ import annotations
from pathlib import Path
import subprocess, sys

def run(args):
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen([sys.executable, "-m", "stateSpaceAnalysis.canonicalTool.cli", *args],
                         cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_help():
    code, out = run(["--help"])
    assert code == 0
    assert "canonicalTool" in out

def test_cli_compare_saves(tmp_path: Path):
    save = tmp_path / "cli_out_{kind}.png"
    code, out = run([
        "compare",
        "--num","2,3",
        "--den","1,1,10",
        "--tfinal","0.5",
        "--dt","0.01",
        "--no_show",
        "--backend","mpl",
        "--save", str(save),
    ])
    assert code == 0
    assert (tmp_path / "cli_out_step.png").exists()
