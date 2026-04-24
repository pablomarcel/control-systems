from __future__ import annotations
import subprocess
import sys
from pathlib import Path


def _run(args: list[str]):
    mod = "frequency_response.compensatorTool.cli"
    p = subprocess.Popen(
        [sys.executable, "-m", mod] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out


def test_cli_lag_exports_and_saves_mpl(tmp_path: Path):
    base = tmp_path / "lag_mpl"
    csv_prefix = str(tmp_path / "lag_export")
    json_path = str(tmp_path / "lag.json")
    save_path = str(base.with_suffix("")) + "_{kind}.png"

    code, out = _run(
        [
            "--mode", "lag",
            "--num", "4", "--den", "1, 2, 0",
            "--lag_pm_target", "45", "--lag_pm_add", "8",
            "--backend", "mpl",
            "--plots", "bode,nyquist,nichols",
            "--nichols_templates",
            "--export_csv_prefix", csv_prefix,
            "--export_json", json_path,
            "--save", save_path,
            "--no_show",
        ]
    )
    assert code == 0
    assert "==== DESIGN SUMMARY ====" in out

    # CSVs
    assert (tmp_path / "lag_export_bode.csv").exists()
    assert (tmp_path / "lag_export_nichols.csv").exists()

    # JSON
    assert (tmp_path / "lag.json").exists()

    # Saved figures
    assert (tmp_path / "lag_mpl_bode.png").exists()
    assert (tmp_path / "lag_mpl_nyquist.png").exists()
    assert (tmp_path / "lag_mpl_nichols.png").exists()


def test_cli_lag_plotly_html_save(tmp_path: Path):
    save_html = str(tmp_path / "lag_plotly_{kind}.html")
    code, out = _run(
        [
            "--mode", "lag",
            "--num", "4", "--den", "1, 2, 0",
            "--lag_pm_target", "45",
            "--backend", "plotly",
            "--plots", "bode",
            "--save", save_html,
            "--no_show",
        ]
    )
    assert code == 0
    assert "==== DESIGN SUMMARY ====" in out
    # HTML written
    assert (tmp_path / "lag_plotly_bode.html").exists()
