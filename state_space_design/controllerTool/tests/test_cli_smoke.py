# -*- coding: utf-8 -*-
import subprocess, sys

PKG = "state_space_design.controllerTool.cli"

def run_cli(args):
    cmd = [sys.executable, "-m", PKG] + args
    return subprocess.run(cmd, capture_output=True, text=True, check=True)

def test_cli_help_runs():
    out = run_cli(["--help"]).stdout
    assert "controllers with observers" in out.lower()

def test_cli_build_no_plots_cfg_both():
    args = [
        "--num", "1",
        "--den", "1 0 1 0",
        "--K_poles=-1+1j,-1-1j,-8",
        "--obs_poles=-4,-4",
        "--cfg", "both",
        "--plots", "none",
    ]
    out = run_cli(args).stdout
    assert "Gc num:" in out and "Gc den:" in out
