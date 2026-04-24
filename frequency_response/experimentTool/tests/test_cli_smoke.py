from __future__ import annotations
from pathlib import Path
import sys, subprocess

def run_cmd(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[3]  # .../modernControl
    p = subprocess.Popen(
        [sys.executable, "-m", "frequency_response.experimentTool.cli", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_run_ogata_smoke():
    code, out = run_cmd(["run", "--ogata", "--backend", "mpl", "--npts", "64", "--save-prefix", "smoke"])
    assert code == 0
    assert "Outputs ->" in out

def test_make_csv_and_fit_smoke(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    csv_path = repo_root / "frequency_response" / "experimentTool" / "in" / "smoke.csv"
    # make-csv
    code, out = run_cmd(["make-csv", "--ogata", "--npts", "64", "--csv-out", str(csv_path)])
    assert code == 0
    assert csv_path.exists()
    # fit
    code, out = run_cmd(["fit", "--csv", str(csv_path), "--backend", "mpl", "--npts", "64", "--save-prefix", "fit_smoke"])
    assert code == 0
