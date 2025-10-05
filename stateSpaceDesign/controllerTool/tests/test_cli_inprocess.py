# -*- coding: utf-8 -*-
import sys
from stateSpaceDesign.controllerTool import cli

def test_cli_main_inprocess_no_plots(capsys):
    argv = [
        "--num", "1",
        "--den", "1 0 1 0",
        "--K_poles=-1+1j,-1-1j,-8",
        "--obs_poles=-4,-4",
        "--cfg", "both",
        "--plots", "none",
    ]
    cli.main(argv)
    out = capsys.readouterr().out
    assert "Build Summary" in out
    assert "Gc num:" in out
