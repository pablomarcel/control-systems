
from __future__ import annotations
import sys, subprocess
from pathlib import Path
import types
import numpy as np
import control as ct
import pytest

def run_cli(args: list[str]) -> tuple[int, str]:
    repo_root = Path(__file__).resolve().parents[3]
    p = subprocess.Popen(
        [sys.executable, "-m", "pid_controllers.zeroPoleTool.cli", *args],
        cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_help_runs():
    code, out = run_cli(["--help"])
    assert code == 0
    assert "Two-DOF zero-placement" in out or "usage" in out

def _build_candidate():
    # Minimal candidate by running a small search
    from pid_controllers.zeroPoleTool.design import Designer
    Gp = ct.tf([1], [1,2,1])
    des = Designer("fig8-31")
    best, ok, *_ = des.search(Gp, [2.0], [2.0], [1.0], 0, 100, 10, 0.02, show_progress=False)
    cand = best if best else ok[0]
    return cand

def test_viz_early_return_no_plotly(monkeypatch):
    # Ensure code path when Plotly is unavailable
    import pid_controllers.zeroPoleTool.viz as viz
    monkeypatch.setattr(viz, "PLOTLY_OK", False, raising=False)
    cand = _build_candidate()
    # should just warn and return without error
    viz.step_reference("tmp_pref", cand)
    viz.step_disturbance("tmp_pref", cand)
    viz.ramp_reference("tmp_pref", cand)
    viz.accel_reference("tmp_pref", cand)

def test_cli_full_run(monkeypatch):
    # Run the CLI with a tiny grid (no plots) to exercise cli.py path
    code, out = run_cli([
        "--plant-form","coeff","--num","1","--den","1,2,1",
        "--a-vals","2.0","--b-vals","2.0","--c-vals","1.0",
        "--os-min","0","--os-max","100","--ts-max","10",
        "--no-progress"
    ])
    assert code == 0
    assert "Best candidate" in out or "No candidate" in out
