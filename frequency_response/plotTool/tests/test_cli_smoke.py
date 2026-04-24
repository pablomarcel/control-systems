
from __future__ import annotations
from pathlib import Path
import sys, subprocess, os, platform

def run_cmd(args: list[str]) -> tuple[int, str]:
    here = Path(__file__).resolve()
    repo_root = None
    for p in [here] + list(here.parents):
        if (p / "frequency_response" / "plotTool" / "cli.py").exists():
            repo_root = p
            break
    assert repo_root, "Could not locate repo root containing frequency_response/plotTool/cli.py"
    cli_mod = repo_root / "frequency_response" / "plotTool" / "cli.py"
    assert cli_mod.exists(), f"cli not found at {cli_mod}"
    python = sys.executable
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("PLOTTOOL_DEBUG", "1")
    env.setdefault("MPLBACKEND", "Agg")
    env.setdefault("PLOTLY_RENDERER", "none")
    cmd = [python, "-m", "frequency_response.plotTool.cli", *args]
    p = subprocess.Popen(cmd, cwd=repo_root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.communicate()[0]
    header = f"\n==== CMD ===\n{' '.join(cmd)}\nCWD={repo_root}\nPython={sys.version}\nPlatform={platform.platform()}\n==== OUTPUT ===\n"
    return p.returncode, header + out

def test_cli_smoke_plotly_html(tmp_path):
    outdir = tmp_path / "out"; outdir.mkdir(exist_ok=True)
    code, out = run_cmd([
        "--fnum", "K", "--fden", "s (s+1) (0.5*s+1)", "--K", "1",
        "--nichols", "--nichols-grid", "--nichols-closedloop", "--plotly",
        "--nichols-range=-240,0,-16,32",
        "--save-html", str(outdir / "nichols_quick")
    ])
    if code != 0: print(out)
    assert code == 0, out
    htmls = list(outdir.glob("*_nichols.html"))
    assert htmls, "No HTML produced. Output was:\n" + out

def test_cli_smoke_mpl_png(tmp_path):
    outdir = tmp_path / "figs"; outdir.mkdir(exist_ok=True)
    code, out = run_cmd([
        "--fnum", "K", "--fden", "s (s+1) (0.5*s+1)", "--K", "1",
        "--bode",
        "--save-png", str(outdir)
    ])
    if code != 0: print(out)
    assert code == 0, out
    pngs = list(outdir.glob("bode*.png"))
    assert pngs, "No PNG produced. Output was:\n" + out
