import os
from pathlib import Path
import numpy as np

from modeling_control_systems.systemTool.app import SystemModelingApp
from modeling_control_systems.systemTool.apis import RunConfig, MSDConfig, TFfromSSConfig, ODENoDerivConfig, ODEWithDerivConfig, CommonSim

OUT = Path(__file__).resolve().parents[1] / "out"

def test_app_msd_step_saves(tmp_path):
    app = SystemModelingApp()
    cfg = RunConfig(mode="msd-step", msd=MSDConfig(tfinal=0.2, dt=0.02, save=True))
    res = app.run(cfg)
    assert res.ok
    assert any("msd_y.png" in p for p in (res.saved_images or []))

def test_app_tf_from_ss_default():
    app = SystemModelingApp()
    cfg = RunConfig(mode="tf-from-ss", tfss=TFfromSSConfig())
    res = app.run(cfg)
    assert res.ok
    assert "G[1,1]" in (res.pretty_tf or "")

def test_app_ode_no_deriv_defaults(tmp_path):
    app = SystemModelingApp()
    cfg = RunConfig(mode="ode-no-deriv", ode_nd=ODENoDerivConfig(tfinal=0.2, dt=0.02, save=True))
    res = app.run(cfg)
    assert res.ok
    assert "G(s)=" in (res.pretty_tf or "")
    assert any("ode_no_deriv_step.png" in p for p in (res.saved_images or []))

def test_app_ode_with_deriv_defaults(tmp_path):
    app = SystemModelingApp()
    cfg = RunConfig(mode="ode-with-deriv", ode_d=ODEWithDerivConfig(tfinal=0.2, dt=0.02, save=True))
    res = app.run(cfg)
    assert res.ok
    assert "beta=" in (res.pretty_tf or "")

def test_app_kv_vs_maxwell_overlay(tmp_path):
    app = SystemModelingApp()
    cfg = RunConfig(mode="kv-vs-maxwell", kvmax=CommonSim(tfinal=0.2, dt=0.02, save=True))
    res = app.run(cfg)
    assert res.ok
