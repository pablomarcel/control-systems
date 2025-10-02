import os, sys, subprocess, json, time, shutil
from pathlib import Path

PY = sys.executable

def _env():
    env = os.environ.copy()
    env.setdefault("PLOTTOOL_DEBUG", "1")
    env.setdefault("MPLBACKEND", "Agg")
    env.setdefault("PLOTLY_RENDERER", "none")
    return env

def test_csv_equals_and_statespace(tmp_path):
    base = tmp_path / "csv"
    cmd = [
        PY, "-m", "frequencyResponse.plotTool.cli",
        "--fnum", "K", "--fden", "s (s+1) (0.5*s+1)", "--K", "1",
        "--nichols", "--nichols-grid", "--plotly",
        # IMPORTANT: when passing argv list to subprocess, DO NOT include quotes;
        # zsh-style quoting is a shell feature. We pass literals here.
        "--nichols-Mdb-csv=-18,-12,-9,-6,-3,0,3,5,6,9,12,18",
        "--nichols-Ndeg-csv=-10,-20,-30,-45,-60,-90,-120",
        "--nichols-closedloop", "--nichols-range=-240,0,-16,32",
        "--save-html", str(base)
    ]
    p = subprocess.run(cmd, env=_env(), capture_output=True, text=True, timeout=90)
    print("[CSV] RC", p.returncode)
    print("[CSV] STDOUT\n", p.stdout)
    print("[CSV] STDERR\n", p.stderr)
    assert p.returncode == 0

    htmls = sorted(str(p) for p in Path(tmp_path).glob("**/*nichols*.html"))
    print("[CSV] HTMLs:", htmls)
    assert htmls, "Expected Nichols HTML from CSV args"

    # State-space Nyquist quick smoke
    base2 = tmp_path / "ss"
    cmd2 = [
        PY, "-m", "frequencyResponse.plotTool.cli",
        "--A", "-1,-1; 6.5,0",
        "--B", "1,1; 1,0",
        "--C", "1,0; 0,1",
        "--D", "0,0; 0,0",
        "--nyquist", "--nyq-markers", "--nyq-samples", "7",
        "--plotly", "--save-html", str(base2)
    ]
    p2 = subprocess.run(cmd2, env=_env(), capture_output=True, text=True, timeout=90)
    print("[SS] RC", p2.returncode)
    print("[SS] STDOUT\n", p2.stdout)
    print("[SS] STDERR\n", p2.stderr)
    assert p2.returncode == 0
    htmls2 = sorted(str(p) for p in Path(tmp_path).glob("**/*nyquist*.html"))
    print("[SS] HTMLs:", htmls2)
    assert htmls2, "Expected Nyquist HTML from state-space"
