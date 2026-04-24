import os, json
from pathlib import Path
import numpy as np

os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH","") + (":" if os.environ.get("PYTHONPATH") else "") + "/mnt/data"
from state_space_design.observerGainMatrixTool.apis import ObserverRequest
from state_space_design.observerGainMatrixTool.app import ObserverGainMatrixApp
from state_space_design.observerGainMatrixTool.io import OutputManager

def test_app_basic_and_closed_loop(tmp_path):
    app = ObserverGainMatrixApp(out=OutputManager(out_dir=tmp_path))
    req = ObserverRequest(
        A="0 1; -2 -3", B="0;1", C="1 0", poles=[-5, -6],
        method="auto", compute_closed_loop=True, x0="1,0", e0="0,0", t_final=0.05, dt=0.01,
        pretty=True, latex_out="eq.tex", K_poles_csv="-3,-4"
    )
    resp = app.run(req)
    assert "Ke" in resp.data and resp.data["observer_controller_tf"] is not None
    # latex file created
    tex_path = resp.data.get("latex_path")
    assert tex_path and Path(tex_path).exists()
