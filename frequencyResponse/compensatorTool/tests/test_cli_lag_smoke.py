from __future__ import annotations
import subprocess
import sys


def _run(args: list[str]):
    mod = "frequencyResponse.compensatorTool.cli"
    p = subprocess.Popen(
        [sys.executable, "-m", mod] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out = p.communicate()[0]
    return p.returncode, out


def test_cli_lag_help():
    code, out = _run(["--help"])
    assert code == 0
    # Must expose lag mode in help
    assert "--mode {laglead,lead,lag}" in out


def test_cli_lag_smoke_run_mpl_bode_only():
    code, out = _run(
        [
            "--mode", "lag",
            "--num", "4", "--den", "1, 2, 0",
            "--lag_pm_target", "45",
            "--backend", "mpl",
            "--plots", "bode",
            "--no_show",
        ]
    )
    assert code == 0
    assert "==== DESIGN SUMMARY ====" in out
