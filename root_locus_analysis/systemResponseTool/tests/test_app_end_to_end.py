
from __future__ import annotations

import os
from pathlib import Path
import numpy as np

from root_locus_analysis.systemResponseTool.app import SystemResponseApp
from root_locus_analysis.systemResponseTool.core import ICMode

def test_app_runs_and_writes(tmp_path: Path, monkeypatch):
    # prevent fig.show()
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "1")

    app = SystemResponseApp(in_dir=tmp_path/"in", out_dir=tmp_path/"out", show_plots=False)
    specs = app.parse_systems([
        "tf; name=G; num=1; den=1,1; fb=none",
        "ss; name=P; A=[0,1; -1,-1]; B=[0;1]; C=[1,0; 0,1]; D=[0,0; 0,0]; x0=[1;0]; outs=all"
    ])
    T = np.linspace(0, 0.2, 5)

    # step
    fig1 = app.run_step(specs[:1], T, out_prefix=str(tmp_path/"out"/"a"))
    assert (tmp_path/"out/a_step.csv").exists()
    assert (tmp_path/"out/a_step.html").exists()

    # ramp
    fig2 = app.run_ramp(specs[:1], T, out_prefix=str(tmp_path/"out"/"b"))
    assert (tmp_path/"out/b_ramp.csv").exists()
    assert (tmp_path/"out/b_ramp.html").exists()

    # arb expr
    fig3 = app.run_arb(specs[:1], T, kind="expr", amp=1.0, freq=1.0, duty=0.5,
                       expr="sin(2*pi*t)", file_path="", show_input=False,
                       out_prefix=str(tmp_path/"out"/"c"))
    assert (tmp_path/"out/c_arb.csv").exists()
    assert (tmp_path/"out/c_arb.html").exists()

    # IC1 with compare
    fig4 = app.run_ic(specs[1:], T, which=ICMode.IC1, compare=True,
                      out_prefix=str(tmp_path/"out"/"d"))
    assert (tmp_path/"out/d_ic1_compare.csv").exists()
    assert (tmp_path/"out/d_ic1_compare.html").exists()

    # IC2 with compare
    fig5 = app.run_ic(specs[1:], T, which=ICMode.IC2, compare=True,
                      out_prefix=str(tmp_path/"out"/"e"))
    assert (tmp_path/"out/e_ic2_compare.csv").exists()
    assert (tmp_path/"out/e_ic2_compare.html").exists()
