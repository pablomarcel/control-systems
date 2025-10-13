
from __future__ import annotations
import numpy as np
from modelingSystems.mimoTool.apis import RunConfig, RunResult, PlantSummary

def test_runconfig_wgrid_range():
    cfg = RunConfig(plants=["two_tank"], wmin=1e-2, wmax=1e1, npts=5, plot_steps=False, plot_sigma=False, show=False)
    w = cfg.wgrid()
    assert isinstance(w, np.ndarray) and w.size == 5
    assert np.isclose(w[0], 1e-2) and np.isclose(w[-1], 1e1)

def test_runresult_jsonable():
    rr = RunResult(summaries=[PlantSummary(name="two_tank", poles=[0+1j, -2+0j])])
    js = rr.to_jsonable()
    assert "summaries" in js and js["summaries"][0]["name"] == "two_tank"
