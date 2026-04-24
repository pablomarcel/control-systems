
# tests/test_app_api.py
import os
import matplotlib
matplotlib.use("Agg", force=True)
from control_systems.canonicalTool.app import CanonicalApp
from control_systems.canonicalTool.apis import RunRequest

def test_cli_like_run_tf_only_no_plot(tmp_path):
    app = CanonicalApp()
    req = RunRequest(num=[2,3], den=[1,1,10], tfinal=2.0, dt=1e-2, symbolic=False, plots=False, no_show=True)
    res = app.run(req)
    assert res.equal_ocf is True
    assert res.equal_modal is True
